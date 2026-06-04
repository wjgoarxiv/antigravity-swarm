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

## Discovery Contract

- Run parallel repo exploration before drafting; do not plan from memory alone.
- Use a Socratic interview only for preferences or constraints that cannot be discovered from files.
- Perform a gap analysis against existing behavior, tests, package surface, and docs before writing tasks.
- Keep the output to one plan file and do not edit product files in plan mode.

## Required Plan Fields

- Write the plan to `.omo/plans/<slug>.md`.
- Include `## TL;DR`, objective, non-goals, and decision summary.
- Include files to edit and tests to write first.
- Include `## TODOs` with atomic checkboxes an executor can run in order.
- Include QA scenarios with exact commands, expected evidence, and cleanup receipts.
- Include privacy/package safeguards.
- End with this exact next step line: Next: `start-work <plan-name>`.

## Downstream Executor Contract

Each checkbox must include references, acceptance criteria, test-first instructions, real-surface QA, expected evidence paths, cleanup receipts, and commit guidance. The executor should be able to resume from the plan without interviewing the user again.

Never end with a passive handoff. End with the exact next step instead.
