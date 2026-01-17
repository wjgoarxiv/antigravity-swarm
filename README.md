# Antigravity Sub-Agents Skill 🚀

**Hire a team of AI agents to code for you.**

This skill allows you to spawn multiple specialized AI agents (Sub-Agents) to work on complex tasks in parallel. Whether you are using the terminal or the Antigravity IDE, this tool orchestrates a team of experts—Architects, Engineers, and Validators—to solve your problems efficiently.

> [!IMPORTANT] > **Why do you need this?**
> As of 2026-01-18, **there is NO native method** to deploy sub-agents in Gemini CLI or the Antigravity IDE.
> This skill bridges that gap, unlocking true parallel agent orchestration for your environment.

---

## Why use this?

- **Parallel Execution**: Why wait for one agent to finish? Run 3 agents at once (e.g., one writes docs, one writes tests, one writes code).
- **Specialization**: Assign different "Personas" (Prompts) to each agent.
- **Quality Assurance**: **[NEW]** Every team includes a mandatory **Validator Agent** who reviews the work before completion, ensuring high quality.

---

## Installation

1.  **Locate the Skill**: Ensure this repository is in your skills folder:
    ```bash
    ~/.gemini/skills/antigravity-swarm/
    ```
2.  **Install Dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

    _(Requires `rich`, `pyyaml`, etc.)_

3.  **Gemini CLI**: Ensure the `gemini` command is installed and in your PATH.

---

## User Manual

There are two main ways to use this skill.

### 🅰️ Scenario A: Gemini CLI (For Terminal Users)

Use this when you want to manually "hire" a team to do a job for you from your terminal.

**Step 1: Hire the Team (Plan)**
Run the planner with your mission description.

```bash
python3 scripts/planner.py "Create a Snake game with a green background and score tracking"
```

**Step 2: Review the Plan**
The Planner will:

1.  Analyze your request.
2.  Propose a team (e.g., `Game_Designer`, `Python_Dev`, `Quality_Validator`).
3.  Draft a `task_plan.md`.
4.  Ask for your confirmation: `[Plan Mode] Save this configuration? [y/N]` -> Type `y`.

**Step 3: Execute (Orchestrate)**
Once approved, launch the team:

```bash
python3 scripts/orchestrator.py
```

_You will see a Dashboard (TUI) showing all agents working in parallel._

---

### 🅱️ Scenario B: Antigravity IDE (For Agent Users)

Use this when you are chatting with the Gemini Agent in the IDE and want it to handle a complex task autonomously.

**How to Trigger:**
If you have integrated this skill into `~/.gemini/GEMINI.md`, the Main Agent will **automatically** trigger this skill when:

1.  The task involves editing **>3 files**.
2.  The task requires **distinct expertise** (e.g., "I need a backend and a frontend").
3.  The task allows for **parallel work**.

**What happens?**

1.  The Main Agent recognizes the complexity.
2.  It calls `planner.py` internally to design a team.
3.  It calls `orchestrator.py` to execute the work.
4.  It presents the final result (verified by the Validator) to you.

---

## Protocol & Architecture

### The "Manus Protocol"

This skill enforces a rigorous state management protocol:

- **`task_plan.md`**: The master checklist.
- **`findings.md`**: Shared scratchpad for agents to exchange knowledge.
- **`progress.md`**: Immutable log of what has been done.

### The "Validator" Rule

By design, the **final agent** in any generated team is strictly enforced to be a **Quality Validator**.

- **Role**: Reviewer / QA.
- **Task**: Check if `task_plan.md` is complete, run tests, and ensure the user's requirements are met.
- **Benefit**: Redundant self-correction loop.

---

## Directory Structure

```text
antigravity-swarm/
├── scripts/
│   ├── planner.py       # The "Hiring Manager" (Generates subagents.yaml)
│   ├── orchestrator.py  # The "Project Manager" (Runs the agents)
│   └── dispatch_agent.py # The "Worker" (Shim layer for Gemini CLI)
├── subagents.yaml       # The current team roster
├── task_plan.md         # Current mission status
└── README.md            # This file
```
