---
name: asw-refactor
description: Behavior-preserving Antigravity Swarm refactoring with characterization, impact mapping, diagnostics, and real-surface verification.
---

# Antigravity Swarm Refactor

Use this skill for behavior-preserving structure changes: moving code, splitting files, simplifying APIs internally, reducing duplication, or preparing a safer implementation path.

The invariant: refactoring changes structure, not observable behavior.

## Refactor Modes

### Rename

- Symbol, file, command, or config key renames.
- Requires reference search.
- Requires docs and package surface checks if public.
- Must preserve compatibility unless the plan explicitly removes it.

### Extract

- Move one responsibility into a named module or helper.
- Requires characterization coverage.
- New file names must describe concepts.
- Avoid catch-all names.

### Inline

- Remove needless wrappers or abstractions.
- Requires call-site review.
- Keep public exports unless explicitly removed.

### Split

- Divide oversized modules by responsibility.
- Preserve import paths through re-exports only when needed.
- Test after each extraction.

### Rewire

- Change dependency direction or ownership.
- Requires impact map and manual QA.
- Avoid combining with feature work.

## Characterization

Before editing:

1. Identify observable behavior.
2. Find existing tests.
3. Add the narrowest characterization test if coverage is weak.
4. Run it green on the old structure.
5. Record the command and output.

Characterization tests should cover:

- public output,
- public errors,
- package contents,
- hook payloads,
- generated assets,
- CLI behavior,
- status line text,
- installer file layout.

Do not characterize private implementation details unless the refactor is explicitly about that internal contract.

## Impact Map

Build an impact map before edits:

```text
Behavior owner:
Callers:
Tests:
Docs:
Package/install:
Generated output:
Manual QA surface:
Rollback:
```

For each affected file, list whether it is source, test, docs, generated asset, package metadata, or runtime state.

## Execution

1. Establish green baseline.
2. Make one mechanical change.
3. Run narrow tests.
4. Run diagnostics for changed files.
5. Repeat.
6. Run full relevant suite.
7. Exercise the same real surface as before.
8. Check package and git boundaries.

Do not mix:

- refactor plus feature,
- refactor plus visual redesign,
- refactor plus dependency upgrade,
- refactor plus behavior cleanup,
- refactor plus public API removal.

If the user asks for both feature and refactor, separate them in the plan and commit strategy.

## Safe Mechanical Moves

Allowed when covered:

- rename local variables for clarity,
- extract pure helper,
- move constants to owner module,
- collapse pass-through wrappers,
- remove unused private helpers,
- split rendering from IO,
- split parse from execute,
- split package manifest logic from UI rendering,
- move tests next to behavior owner.

High-risk moves:

- public export removal,
- command flag changes,
- hook payload format changes,
- status line layout changes,
- package allowlist changes,
- config path changes,
- generated asset format changes.

High-risk moves require explicit tests and manual QA.

## Diagnostics

Run the repo's authoritative checks. If unavailable, use fallbacks:

- JavaScript or TypeScript: project tests, typecheck, script smoke.
- Python: compile check, script run, project tests.
- Plugin: Antigravity plugin validation.
- Package: dry-run tarball.
- Docs: docs tests and visual/README rendering if relevant.

Treat hook diagnostics as early warnings and rerun the real command.

## Stop Conditions

Stop and report when:

- behavior cannot be characterized,
- the test baseline is red and unrelated,
- a moved symbol is used dynamically and cannot be traced,
- package output changes unexpectedly,
- public docs would become false,
- the refactor needs a product decision,
- two attempts fail the same diagnostic.

## Failure Recovery

If a gate fails:

1. Identify the exact refactor step that caused it.
2. Revert only that step.
3. Preserve earlier green steps.
4. Add stronger characterization if the failure exposed missing coverage.
5. Retry with a smaller move.

Do not use broad destructive commands.

## Output

Report:

- scope,
- characterization evidence,
- files moved or changed,
- behavior preserved,
- tests and diagnostics,
- real-surface QA,
- package/git boundary checks,
- skipped risky refactors,
- final status.

## Quality Bar

The refactor is complete only when the code is easier to reason about and the user-facing behavior is proven unchanged.
