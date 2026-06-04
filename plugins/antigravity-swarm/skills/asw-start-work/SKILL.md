---
name: asw-start-work
description: Execute an ASW plan after asw-plan, with subagents, verification, real-surface QA, continuation state, and cleanup receipts.
---

# Antigravity Swarm Start Work

Use this skill after `asw-plan` when the user says `start-work`, `asw-start-work`, execute the plan, continue the plan, or resume a plan under `.asw/plans/`.

## Contract

1. Select the named plan. If no name is provided, inspect `.asw/plans/` and choose the only active plan; ask one focused question only when multiple plans match.
2. Create or resume `.asw/start-work/state.json` before editing. Track the selected plan path, active checkbox, spawned subagents, artifacts, and cleanup items.
3. Re-read the selected plan before each step.
4. Execute the first unchecked top-level checkbox in `## TODOs` or `## Final Verification Wave`.
5. Split independent work across Antigravity subagents. Keep dependent file edits serialized.
6. For each checkbox, capture:
   - failing test or reproduction before production changes,
   - passing automated verification after the fix,
   - real-surface QA through tmux, browser, HTTP, or desktop automation,
   - applicable adversarial checks,
   - cleanup receipt for every spawned QA resource.
7. Mark the checkbox done only after the evidence exists.
8. Continue to the next unchecked checkbox without asking whether to proceed.

## Execution Rules

- If the selected checkbox is too broad, split it inside the plan before editing.
- Keep one status ledger entry per checkbox: started, RED evidence, implementation, GREEN evidence, real-surface QA, cleanup, done.
- Do not mark a checkbox complete until the evidence named in the plan exists.
- If a command fails for environmental reasons, capture the exact failure and choose the nearest authoritative fallback.
- If user instructions conflict with the plan, follow the newest user instruction and update the plan ledger.
- If unrelated local changes exist, preserve them and work around them.

## Completion

When every top-level checkbox is complete, run the plan's final verification commands and print:

```text
ORCHESTRATION COMPLETE
Plan: <path>
Verification: <commands>
Artifacts: <paths>
Cleanup: <receipts>
```

Never treat green tests alone as completion. The plan is done only when the observable user-facing surface has been exercised and all continuation state is closed.
