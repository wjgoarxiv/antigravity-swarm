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

## Detection Criteria

Look for specific clutter, not vibes:

### Obvious Comments

Remove comments that restate the code, section dividers that add no navigation, stale notes, commented-out code, and generic TODOs with no owner or reason.

Keep:

- comments explaining why,
- edge-case notes,
- ticket or issue references,
- regex or algorithm explanation,
- Given / When / Then test markers.

### Over-Defensive Code

Consider simplifying:

- null checks after required parsing,
- broad catches around code that should fail loudly,
- duplicate validation inside trusted paths,
- compatibility branches for versions no longer supported,
- default values for required fields,
- wrappers that only hide errors.

Keep:

- user input validation,
- network and filesystem error handling,
- subprocess error handling,
- package/config boundary validation,
- top-level CLI error reporting.

### Spaghetti Nesting

Flag:

- deeply nested conditionals,
- nested ternaries,
- boolean expressions with many unrelated predicates,
- long functions that mix parse, IO, compute, render, and write,
- variant chains that should be exhaustive handling.

Prefer:

- guard clauses,
- small pure helpers,
- structured variants,
- named predicates only when they clarify domain meaning.

### Dead Or Temporary Code

Remove:

- debug prints,
- unused imports,
- unreachable branches,
- stale feature flags,
- local probe scripts,
- copied output transcripts in source,
- temporary files from QA.

### Needless Abstraction

Remove only when safe:

- pass-through wrappers,
- single-use helpers that obscure behavior,
- speculative interfaces,
- factories that only call constructors,
- config indirection with one value.

Keep abstractions that create a real boundary for testing, platform integration, package layout, or user configuration.

## Deep Consideration

Before editing, ask:

1. What behavior does this code protect?
2. Is the behavior covered?
3. Is this clutter or an intentional compatibility path?
4. Is the code at a boundary?
5. Would removing it change errors, logs, package output, or docs?
6. Can I prove the cleanup is safe with a narrow check?

If the answer is uncertain, skip and report. The default action is preserve, not guess.

## Detailed Report

For each file:

```text
Cleanup Report: <file>
Scope:
Behavior lock:
Removed:
- category:
- before:
- after:
- why safe:
Preserved:
- item:
- reason:
Checks:
Residual risk:
```

Do not summarize cleanup as "tidied code". Say what category was removed and why behavior stayed the same.

## Safety Rules

- Preserve public APIs.
- Preserve documented aliases.
- Preserve config paths.
- Preserve package contents unless package cleanup is the task.
- Preserve validation at boundaries.
- Preserve meaningful error messages.
- Preserve tests that describe behavior.
- Preserve generated assets unless regenerated through the real generator.
- Run the smallest relevant check after risky cleanup.
- Run package or plugin validation when cleanup touches shipped files.

Never:

- remove code because it "looks AI-generated",
- collapse behavior into clever one-liners,
- delete comments explaining why,
- remove fallback behavior without version evidence,
- edit unrelated files during cleanup,
- use cleanup as a hidden refactor,
- use cleanup as a hidden feature change.

## When No Clutter Is Found

Report that clearly:

```text
Cleanup Report: <file>
Result: No cleanup applied.
Inspected:
- comments:
- defensive checks:
- nesting:
- dead code:
- abstractions:
Reason:
Checks:
```

No-op cleanup is valid when the code is already purposeful.
