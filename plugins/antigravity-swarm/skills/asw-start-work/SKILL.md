---
name: asw-start-work
description: Execute an ASW plan after asw-plan, with subagents, verification, real-surface QA, continuation state, and cleanup receipts.
---

# Antigravity Swarm Start Work

Use this skill after `asw-plan` when the user says `start-work`, `asw-start-work`, execute the plan, continue the plan, or resume a plan under `.omo/plans/`.

## Contract

1. Select the named plan. If no name is provided, inspect `.omo/plans/` and choose the only active plan; ask one focused question only when multiple plans match.
2. Create or resume `.omo/start-work/state.json` before editing. Track the selected plan path, active checkbox, spawned subagents, artifacts, and cleanup items.
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
