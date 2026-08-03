````markdown
# codex-token-usage

A global skill for Codex that displays the cumulative token usage of the current task.

```text
Input tokens 2,184
Output tokens 742
Estimated total 2,926

Context

███████░░░░░░░░

52%   124k / 240k tokens
```

The skill reads local Codex JSONL logs and retrieves the latest recorded `token_count` event. If the task launched subagents, their token usage is also added recursively without double counting.

## What is included

- `Input tokens` — all input tokens, including cached input.
- `Output tokens` — all output tokens, including reasoning output.
- `Estimated total` — the sum of input and output tokens.
- Each main agent and subagent is counted only once.
- `Context` — the context window usage of the agent where the skill is invoked.
- Subagent context is **not** aggregated, since each agent has its own independent context window.
- If statistics are unavailable or incompatible, `N/A` is displayed.

The skill runs only when explicitly invoked with `$codex-token-usage` and does not activate automatically during normal conversations about tokens.

## Requirements

- A local Codex session with logs stored in `.codex/sessions`.
- Python 3.10 or newer.
- The `python` command must be available from the Codex terminal.
- Git — for installation using the method below.

Check your Python version:

```powershell
python --version
```

## Installation from GitHub (Windows)

Open PowerShell and create the user skills directory:

```powershell
New-Item -ItemType Directory -Force `
  -Path "$env:USERPROFILE\.agents\skills" | Out-Null
```

Clone the repository directly into the skills directory:

```powershell
git clone https://github.com/Web3Zak/codex-token-usage.git `
  "$env:USERPROFILE\.agents\skills\codex-token-usage"
```

Verify the installation:

```powershell
Test-Path "$env:USERPROFILE\.agents\skills\codex-token-usage\SKILL.md"
```

The command should return `True`.

Codex usually detects new skills automatically. If it does not appear, open a new task or restart Codex.

## Installation without Git

1. Open the [Web3Zak/codex-token-usage](https://github.com/Web3Zak/codex-token-usage) repository.
2. Click **Code → Download ZIP**.
3. Extract the archive.
4. Rename the folder from `codex-token-usage-main` to `codex-token-usage`.
5. Move it to `%USERPROFILE%\.agents\skills\`.

The final directory should be:

```text
C:\Users\<username>\.agents\skills\codex-token-usage\SKILL.md
```

Avoid a nested directory structure like:

```text
codex-token-usage\
└── codex-token-usage\
    └── SKILL.md
```

## Usage

In a new or existing Codex task, run:

```text
$codex-token-usage
```

The skill will return a compact summary of token usage and context utilization.

## Updating

If the skill was installed using Git:

```powershell
git -C "$env:USERPROFILE\.agents\skills\codex-token-usage" pull --ff-only
```

Restart Codex afterward if necessary.

## macOS and Linux

User skills are stored in `~/.agents/skills`:

```bash
mkdir -p ~/.agents/skills
git clone https://github.com/Web3Zak/codex-token-usage.git \
  ~/.agents/skills/codex-token-usage
```

The `python` command must launch Python 3.10 or newer.

## Limitations

- The report reflects the latest state already written to the Codex session log.
- It is not possible to calculate the tokens for a response that is still being generated.
- Cost and rate limits are not displayed.
- The skill is intended for local Codex tasks. In cloud environments without local rollout logs, statistics may be unavailable.

The script uses only the Python standard library, reads logs in read-only mode, and does not send any data over the network.
````
