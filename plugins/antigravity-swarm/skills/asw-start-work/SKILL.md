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

## Resume Protocol

On start:

1. Read the selected plan.
2. Read `.asw/start-work/state.json` if present.
3. Confirm the last completed checkbox.
4. Confirm any in-progress checkbox.
5. Verify artifacts listed in state still exist or mark them stale.
6. Inspect git status.
7. Continue from the first unchecked checkbox.

State shape:

```json
{
  "plan": ".asw/plans/name.md",
  "activeTask": "Task 3",
  "completed": [],
  "artifacts": [],
  "cleanup": [],
  "blockers": []
}
```

Do not restart from scratch when state exists. Reconcile state with the plan.

## Evidence Ledger

For each checkbox, append:

```text
Task:
RED:
Implementation:
GREEN:
Manual QA:
Reviewer:
Cleanup:
Status:
```

If a plan item has no RED test because it is docs-only or inventory-only, record the exemption and the replacement check. Do not silently skip evidence.

## Manual QA Channels

Run the channel named by the plan:

- HTTP call for API behavior,
- tmux for CLI, installer, hook, HUD, and package smoke,
- browser for web UI,
- computer use for desktop or IDE flows.

If the named channel is impossible in the environment, record:

- why it is impossible,
- nearest authoritative fallback,
- what risk remains.

Do not substitute unit tests for manual QA.

## Reviewer Gate

Run a reviewer before completion when:

- the plan's final verification wave asks for it,
- 3 or more files changed,
- package or public docs changed,
- hooks, agents, skills, installer, or status line changed,
- private/runtime exclusion is part of the goal.

Reviewer packet:

- selected plan,
- evidence ledger,
- diff,
- automated test outputs,
- manual QA artifacts,
- package/private scans,
- cleanup receipts,
- remaining risk.

Blockers must be fixed and rechecked before final status.

## Cleanup Receipts

Every task must close its own resources:

- temp dirs removed,
- tmux sessions killed,
- spawned servers stopped,
- browser contexts closed,
- generated scratch files deleted,
- package tarballs removed,
- config backups restored or documented.

Append one receipt per resource. A missing cleanup receipt keeps the task open.

## Failure Handling

When a task fails:

1. Capture the failing command and output.
2. Identify whether the failure is code, test, environment, or plan quality.
3. Fix code/test issues with the smallest change.
4. Update the plan if the task was underspecified.
5. Retry once with a clearer check.
6. If the same blocker repeats, stop and report with evidence.

Do not mark the checkbox done because a fallback passed unless the fallback proves the same user-visible criterion.

## Final Verification

Before printing completion:

- all top-level checkboxes are marked complete,
- evidence ledger has no empty RED/GREEN/manual QA rows except documented exemptions,
- final verification wave ran,
- package/private surfaces were checked when shipping changed,
- reviewer gate passed when triggered,
- cleanup list is closed,
- git status is understood.

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
