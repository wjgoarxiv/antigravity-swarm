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
