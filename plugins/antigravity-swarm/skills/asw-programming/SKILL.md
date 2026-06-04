---
name: asw-programming
description: Strict implementation discipline for Python, TypeScript, JavaScript, Go, and Rust work.
---

# Antigravity Swarm Programming

Use this skill when editing code.

- Read the existing pattern before adding an abstraction.
- Prefer typed, parsed, structured APIs over stringly logic.
- Keep files small enough to review; split only when it reduces real complexity.
- Write the failing test first when behavior is changing.
- Avoid broad defensive code that hides invalid states.
- Do not leave debug output, dead compatibility shims, generated clutter, or unexplained comments.
- Run language diagnostics for changed files before declaring done.
- Verify the user-facing command, page, API, or package surface, not just the helper function.

## Implementation Order

1. Read nearby code and tests.
2. Identify the public contract and the smallest failing check.
3. Make the minimal change.
4. Run the narrow check, then the broader command the repository already trusts.
5. Inspect generated or packaged output when the changed file ships.
6. Remove temporary logs, scratch files, and unused helpers.

## Style

- Match local naming, module boundaries, and formatting.
- Add abstractions only when they remove real duplication or clarify ownership.
- Prefer structured parsers over ad hoc string manipulation when available.
- Keep comments focused on constraints, invariants, and surprising decisions.
- Do not rewrite unrelated files to satisfy personal taste.
