#!/usr/bin/env python3
"""Print cumulative token usage for the current Codex task."""

from __future__ import annotations

import argparse
import json
import os
import re
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator


THREAD_ID_PATTERN = re.compile(
    r"([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12})\.jsonl$"
)


class UsageUnavailable(Exception):
    """Raised when a reliable token total cannot be produced."""


@dataclass(frozen=True)
class TokenUsage:
    input_tokens: int
    output_tokens: int
    total_tokens: int


@dataclass(frozen=True)
class TranscriptSnapshot:
    thread_id: str
    session_id: str
    usage: TokenUsage | None
    child_thread_ids: frozenset[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print cumulative token usage for the current Codex task."
    )
    parser.add_argument(
        "--transcript",
        type=Path,
        help="Use this Codex rollout JSONL instead of CODEX_THREAD_ID discovery.",
    )
    return parser.parse_args()


def codex_home() -> Path:
    configured = os.environ.get("CODEX_HOME")
    return Path(configured).expanduser() if configured else Path.home() / ".codex"


def jsonl_records(path: Path) -> Iterator[dict[str, Any]]:
    """Read JSONL while tolerating only an unfinished final line."""
    try:
        stream = path.open("rb")
    except OSError as error:
        raise UsageUnavailable from error

    with stream:
        current = stream.readline()
        while current:
            following = stream.readline()
            is_last = not following

            if current.strip():
                try:
                    record = json.loads(current)
                except (UnicodeDecodeError, json.JSONDecodeError) as error:
                    if is_last and not current.endswith(b"\n"):
                        return
                    raise UsageUnavailable from error

                if not isinstance(record, dict):
                    raise UsageUnavailable
                yield record

            current = following


def nonnegative_integer(mapping: dict[str, Any], key: str) -> int:
    value = mapping.get(key)
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise UsageUnavailable
    return value


def parse_usage(info: Any) -> TokenUsage | None:
    if info is None:
        return None
    if not isinstance(info, dict):
        raise UsageUnavailable

    total_usage = info.get("total_token_usage")
    if total_usage is None:
        return None
    if not isinstance(total_usage, dict):
        raise UsageUnavailable

    input_tokens = nonnegative_integer(total_usage, "input_tokens")
    output_tokens = nonnegative_integer(total_usage, "output_tokens")
    total_tokens = nonnegative_integer(total_usage, "total_tokens")
    if total_tokens != input_tokens + output_tokens:
        raise UsageUnavailable

    cached = total_usage.get("cached_input_tokens")
    if cached is not None:
        cached_tokens = nonnegative_integer(total_usage, "cached_input_tokens")
        if cached_tokens > input_tokens:
            raise UsageUnavailable

    reasoning = total_usage.get("reasoning_output_tokens")
    if reasoning is not None:
        reasoning_tokens = nonnegative_integer(total_usage, "reasoning_output_tokens")
        if reasoning_tokens > output_tokens:
            raise UsageUnavailable

    return TokenUsage(input_tokens, output_tokens, total_tokens)


def read_transcript(path: Path) -> TranscriptSnapshot:
    metadata: dict[str, Any] | None = None
    latest_usage: TokenUsage | None = None
    child_ids: set[str] = set()

    for record in jsonl_records(path):
        record_type = record.get("type")
        payload = record.get("payload")
        if not isinstance(payload, dict):
            continue

        if record_type == "session_meta" and metadata is None:
            metadata = payload
            continue

        if record_type != "event_msg":
            continue

        payload_type = payload.get("type")
        if payload_type == "token_count":
            usage = parse_usage(payload.get("info"))
            if usage is not None:
                latest_usage = usage
        elif payload_type == "sub_agent_activity":
            child_id = payload.get("agent_thread_id")
            if isinstance(child_id, str) and child_id:
                child_ids.add(child_id)

    if metadata is None:
        raise UsageUnavailable

    thread_id = metadata.get("id")
    if not isinstance(thread_id, str) or not thread_id:
        raise UsageUnavailable

    session_id = metadata.get("session_id", thread_id)
    if not isinstance(session_id, str) or not session_id:
        raise UsageUnavailable

    return TranscriptSnapshot(
        thread_id=thread_id,
        session_id=session_id,
        usage=latest_usage,
        child_thread_ids=frozenset(child_ids),
    )


def sessions_root_for(transcript: Path | None) -> Path:
    if transcript is None:
        return codex_home() / "sessions"

    resolved = transcript.resolve()
    for parent in (resolved.parent, *resolved.parents):
        if parent.name.lower() == "sessions":
            return parent
    return resolved.parent


def index_transcripts(root: Path, explicit: Path | None) -> dict[str, list[Path]]:
    if not root.is_dir():
        raise UsageUnavailable

    index: dict[str, list[Path]] = {}
    try:
        paths = root.rglob("*.jsonl")
        for path in paths:
            match = THREAD_ID_PATTERN.search(path.name)
            if match:
                index.setdefault(match.group(1).lower(), []).append(path.resolve())
    except OSError as error:
        raise UsageUnavailable from error

    if explicit is not None:
        explicit_path = explicit.expanduser().resolve()
        if not explicit_path.is_file():
            raise UsageUnavailable
        snapshot = read_transcript(explicit_path)
        paths_for_id = index.setdefault(snapshot.thread_id.lower(), [])
        if explicit_path not in paths_for_id:
            paths_for_id.append(explicit_path)

    return index


def unique_transcript(index: dict[str, list[Path]], thread_id: str) -> Path:
    candidates = list(dict.fromkeys(index.get(thread_id.lower(), [])))
    if len(candidates) != 1:
        raise UsageUnavailable
    return candidates[0]


def current_transcript(
    index: dict[str, list[Path]], explicit: Path | None
) -> TranscriptSnapshot:
    if explicit is not None:
        return read_transcript(explicit.expanduser().resolve())

    thread_id = os.environ.get("CODEX_THREAD_ID")
    if not thread_id:
        raise UsageUnavailable
    path = unique_transcript(index, thread_id)
    snapshot = read_transcript(path)
    if snapshot.thread_id.lower() != thread_id.lower():
        raise UsageUnavailable
    return snapshot


def aggregate_task_usage(transcript: Path | None) -> TokenUsage:
    root = sessions_root_for(transcript)
    index = index_transcripts(root, transcript)
    current = current_transcript(index, transcript)
    root_id = current.session_id

    pending: deque[str] = deque([root_id])
    seen: set[str] = set()
    input_tokens = 0
    output_tokens = 0
    found_usage = False

    while pending:
        thread_id = pending.popleft()
        normalized_id = thread_id.lower()
        if normalized_id in seen:
            continue
        seen.add(normalized_id)

        path = unique_transcript(index, thread_id)
        snapshot = read_transcript(path)
        if snapshot.thread_id.lower() != normalized_id:
            raise UsageUnavailable
        if snapshot.session_id.lower() != root_id.lower():
            raise UsageUnavailable

        if snapshot.usage is not None:
            input_tokens += snapshot.usage.input_tokens
            output_tokens += snapshot.usage.output_tokens
            found_usage = True

        for child_id in snapshot.child_thread_ids:
            if child_id.lower() not in seen:
                pending.append(child_id)

    if not found_usage:
        raise UsageUnavailable

    return TokenUsage(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=input_tokens + output_tokens,
    )


def format_number(value: int) -> str:
    return f"{value:,}".replace(",", " ")


def render(usage: TokenUsage | None) -> str:
    if usage is None:
        input_value = output_value = total_value = "N/A"
    else:
        input_value = format_number(usage.input_tokens)
        output_value = format_number(usage.output_tokens)
        total_value = format_number(usage.total_tokens)

    return "\n".join(
        (
            f"Input tokens {input_value}",
            f"Output tokens {output_value}",
            f"Estimated total {total_value}",
        )
    )


def main() -> int:
    args = parse_args()
    try:
        usage = aggregate_task_usage(args.transcript)
    except (OSError, UsageUnavailable):
        usage = None
    print(render(usage))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
