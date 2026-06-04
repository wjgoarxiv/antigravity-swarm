---
name: asw-cleanup
description: Remove AI-looking clutter and temporary artifacts without changing behavior.
---

# Antigravity Swarm Cleanup

Use this skill when a file looks generated, noisy, or over-defensive.

- Work on one file at a time unless the user asks for a broader sweep.
- Preserve behavior unless the cleanup request explicitly includes behavior change.
- Remove redundant comments, dead branches, stale compatibility exports, unused helpers, and debug output.
- Keep validation at real boundaries: user input, network, filesystem, subprocesses, and external APIs.
- Stop when cleanup would require guessing about product intent.

## Cleanup Order

1. Remove internal notes, stale TODOs, and generated-looking prose.
2. Delete dead imports, unused helpers, and unreachable branches.
3. Collapse needless wrappers only when call sites remain clear.
4. Simplify defensive checks that cannot be reached from a real boundary.
5. Re-run the smallest relevant test after each risky file.

## Preserve

- Compatibility that is still documented and tested.
- Comments that explain non-obvious behavior.
- Explicit validation at external boundaries.
- User-facing copy that carries product tone.
- Changelog, license, and attribution text that is intentionally public.
