---
name: asw-remove-ai-slops
description: Remove AI-looking clutter from changed files while preserving behavior with regression tests and verification.
---

# Antigravity Swarm Remove AI Slops

Use this skill when the user asks to remove AI slop, clean AI-generated code, deslop a branch, or tidy generated-looking changes.

## Scope

- Default to changed files from the current branch.
- If the user names files, use only those files.
- Exclude generated output, vendored directories, lockfiles, deleted files, and binary files.

## Workflow

1. Identify observable behavior for each file in scope.
2. Confirm existing coverage or write the narrowest characterization test before cleanup.
3. Clean in the safest order:
   - obvious comments and stale notes,
   - dead code and debug output,
   - needless defensive checks,
   - duplication,
   - avoidable complexity,
   - needless abstraction,
   - oversized modules when a named responsibility split is clear.
4. Preserve validation at external boundaries, I/O handling, public APIs, and comments that explain why.
5. Process independent files in parallel subagents when the scope is large.
6. Run relevant tests, diagnostics, and real-surface QA when behavior users can observe may change.
7. Report what was removed, what was intentionally kept, and why.

Do not remove code just because it looks generated. If behavior cannot be locked down, stop and report the uncertainty instead of guessing.
