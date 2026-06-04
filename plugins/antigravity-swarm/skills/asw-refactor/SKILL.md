---
name: asw-refactor
description: Behavior-preserving Antigravity Swarm refactoring with verification and rollback discipline.
---

# Antigravity Swarm Refactor

Use this skill for behavior-preserving structure changes.

1. State the behavior that must remain unchanged.
2. Find existing tests or add a narrow characterization test first.
3. Make one mechanical change at a time.
4. Prefer removing duplication, dead code, or accidental complexity over adding architecture.
5. Rerun diagnostics after each risky step.
6. Finish by exercising the same user-facing surface that existed before the refactor.

## Guardrails

- Never combine a refactor and feature change unless the user asks for both.
- Use characterization tests when behavior is under-tested.
- Keep commits or working chunks small enough to revert.
- Preserve public filenames, exports, CLI flags, env vars, and config keys unless the plan explicitly changes them.
- After moving code, check package allowlists and installer copy paths.

## Stop Conditions

Stop and report instead of guessing when:

- the behavior is not understood,
- no safe characterization exists,
- generated files and source files disagree,
- the refactor requires changing external contracts.
