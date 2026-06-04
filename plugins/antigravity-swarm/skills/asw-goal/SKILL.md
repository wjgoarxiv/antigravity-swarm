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
