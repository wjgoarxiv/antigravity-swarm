---
name: asw-remove-ai-slops
description: Remove AI-looking code smells from branch changes or explicit files. Lock behavior with regression tests first, run categorized cleanup in bounded Antigravity lanes, then verify with quality gates.
---

# Antigravity Swarm Remove AI Slops

Use this skill when the user asks to remove slop, clean generated-looking code, deslop a branch, remove noisy comments, simplify over-defensive logic, or tidy recent AI-assisted changes.

The invariant: behavior is locked before cleanup. A checklist is not safety. A passing characterization or regression check is the safety mechanism.

## Inputs

- Default scope: changed files in the current branch compared with the merge base of `main`.
- Optional scope: an explicit file list from the user or from an ASW plan.
- Accepted file types: source, tests, docs, installer scripts, hook scripts, and configuration files owned by the current change.
- Excluded file types: deleted files, binaries, vendored directories, generated output, lockfiles unless the lockfile is the requested surface.

## What this skill does

This skill cleans a bounded set of files while preserving behavior.

It does four things:

1. Determines scope.
2. Locks current behavior with tests or characterization checks.
3. Runs categorized cleanup in safe order.
4. Verifies with quality gates and an ASW review.

It does not:

- change public APIs unless the user explicitly asked,
- remove validation at external boundaries,
- rewrite architecture for taste,
- optimize code when behavior equivalence is not obvious,
- claim completion from green tests alone.

## Categories

### 1. Obvious Comments

Remove:

- comments that restate the next line,
- trivial docstrings on self-explanatory functions,
- section banners,
- commented-out code,
- vague TODOs without owner or issue,
- notes that expose internal process instead of product behavior.

Keep:

- comments explaining why,
- issue links,
- algorithm notes,
- regex explanations,
- boundary or compatibility constraints,
- BDD markers in tests.

### 2. Over-Defensive Code

Remove or simplify:

- null checks for guaranteed values,
- default values for required parameters,
- broad catches around code that cannot throw,
- duplicated validation after a trusted parse step,
- stale compatibility shims no longer documented or tested,
- empty catches and log-only catches that swallow unknown failures.

Keep:

- validation at user input, network, filesystem, subprocess, database, and external API boundaries,
- nullable data handling,
- top-level CLI or server boundary error handling with explicit reporting,
- security checks.

When narrowing broad catches, handle known errors and rethrow unknown errors.

### 3. Excessive Complexity

Look for:

- nesting deeper than three levels,
- nested ternaries,
- boolean expressions with four or more predicates,
- long parameter lists,
- functions doing several responsibilities,
- type or variant discrimination through long conditional chains,
- generic catch-all object shapes where a typed shape is known.

Preferred cleanup:

- guard clauses,
- named intermediate values,
- small responsibility extraction,
- exhaustive variant handling in the local language,
- typed input parsing at the boundary.

Skip when:

- the pattern is established and clearer in this codebase,
- the path is performance-critical and intentionally shaped,
- the simplification would require a behavior proof you do not have.

### 4. Needless Abstraction

Remove:

- pass-through wrappers,
- single-use helpers that hide simple code,
- speculative interfaces,
- factories that only call constructors,
- indirection created only because future changes might happen.

Keep:

- abstractions with multiple implementations,
- test seams that reduce real coupling,
- framework-required boundaries,
- public extension points.

### 5. Boundary Violations

Flag and fix only when safe:

- UI or command layer importing storage internals,
- hook scripts owning installer policy,
- package tests depending on private reference trees,
- docs claiming behavior not covered by the package,
- pure-named functions with hidden side effects.

When unsure, report the boundary issue and skip the edit.

### 6. Dead Code

Remove:

- unused imports,
- unused private helpers,
- unreachable branches,
- stale feature flags,
- debug output,
- removed-code comments,
- orphaned exports not referenced by docs, tests, package manifests, or dynamic lookup.

Keep:

- dynamic dispatch targets,
- plugin manifest entries,
- public exports,
- intentional rollback flags with evidence.

### 7. Duplication

Remove:

- copy-pasted branches with trivial differences,
- repeated literal sequences,
- redundant helpers doing the same thing,
- duplicated package or hook path logic.

Keep:

- similar code with different intent,
- local duplication that is clearer than premature sharing.

### 8. Performance Equivalences

Apply only when behavior equivalence is obvious:

- list scan to set lookup,
- repeated computation in a loop hoisted outside,
- eager collection to lazy iteration,
- string concatenation in loop to join,
- repeated API or database calls batched when result ordering and errors stay the same,
- redundant clones or deep copies removed,
- repeated length checks cached when the collection cannot mutate.

Do not:

- alter algorithms with subtle correctness conditions,
- micro-optimize without a benchmark,
- change ordering, exception timing, or side effects.

### 9. Missing Tests

If changed behavior is uncovered, add the narrowest regression test before cleanup. The fix is not to remove code; the fix is to lock behavior.

Tests should pin observable outputs, public errors, package contents, generated files, or CLI text rather than private implementation details.

### 10. Oversized Modules

Any source file over 250 pure lines is a design smell unless it is a clearly self-contained script.

Measure pure lines by excluding blanks and comments.

When oversized files are in scope:

1. Identify responsibilities.
2. Name target files by concept, never `utils`, `helpers`, `common`, or numbered chunks.
3. Preserve public imports and package paths.
4. Extract one responsibility at a time.
5. Re-run tests and diagnostics after each extraction.
6. Report any intentionally unsplit file with evidence.

Do not split generated output. Do not split by token count.

## Quality Gates

Run every applicable gate. Mark genuinely absent gates as `N/A` with a reason.

| Gate | Pass condition |
|---|---|
| Behavior lock | relevant tests or characterization checks green before cleanup |
| Regression tests | all relevant tests green after cleanup |
| Full suite | project test runner green, or pre-existing failures named |
| Lint/format | zero new errors |
| Typecheck/diagnostics | zero new diagnostics in changed files |
| Package surface | npm or plugin package excludes private/runtime material |
| Manual QA | real CLI, hook, installer, browser, HTTP, or desktop surface exercised when user-visible behavior changed |
| Review | ASW reviewer has no blockers |

## Process

### Phase 0: Plan

Create a short cleanup plan before editing:

```text
Scope:
- file

Behavior lock:
- test or characterization command

Cleanup order:
- comments -> dead code -> defensive -> duplication -> complexity -> abstraction/boundary -> performance -> oversized modules

Risk:
- low | medium | high
```

### Phase 1: Determine scope

If the user passed paths, use those paths.

Otherwise inspect the branch diff:

```bash
git diff "$(git merge-base main HEAD)"..HEAD --name-only
```

Filter:

- deleted files,
- binary files,
- generated output,
- vendored directories,
- lockfiles unless they are the requested surface.

List final scope before cleanup.

### Phase 2: Lock behavior

For each in-scope source file:

1. Identify observable behavior.
2. Find existing tests.
3. Add a characterization test if coverage is weak.
4. Run the relevant test and confirm it is green before editing.

If no green baseline can be established, stop and report. Do not clean uncovered behavior.

### Phase 3: Cleanup plan

For each file, list categories and order:

```text
File: path
Categories: comments, dead code, defensive
Order: comments -> dead code -> defensive
Risk: low
Behavior lock: command/test id
```

### Phase 4: Parallel cleanup

For multiple independent files, use Antigravity subagents in batches of up to five.

Per-file lane message should include:

- exact file,
- categories to evaluate,
- behavior lock evidence,
- cleanup order,
- hard constraints,
- report format.

Hard constraints for each lane:

- preserve behavior,
- do not change public API signatures,
- do not remove type hints,
- do not introduce dependencies,
- skip uncertain performance changes,
- keep diff minimal.

If a lane fails, collect successful lanes, retry the failed file once, then escalate.

### Phase 5: Verify

Run the quality gates. Then walk the critical review checklist:

Safety:

- no functional logic accidentally removed,
- all boundary error handling preserved,
- types and imports intact,
- public APIs stable.

Behavior:

- return values unchanged,
- side effects unchanged,
- exception behavior unchanged,
- edge cases preserved.

Quality:

- removed code was genuine slop,
- remaining code follows project conventions,
- no orphaned references,
- no subtle performance changes,
- no speculative abstraction added.

### Phase 6: Fix issues

If a gate fails:

1. Identify the exact hunk.
2. Explain why it failed.
3. Revert only that hunk.
4. Apply a safer edit if genuine slop remains.
5. Re-run the failing gate.
6. Stop after repeated failure and report the file, attempts, and hypothesis.

## Output Format

```text
AI SLOP REMOVAL REPORT
======================

Scope:
Files:

Behavior Lock:
- Existing coverage:
- Tests added:
- Baseline status:

Cleanup Plan:
- path: categories in order

Per-File Results:
path
- Category: change summary
- Skipped: preserved for safety

Quality Gates:
- Behavior lock:
- Regression tests:
- Full suite:
- Lint:
- Typecheck:
- Package surface:
- Manual QA:
- Review:

Critical Review:
- Safety:
- Behavior:
- Quality:

Issues Found & Fixed:
- None | details

Remaining Risks / Deferred:
- None | details

Final Status: CLEAN | ISSUES FIXED | REQUIRES ATTENTION
```

## Anti-Patterns

- Skipping behavior lock.
- Bundling unrelated refactors.
- Calling a performance change safe without obvious equivalence.
- Silently skipping gates.
- Removing comments that explain why.
- Touching files outside scope.
- Deleting tests or weakening assertions.
- Calling green tests completion without a real surface when users observe the behavior.

## Final Rule

When in doubt, skip the cleanup and report the suspected slop. False negatives are better than broken behavior.
