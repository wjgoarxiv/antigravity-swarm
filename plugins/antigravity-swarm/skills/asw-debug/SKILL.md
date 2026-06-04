---
name: asw-debug
description: Hypothesis-driven Antigravity Swarm debugging for crashes, hangs, wrong output, and runtime drift.
---

# Antigravity Swarm Debug

Use this skill for real runtime failures.

1. Reproduce the failure before explaining it.
2. Write at least three plausible hypotheses with distinguishing evidence.
3. Inspect runtime truth: logs, process state, debugger output, network traces, browser traces, or CLI transcripts.
4. After two failed investigation rounds, split the search across independent subagents.
5. Confirm root cause by toggling the suspected cause and observing the behavior change.
6. Add or update the narrowest regression check.
7. Fix minimally, then rerun the original reproduction through the real surface.
8. Remove temporary debugging artifacts and report the cleanup receipt.
