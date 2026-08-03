---
name: codex-token-usage
description: Report cumulative input, output, and estimated total token usage for the current Codex task, including spawned subagents, plus current context-window usage. Invoke only explicitly as $codex-token-usage when the user wants a compact token and context summary.
---

# Codex Token Usage

1. Run `python "<skill-dir>/scripts/session_token_usage.py"`, resolving `<skill-dir>` to the directory containing this `SKILL.md`.
2. Return the script stdout verbatim as the final response.
3. Add no heading, bullets, code fence, explanation, or other text.
4. Do not recalculate the values or expose parser errors. The script preserves the token and Context sections and prints `N/A` when reliable data is unavailable.
