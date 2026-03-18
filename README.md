<p align="center">
  <img src="./cover.png" alt="antigravity-swarm cover" width="100%" />
</p>

<h1 align="center">Antigravity Swarm</h1>
<p align="center">
  <em>Run a coordinated team of AI coding agents from Gemini CLI and Antigravity IDE.</em>
</p>
<p align="center">
  <a href="#quick-start">Quick Start</a> ·
  <a href="#why-antigravity-swarm">Why Antigravity Swarm</a> ·
  <a href="#usage">Usage</a> ·
  <a href="#protocol--architecture">Architecture</a> ·
  <a href="./README_KO.md">한국어</a>
</p>
<p align="center">
  <img src="https://img.shields.io/github/stars/wjgoarxiv/antigravity-swarm?style=social" alt="GitHub stars" />
  <img src="https://img.shields.io/badge/license-MIT-blue" alt="MIT license" />
  <img src="https://img.shields.io/badge/python-3.8%2B-green" alt="Python 3.8+" />
  <img src="https://img.shields.io/badge/runtime-Gemini%20CLI-4285F4" alt="Gemini CLI runtime" />
</p>

Antigravity Swarm turns a single-agent workflow into a coordinated coding team. Use the planner to design a roster, the orchestrator to run it live, and the validator to close the mission with verification.

## Antigravity Swarm in Action

```text
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                   Antigravity Swarm Mission Control                        ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
┌──────────────┬──────────┬──────────────┬───────┬─────────┬─────────────────────┐
│ Agent        │ Role     │ Status       │ Time  │ Msgs    │ Backend             │
├──────────────┼──────────┼──────────────┼───────┼─────────┼─────────────────────┤
│ ● Oracle     │ parallel │ Running      │ 12.3s │ ↑2 ↓1   │ tmux %3             │
│ ● Junior     │ parallel │ Running      │ 10.1s │ ↑0 ↓1   │ tmux %4             │
│ ● Librarian  │ serial   │ Pending      │ -     │ -       │ -                   │
│ ● Validator  │ validator│ Pending      │ -     │ -       │ -                   │
└──────────────┴──────────┴──────────────┴───────┴─────────┴─────────────────────┘
┌─── Live Activity ──────────────────────────────────────────────────────────────┐
│ Oracle: Analyzing auth.py module structure...                                  │
└────────────────────────────────────────────────────────────────────────────────┘
[Tab] View  [w,s] Select  [k] Kill  [x] Shutdown  [q] Quit
```

> [!IMPORTANT]
> If your Gemini-based workflow stops at a single agent, Antigravity Swarm adds the missing coordination layer: team planning, live orchestration, mailbox-based collaboration, resumable missions, and a mandatory final validator.

<a id="quick-start"></a>
## Quick Start

Fastest path to a first mission:

1. Install Python dependencies and confirm Gemini CLI is available.

   ```bash
   pip install -r requirements.txt
   gemini --version
   ```

2. Generate a starter team and mission files.

   ```bash
   python3 scripts/planner.py --preset quick "Write unit tests for all Python modules"
   ```

3. Launch the orchestrator.

   ```bash
   python3 scripts/orchestrator.py --yes
   ```

Resume the latest mission:

```bash
python3 scripts/orchestrator.py --resume
```

Try the TUI without Gemini CLI:

```bash
python3 scripts/orchestrator.py --demo
```

> [!TIP]
> The planner generates `subagents.yaml`, `task_plan.md`, `findings.md`, `progress.md`, and the `.swarm/` runtime state in the mission workspace.

<a id="why-antigravity-swarm"></a>
## Why Antigravity Swarm

- **Parallel execution**: Run multiple agents at once instead of waiting on a single long loop.
- **Specialized roles**: Split architecture, search, implementation, critique, and documentation across distinct agents.
- **Built-in verification**: Every generated team ends with `Quality_Validator`, the final gate before mission completion.
- **Live coordination**: Agents can message each other through file-backed mailboxes while the orchestrator keeps the state visible.
- **Mission durability**: Resume interrupted runs, keep an audit trail, and inspect progress after the fact.

The value is not just "more agents." It is explicit coordination: planning, execution, communication, and validation are separated into visible steps you can inspect and control.

## What's New in v2

Antigravity Swarm evolved from a batch dispatcher into a live agent team platform:

- **Inter-agent messaging**: Agents communicate through a file-based JSON mailbox system with `<<SEND_MESSAGE ...>>` and `<<BROADCAST>>` tags.
- **Agent lifecycle management**: `PENDING -> RUNNING -> IDLE -> RUNNING -> COMPLETED/FAILED/SHUTDOWN`
- **Interactive TUI v2**: Dashboard, Messages, and Agent Detail views with keyboard navigation.
- **Backend abstraction**: Thread backend by default, tmux panes when tmux is available.
- **Audit trail**: Append-only JSONL mission logs in `.swarm/audit/`.
- **Mission persistence**: Resume interrupted missions with `--resume`.
- **Team presets**: Reusable configurations through `swarm-config.yaml`.
- **Post-mission reporting**: A summary report with per-agent statistics and recent timeline entries.
- **Streaming side-effect parsing**: Tags execute as they appear in agent output.
- **Heartbeat monitoring**: Dead or stalled agents are detected automatically.

## Prerequisites

Before installing, make sure you have:

| Requirement | Install Command | Notes |
|------------|----------------|-------|
| **Node.js** (v18+) | [nodejs.org](https://nodejs.org) | Needed for Gemini CLI |
| **Gemini CLI** | `npm install -g @google/gemini-cli` | Core runtime used by the agents |
| **Python 3.8+** | [python.org](https://python.org) | Runtime for planner/orchestrator scripts |
| **pip packages** | `pip install -r requirements.txt` | Installs `rich`, `pyyaml` |

> [!TIP]
> If Gemini CLI is not installed, the planner can offer an install flow the first time you run a mission.

## Installation

> [!TIP]
> You can paste the following block directly into an LLM agent and let it perform installation end-to-end.

```text
Install this repository end-to-end with verification.

Repository: https://github.com/wjgoarxiv/antigravity-swarm
Target directory: <your-install-path>/antigravity-swarm

Do this exactly:
1) Clone the repo into the target directory (if it already exists, do not reset/delete; report current state).
2) Install dependencies from requirements.txt.
3) Verify runtime prerequisites and script health:
   - gemini --version
   - python3 -m py_compile scripts/*.py scripts/core/*.py scripts/core/backends/*.py
   - python3 scripts/orchestrator.py --demo
4) If this repository contains nvim/neovim setup files, apply those settings too; if not, report "no nvim config found" and continue.

Safety rules:
- Stop immediately on the first failure and report the exact failed command plus reason.
- Never run destructive git commands (reset --hard, force push, checkout --, delete existing dirs).

Final report format:
- Cloned: yes/no
- Dependencies: yes/no
- Validation: pass/fail
- Nvim setup: applied/skipped
- Next action: one line
```

### Manual Install

1. Clone the repository and enter it.

   ```bash
   git clone https://github.com/wjgoarxiv/antigravity-swarm.git
   cd antigravity-swarm
   ```

2. Link or copy it into your Gemini skills directory.

   ```bash
   mkdir -p ~/.gemini/skills
   ln -s "$(pwd)" ~/.gemini/skills/antigravity-swarm
   ```

3. Install Python dependencies.

   ```bash
   pip install -r requirements.txt
   ```

4. Ensure the `gemini` command is available in `PATH`, then adjust `swarm-config.yaml` if you want custom presets or backend settings.

### Agent One-Shot Prompt (Update/Upgrade)

```text
Update this repository safely and re-validate without reinstalling from scratch.

Repository path: <your-install-path>/antigravity-swarm

Do this exactly:
1) Check current git status and branch.
2) Pull the latest changes safely (no destructive operations).
3) Reinstall/refresh Python dependencies only if requirements.txt changed.
4) Run validation:
   - gemini --version
   - python3 -m py_compile scripts/*.py scripts/core/*.py scripts/core/backends/*.py
   - python3 scripts/orchestrator.py --demo
5) If nvim/neovim config files exist in this repo and changed, apply/update them; otherwise report "no nvim update needed".

Safety rules:
- Never run destructive git commands (reset --hard, clean -fd, force push, checkout --).
- If merge/rebase conflicts happen, stop and report files with conflicts.

Final report format:
- Pulled: yes/no
- Dependency refresh: yes/no
- Validation: pass/fail
- Nvim update: applied/skipped
- Next action: one line
```

## Operational Notes

> [!NOTE]
> **Windows compatibility**
>
> Antigravity Swarm includes Windows-aware handling for PowerShell and Korean locale environments. UTF-8 output is enforced where possible, and the TUI switches to native `msvcrt` keyboard input on Windows while using `termios`/`tty` on macOS and Linux.

> [!WARNING]
> **Do not modify runtime state while the orchestrator is running.**
>
> The system actively reads and writes `task_plan.md`, `findings.md`, `progress.md`, `subagents.yaml`, and the `.swarm/` directory. Manual edits during execution can introduce race conditions or inconsistent agent behavior.

> [!NOTE]
> **State files are part of the workflow**
>
> A mission creates shared working memory files plus `.swarm/` runtime state. Treat them as coordination artifacts, not disposable scratch files, until the run is complete.

<a id="usage"></a>
## Usage

Pick the path that matches how you want to work.

### Path A: Gemini CLI

Custom team planning:

```bash
python3 scripts/planner.py "Your mission"
python3 scripts/orchestrator.py --yes
```

Preset-driven planning:

```bash
python3 scripts/planner.py --preset quick "Your mission"
python3 scripts/orchestrator.py --yes
```

Resume:

```bash
python3 scripts/orchestrator.py --resume
```

Demo:

```bash
python3 scripts/orchestrator.py --demo
```

### Path B: Autonomous Loop

```bash
python3 scripts/ultrawork_loop.py "Your mission"
```

Resume:

```bash
python3 scripts/ultrawork_loop.py --resume
```

`ultrawork_loop.py` re-plans and re-runs the mission for up to five attempts if a run fails.

### Path C: Antigravity IDE

Add this skill to `~/.gemini/GEMINI.md` so the main agent can trigger it automatically for larger tasks.

## Example Prompts

Not sure how to phrase a mission? Copy-paste one of these prompts into your LLM agent.

### Basic Usage

```text
Use the antigravity-swarm skill to write unit tests for this project.
```

```text
Use the antigravity-swarm skill to refactor the authentication module in this project.
```

### Advanced Usage

```text
Use the antigravity-swarm skill with the fullstack preset to build a React Todo app.
```

```text
Use the antigravity-swarm skill with the analysis preset to inspect the codebase architecture and generate documentation.
```

### Direct CLI Usage

```bash
# Quick mission with a compact roster
python3 scripts/planner.py --preset quick "Write unit tests for all Python modules"
python3 scripts/orchestrator.py --yes

# Full-stack team for a broader build
python3 scripts/planner.py --preset fullstack "Build a REST API with authentication"
python3 scripts/orchestrator.py --yes

# Analysis-heavy team for planning and critique
python3 scripts/planner.py --preset analysis "Review the architecture and identify risks"
python3 scripts/orchestrator.py --yes
```

> [!TIP]
> In an IDE agent, plain-language requests like `Use the antigravity-swarm skill to ...` are usually enough to trigger the workflow.

## Available Agent Roles

The planner selects 2-5 specialists from this pool and always places `Quality_Validator` last.

| Role | Expertise | Default Model |
|------|-----------|---------------|
| **Oracle** | Architecture, deep debugging, root cause analysis | `auto-gemini-3` |
| **Librarian** | Documentation search, code structure analysis, research | `auto-gemini-3` |
| **Explore** | Fast file search, pattern matching, reconnaissance | `auto-gemini-3` |
| **Frontend** | UI components, styling, accessibility, frontend logic | `auto-gemini-3` |
| **Doc_Writer** | READMEs, API docs, comments | `auto-gemini-3` |
| **Prometheus** | Strategic planning, requirements gathering | `auto-gemini-3` |
| **Momus** | Critical review, feasibility checks, risk identification | `auto-gemini-3` |
| **Sisyphus** | Task coordination, delegation, progress tracking | `auto-gemini-3` |
| **Junior** | Concrete implementation, direct execution | `auto-gemini-3` |
| **Quality_Validator** | Final QA, verification, testing | `auto-gemini-3` |

## Configuration

Edit `swarm-config.yaml` to customize runtime behavior and team presets:

```yaml
# Antigravity Swarm Configuration
version: 1

# Spawn backend: auto | tmux | thread
backend: auto

# Default model for agents
default_model: auto-gemini-3

# Maximum parallel agents
max_parallel: 5

# Mailbox polling interval (milliseconds)
poll_interval_ms: 1000

# Permission mode: auto | ask | deny
permission_mode: auto

# Audit trail
audit_enabled: true

# TUI refresh rate (frames per second)
tui_refresh_rate: 10

# Context compaction threshold (lines before compacting)
compaction_threshold: 50

# Team presets
presets:
  fullstack:
    description: "Full-stack development team"
    agents:
      - {name: Oracle, mode: parallel}
      - {name: Frontend, mode: parallel}
      - {name: Junior, mode: parallel}
      - {name: Quality_Validator, mode: validator}
  analysis:
    description: "Deep analysis and planning team"
    agents:
      - {name: Prometheus, mode: serial}
      - {name: Momus, mode: serial}
      - {name: Librarian, mode: parallel}
      - {name: Quality_Validator, mode: validator}
  quick:
    description: "Fast single-agent execution"
    agents:
      - {name: Junior, mode: serial}
      - {name: Quality_Validator, mode: validator}
```

Use a preset:

```bash
python3 scripts/planner.py --preset fullstack "Build a Todo app"
python3 scripts/planner.py --preset analysis "Review architecture risks"
python3 scripts/planner.py --preset quick "Fix a small bug safely"
```

## Agent Communication

Agents communicate with two message tags that are parsed from streamed output.

### Send a Direct Message

```markdown
<<SEND_MESSAGE to="Junior">>
I mapped the auth module. Please implement the OAuth2 flow in `src/auth/oauth.py`.
<<END_MESSAGE>>
```

### Broadcast to the Whole Team

```markdown
<<BROADCAST>>
The API contract is frozen. Everyone should follow `docs/api.yml`.
<<END_BROADCAST>>
```

Messages are stored in `.swarm/mailboxes/` and surfaced in the orchestrator's message timeline.

## TUI Controls

The interactive TUI has three views with keyboard navigation.

| Key | Action |
|-----|--------|
| **Tab** | Cycle between Dashboard, Messages, and Agent Detail views |
| **w / s** | Move selection |
| **Enter** | Open the selected agent or message |
| **k** | Kill the selected agent |
| **x** | Send a shutdown request to the selected agent |
| **q** | Quit the orchestrator |
| **Esc** | Return to Dashboard view |
| **?** | Show help |

### Dashboard View

- **Agent**: Agent name and state indicator
- **Role**: `parallel`, `serial`, or `validator`
- **Status**: `Pending`, `Running`, `Idle`, `Completed`, `Failed`, or `Shutdown`
- **Time**: Runtime duration
- **Msgs**: Sent and received message counts
- **Backend**: `thread` process info or a tmux pane id

### Messages View

Shows inter-agent messages in chronological order, including sender, receiver, and a short preview.

### Agent Detail View

Shows one agent's full output, status history, and recent context at a glance.

<a id="protocol--architecture"></a>
## Protocol & Architecture

### The Manus Protocol

Antigravity Swarm follows a persistent state-management pattern:

- **`task_plan.md`**: The master checklist for the mission
- **`findings.md`**: Shared scratchpad for research and discoveries
- **`progress.md`**: Running log of completed work and current status

### Inter-Agent Mailbox System

In addition to the Manus files, v2 introduces a file-based JSON mailbox layer:

- **`.swarm/mailboxes/{agent}/inbox/`**: Unread messages for each agent
- **`.swarm/mailboxes/{agent}/processed/`**: Archive of consumed messages
- **Message shape**: JSON records with sender, receiver, type, body, and timestamps
- **Delivery model**: The orchestrator polls mailboxes and injects new messages into agent prompts

This lets agents collaborate dynamically without competing to edit the same markdown files.

### The Validator Rule

The last agent in any team must be `Quality_Validator`.

- **Role**: Reviewer and QA gatekeeper
- **Task**: Check `task_plan.md`, inspect artifacts, run verification, and confirm the mission is actually complete
- **Benefit**: A final feedback loop before completion claims

### Agent Lifecycle

Agents move through these states:

1. **PENDING**: Hired but not started
2. **RUNNING**: Actively processing work
3. **IDLE**: Waiting for more work and able to receive messages
4. **COMPLETED**: Finished successfully
5. **FAILED**: Stopped because of an unrecoverable error
6. **SHUTDOWN**: Exited after a shutdown request

The orchestrator also tracks heartbeats so dead or stalled agents can be detected automatically.

### Backend Abstraction

Two execution backends are supported:

- **Thread backend**: Default and portable. Each agent runs as a subprocess tracked by a Python thread.
- **Tmux backend**: Auto-selected when tmux is available and you are not already inside a tmux session. Each agent runs in its own pane for live monitoring.

You can keep backend selection on `auto` or force `thread` / `tmux` in `swarm-config.yaml`.

## Directory Structure

### Repository Layout

```text
antigravity-swarm/
├── scripts/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── types.py
│   │   ├── mailbox.py
│   │   ├── audit.py
│   │   ├── mission.py
│   │   └── backends/
│   │       ├── __init__.py
│   │       ├── base.py
│   │       ├── thread_backend.py
│   │       └── tmux_backend.py
│   ├── planner.py
│   ├── orchestrator.py
│   ├── dispatch_agent.py
│   ├── ultrawork_loop.py
│   ├── compactor.py
│   ├── reporter.py
│   └── mock_gemini_timeout.sh
├── cover.png
├── GEMINI_example.md
├── gemini-extension.json
├── requirements.txt
├── swarm-config.yaml
├── SKILL.md
├── README.md
└── README_KO.md
```

### Generated in the Mission Workspace

When you run a mission, Antigravity Swarm creates coordination files in the working directory:

```text
your-project/
├── subagents.yaml
├── task_plan.md
├── findings.md
├── progress.md
└── .swarm/
    ├── config.json
    ├── mailboxes/
    ├── audit/
    └── missions/
```

### Runtime State (`.swarm/`)

```text
.swarm/
├── config.json                  # Team roster and settings snapshot
├── mailboxes/
│   ├── oracle/
│   │   ├── inbox/
│   │   └── processed/
│   └── junior/
│       ├── inbox/
│       └── processed/
├── audit/
│   └── mission-xyz.jsonl
└── missions/
    └── mission-xyz.json
```

## Credits & Inspiration

This project is heavily inspired by **[Oh-My-Opencode](https://github.com/code-yeongyu/oh-my-opencode)**.

Key ideas adopted here:

- **Multi-agent orchestration**: Specialized roles such as Oracle, Librarian, and Sisyphus
- **The Manus Protocol**: Persistent markdown files for state management, with additional inspiration from **[planning-with-files](https://github.com/OthmanAdi/planning-with-files)**
- **Ultrawork Loop**: A repeated `plan -> act -> verify` cycle for autonomous progress

Thanks to the original creators for establishing these interaction patterns.
