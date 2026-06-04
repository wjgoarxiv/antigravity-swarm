---
name: asw-goal
description: Durable Antigravity Swarm goal orchestration with explicit success criteria, evidence ledger, manual QA channels, and completion audit.
---

# Antigravity Swarm Goal

Use this skill when a task spans multiple turns, several deliverables, release surfaces, or strict completion criteria.

The invariant: a goal is complete only when every success criterion has current observable evidence.

## Goal Files

Use `.asw/goals/<slug>.md` for durable local state when needed.

Keep it small:

- original objective,
- non-goals,
- success criteria,
- evidence ledger,
- blockers,
- cleanup receipts,
- final audit.

Do not store secrets, private transcripts, tokens, or unnecessary personal paths.

## Success Criteria

Each criterion must include:

- id,
- scenario,
- expected evidence,
- automated test or diagnostic,
- Manual QA channels,
- adversarial risk,
- cleanup requirement,
- pass/fail/block condition.

Use at least:

- happy path,
- edge or malformed input,
- adjacent-surface regression,
- package or privacy surface when distribution is involved.

## Manual QA channels

Choose the channel that matches the surface:

### tmux

Use for CLI, installer, terminal HUD, hook-visible behavior, and terminal menus.

Evidence:

- command sent,
- captured pane output,
- cleanup receipt for the session if spawned.

### HTTP

Use for APIs and local servers.

Evidence:

- request,
- status,
- headers when relevant,
- body,
- server cleanup.

### Browser

Use for web pages and README render previews when visual layout matters.

Evidence:

- action log,
- screenshot path,
- browser/context cleanup.

### Computer use

Use for desktop or IDE GUI behavior.

Evidence:

- action log,
- screenshot,
- app/window state,
- cleanup.

Auxiliary CLI output can support a criterion, but it does not replace the real channel for user-visible behavior.

## Ledger

Record one entry per criterion attempt:

```text
time:
criterion:
status: pass | fail | blocked
automated evidence:
manual channel:
artifact:
cleanup:
notes:
```

Never record pass without cleanup.

## Execution Cycle

1. Re-read the newest user request.
2. Re-read the goal ledger.
3. Pick one pending criterion.
4. Confirm or create the RED test.
5. Implement the smallest change.
6. Run GREEN.
7. Run the manual channel scenario.
8. Capture evidence.
9. Clean temporary state.
10. Record pass, fail, or blocked.
11. Continue to the next criterion.

## Dynamic Steering

Revise the goal only with evidence:

- add a criterion when a real adjacent risk appears,
- split a criterion that is too broad,
- reorder work when dependencies are discovered,
- mark a criterion blocked when external state prevents verification,
- remove a criterion only when the newest user instruction changes the objective.

Do not mutate goals because the work feels hard.

## Completion Audit

Before closing:

- every criterion is pass,
- tests and diagnostics are current,
- manual QA artifacts exist,
- cleanup receipts exist,
- package/git/private boundaries are clean,
- docs match behavior,
- reviewer has no blockers when review is required.

## Failure Handling

If the same criterion fails repeatedly:

1. Stop editing.
2. Record attempts.
3. State the likely cause.
4. Name the evidence needed.
5. Ask for user input only when no safe local path remains.

## Output

When reporting goal status:

```text
Goal:
Criteria:
- id: PASS | FAIL | BLOCKED - evidence
Verification:
Manual QA:
Cleanup:
Remaining risk:
Final status:
```

## Final Rule

Green tests are necessary evidence, not completion. The user-visible surface decides completion.
