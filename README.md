# codex-token-usage

A global skill for Codex that shows the cumulative token usage for the current task.

```text
Input tokens 2,184
Output tokens 742
Estimated total 2,926
```

The skill reads local Codex JSONL logs and retrieves the latest recorded `token_count` event. If the task launched subagents, their token usage is also added recursively without double counting.

## What is included

- **Input tokens** — all input tokens, including cached input.
- **Output tokens** — all output tokens, including reasoning output.
- **Estimated total** — the sum of input and output tokens.
- Each main agent and subagent is counted only once.
- If statistics are unavailable or incompatible, `N/A` is displayed.

The skill only runs when explicitly invoked with:

```text
$codex-token-usage
```

It does **not** run automatically during normal conversations about tokens.

---

## Requirements

- Local Codex session with logs stored in `.codex/sessions`
- Python **3.10+**
- The `python` command must be available from the Codex terminal
- Git (optional, for installation)

Check your Python version:

```powershell
python --version
```

---

## Installation (Git)

Create the user skills directory:

```powershell
New-Item -ItemType Directory -Force `
  -Path "$env:USERPROFILE\.agents\skills" | Out-Null
```

Clone the repository:

```powershell
git clone https://github.com/Web3Zak/codex-token-usage.git `
  "$env:USERPROFILE\.agents\skills\codex-token-usage"
```

Verify the installation:

```powershell
Test-Path "$env:USERPROFILE\.agents\skills\codex-token-usage\SKILL.md"
```

The command should return:

```text
True
```

Codex usually detects the new skill automatically. If it does not appear, open a new task or restart Codex.

---

## Installation (without Git)

1. Open the repository:
   https://github.com/Web3Zak/codex-token-usage
2. Click **Code → Download ZIP**.
3. Extract the archive.
4. Rename the folder from `codex-token-usage-main` to `codex-token-usage`.
5. Move it to:

```text
%USERPROFILE%\.agents\skills\
```

The final directory should look like:

```text
C:\Users\<username>\.agents\skills\codex-token-usage\SKILL.md
```

Avoid double nesting such as:

```text
codex-token-usage\
└── codex-token-usage\
    └── SKILL.md
```

---

## Usage

Run the skill inside any Codex task:

```text
$codex-token-usage
```

Example output:

```text
Input tokens 2,184
Output tokens 742
Estimated total 2,926
```

---

## Updating

If installed via Git:

```powershell
git -C "$env:USERPROFILE\.agents\skills\codex-token-usage" pull --ff-only
```

Restart Codex if necessary.

---

## macOS / Linux

User skills are stored in:

```text
~/.agents/skills
```

Install with:

```bash
mkdir -p ~/.agents/skills

git clone https://github.com/Web3Zak/codex-token-usage.git \
  ~/.agents/skills/codex-token-usage
```

The `python` command must launch Python 3.10 or newer.

---

## Limitations

- The report reflects the latest state already written to the Codex session log.
- Tokens for a response that is still being generated cannot be calculated in advance.
- Cost, rate limits, and context window size are not displayed.
- The skill is intended for local Codex tasks. In cloud environments without local rollout logs, statistics may be unavailable.

---

## Security

- Uses only the Python standard library.
- Reads Codex session logs in **read-only** mode.
- Does **not** modify any files.
- Does **not** send any data over the network.
