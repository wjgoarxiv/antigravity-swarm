---
name: asw-loop
description: Antigravity Swarm Loop executes RED to GREEN to real-surface QA with cleanup receipts.
---

# Antigravity Swarm Loop

Use this skill when a plan exists or the work is clear enough to execute.

## Loop

1. Pick one criterion.
2. Write the failing test and capture RED output.
3. Implement the smallest production change.
4. Capture GREEN output.
5. Run the real Antigravity or application surface.
6. Record cleanup.
7. Re-run the full relevant suite.

Never claim completion from tests alone.

## Subagent Use

- Explorer lane: locate owners, tests, configs, and prior art.
- Librarian lane: check current official docs for libraries or external CLIs.
- Reviewer lane: inspect the diff after implementation.
- Keep all write operations in the execution lane unless the caller explicitly delegates file edits.

## Evidence Ledger

For each criterion, keep a terse ledger:

```text
Criterion:
RED:
Change:
GREEN:
Real surface:
Cleanup:
```

If any row is empty, the loop is still running.
