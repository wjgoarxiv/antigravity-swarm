---
name: asw
description: Antigravity Swarm execution loop for evidence-driven implementation with tests, subagents, hooks, and manual QA.
---

# Antigravity Swarm Loop

Use this skill when the user asks to complete a non-trivial coding, documentation, packaging, or automation task through Antigravity CLI.

## Operating Contract

1. Define the observable outcome before editing.
2. Read repository guidance and the files that own the behavior.
3. Write a failing automated test for each production behavior change.
4. Implement the smallest change that makes the test pass.
5. Run the real user-facing surface through tmux, HTTP, browser, or computer-use QA.
6. Capture the artifact path or transcript and clean up spawned state.
7. Use Antigravity subagents for independent research, test, or review lanes.

## Hook Aliases

The installed PreInvocation hook wakes this mode from `asw`, `asw-loop`, `swarmwork`, and the legacy compatibility alias `ulw`.

