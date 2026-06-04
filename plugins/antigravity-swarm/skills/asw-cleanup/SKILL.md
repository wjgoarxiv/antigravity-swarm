---
name: asw-cleanup
description: Remove AI-looking clutter and temporary artifacts without changing behavior.
---

# Antigravity Swarm Cleanup

Use this skill when a file looks generated, noisy, or over-defensive.

- Work on one file at a time unless the user asks for a broader sweep.
- Preserve behavior unless the cleanup request explicitly includes behavior change.
- Remove redundant comments, dead branches, stale compatibility exports, unused helpers, and debug output.
- Keep validation at real boundaries: user input, network, filesystem, subprocesses, and external APIs.
- Stop when cleanup would require guessing about product intent.
