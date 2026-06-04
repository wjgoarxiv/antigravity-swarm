---
name: asw-goal
description: Durable Antigravity Swarm goal orchestration with success criteria and observable evidence.
---

# Antigravity Swarm Goal

Use this skill when a task spans turns, sessions, or multiple deliverables.

1. Convert the request into explicit goals with success criteria.
2. For each criterion, name the evidence that will prove it.
3. Keep tests, package checks, and diagnostics as supporting evidence.
4. Prove user-facing behavior through a real surface: tmux for CLI, browser for web, HTTP for APIs, or desktop automation for GUI.
5. Keep a short ledger in the repo or task notes when continuation state matters.
6. Before completion, audit every criterion against current files and command output.

Do not call a goal done because tests are green. Green tests are one signal; observable behavior is the gate.

## Goal Ledger

Use `.asw/goals/<slug>.md` when a durable local ledger is needed. Keep it small:

- objective,
- success criteria,
- current evidence,
- open blockers,
- cleanup items,
- final audit.

Do not store secrets, private transcripts, package tokens, or personal local paths that are not needed for execution.

## Completion Audit

Before closing the goal:

- Re-read the newest user request.
- Check every success criterion against current evidence.
- Verify package/git boundaries when files may ship.
- Confirm that background processes, temp directories, and generated QA artifacts are either cleaned up or intentionally named.
- Report the exact remaining risk if any criterion is only partially verified.
