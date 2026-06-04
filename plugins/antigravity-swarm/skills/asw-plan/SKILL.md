---
name: asw-plan
description: Antigravity Swarm Plan creates a decision-complete plan before large or ambiguous work.
---

# Antigravity Swarm Plan

Use this skill for 5+ step work, migrations, release preparation, package ports, broad refactors, or ambiguous user goals.

You are the planner, not an implementer. Refuse implementation while this skill is active; write the executable plan and direct the caller to `start-work`.

## Planner Duties

1. Explore the repo before asking questions.
2. Separate discoverable facts from user preferences.
3. Decide naming, file ownership, tests, QA channels, and rollback boundaries.
4. Split independent work into Antigravity subagent lanes.
5. Produce a plan that an executor can follow without inventing missing decisions.
6. Preserve user language that changes the outcome, but remove rant/noise from the actual task list.
7. Name every assumption that would be expensive to unwind later.

## Discovery Contract

- Run parallel repo exploration before drafting; do not plan from memory alone.
- Use a Socratic interview only for preferences or constraints that cannot be discovered from files.
- Perform a gap analysis against existing behavior, tests, package surface, and docs before writing tasks.
- Keep the output to one plan file and do not edit product files in plan mode.
- Prefer exact local paths over module guesses.
- If a package, installer, hook, or config surface is involved, include a package-surface audit.

## Required Plan Fields

- Write the plan to `.asw/plans/<slug>.md`.
- Include `## TL;DR`, objective, non-goals, and decision summary.
- Include files to edit and tests to write first.
- Include `## TODOs` with atomic checkboxes an executor can run in order.
- Include QA scenarios with exact commands, expected evidence, and cleanup receipts.
- Include privacy/package safeguards.
- End with this exact next step line: Next: `start-work <plan-name>`.

## Downstream Executor Contract

Each checkbox must include references, acceptance criteria, test-first instructions, real-surface QA, expected evidence paths, cleanup receipts, and commit guidance. The executor should be able to resume from the plan without interviewing the user again.

Never end with a passive handoff. End with the exact next step instead.

## Parallel Execution Waves

Split work into waves when tasks can proceed independently.

```text
Wave 1:
- Task A: no dependencies
- Task B: no dependencies

Wave 2:
- Task C: depends on A

Critical path:
A -> C
```

A good wave plan:

- keeps shared setup early,
- avoids two agents editing the same file,
- groups independent tests and docs separately,
- reserves final verification for after all implementation waves,
- makes blockers explicit.

If fewer than two tasks can run independently, say so and keep execution serialized.

## Dependency Matrix

Every non-trivial plan needs a matrix:

| Task | Depends on | Blocks | Can parallelize with |
|---|---|---|---|
| 1 | none | 3 | 2 |

The executor should not need to infer ordering from prose.

## Task Contract

Every task must include:

- what to do,
- what not to do,
- files or directories,
- references,
- RED test,
- GREEN check,
- manual QA scenario,
- cleanup receipt,
- acceptance criteria,
- commit guidance.

Do not separate "write code" and "write tests" into different tasks. Implementation and verification belong together.

## QA Scenarios

Each task needs at least one concrete scenario:

```text
Scenario:
Channel:
Steps:
Expected:
Evidence:
Cleanup:
```

Use:

- HTTP call for API behavior,
- tmux for CLI/install/HUD/hook behavior,
- browser for web behavior,
- computer use for desktop or IDE behavior.

The scenario must be agent-executable. Do not write "user manually checks".

## Commit Strategy

Give commit guidance per task:

```text
Commit: YES|NO
Message:
Files:
Reason:
```

Use conventional commit subjects. Keep commits atomic and green. If the user did not ask for commits, mark commit as `NO` and instruct the executor to report a draft message instead.

## Final Verification Wave

The plan must end with a verification wave:

- plan compliance audit,
- full automated tests,
- package/private surface scan,
- plugin validation when applicable,
- manual QA replay for user-visible surfaces,
- reviewer pass when the change is broad or risky,
- git status review,
- cleanup receipt review.

This wave is not optional. It is the guard against "green tests, broken product".

## Plan Shape

Use this skeleton unless the repository clearly needs something else:

```markdown
# <plan-name>

## TL;DR
<one paragraph>

## Objective
<observable outcome>

## Non-goals
- <what must not change>

## Discovery
- <path>: <fact>

## Decisions
- <decision>: <reason>

## TODOs
- [ ] <task>
  - Files:
  - RED:
  - GREEN:
  - Real-surface QA:
  - Evidence:
  - Cleanup:
  - Commit:

## Parallel Execution Waves
- Wave 1:

## Dependency Matrix
| Task | Depends on | Blocks | Can parallelize with |
|---|---|---|---|

## Final Verification Wave
- [ ] <full test/package/docs/manual QA pass>

Next: `start-work <plan-name>`
```

## Quality Bar

- A plan that says only "create implementation, then test" is not executable.
- A plan that lacks a real-surface check is incomplete when users can observe the change.
- A plan that writes broad tasks without file ownership will stall the executor.
- A plan that requires hidden context from the planning chat is not acceptable.
