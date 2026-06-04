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

## Intent Gate

Run this gate before touching files. Refactor requests are often mixed with feature requests, cleanup requests, or migration requests; separating them prevents accidental behavior changes.

1. Restate the requested refactor in one sentence.
2. Name the behavior that must remain unchanged.
3. Name the structure that is allowed to change.
4. List explicit non-goals.
5. Identify whether the request is rename, extract, inline, split, rewire, or mixed.
6. If mixed, split the work into ordered phases.
7. Ask for a product decision only when the allowed behavior boundary is unclear.

Use this template:

```text
Intent:
Allowed structural changes:
Behavior that must not change:
Public contracts:
Non-goals:
Refactor mode:
Risk:
```

Reject the refactor if the user-facing behavior cannot be named. A refactor without a behavior boundary is unbounded redesign.

## Parallel Exploration

For broad refactors, inspect in parallel before planning. Use read-only subagents or direct searches to answer independent questions:

- where the target symbol or responsibility is defined,
- where it is called,
- what tests already cover it,
- which docs or README examples mention it,
- what package or install surfaces include it,
- what runtime state or generated output may depend on it,
- which compatibility shims exist and whether they are public.

Exploration agents must return evidence, not opinions:

```text
Question:
Files inspected:
References found:
Tests found:
Public surface:
Risk:
Recommendation:
```

Do not start moving files while exploration is still incomplete for the same dependency graph. Direct local inspection may continue while background exploration runs, but edits wait for enough evidence to build the codemap.

## Direct Search Checklist

Use the fastest appropriate tool:

- symbol search for definitions and call sites,
- text search for docs, examples, and config keys,
- file listing for package boundaries,
- language diagnostics for imports and moved symbols,
- JSON or TOML parsing for manifests,
- package dry-run for shipped files,
- plugin validation for Antigravity assets.

For dynamic references, search strings too. Renames often fail through config files, CLI examples, hook manifests, status-line command strings, and README snippets.

## Codemap

Before planning, write a codemap. It is the source of truth for the refactor.

```text
CODEMAP: <target>

Core files:
- path: role, owner, public/private

Callers:
- path: call shape, risk

Tests:
- path: behavior covered
- missing: behavior not covered

Docs and examples:
- path: wording or command that must stay true

Package/install surface:
- package path, config path, hook path, generated asset, status line

Impact zones:
- low risk:
- medium risk:
- high risk:

Constraints:
- compatibility:
- manual QA:
- rollback:
```

A codemap is not optional for multi-file refactors. If there is only one tiny local edit, a compact paragraph is enough, but it must still identify callers and tests.

## Verification Plan

Create the verification plan before the first edit.

```text
Baseline:
- command:
- expected:

Narrow checks:
- after rename:
- after extract:
- after split:

Diagnostics:
- language:
- package:
- plugin:

Manual QA:
- surface:
- transcript or screenshot:

Regression indicators:
- what would prove behavior changed:
```

The baseline must be green before a behavior-preserving refactor. If the baseline is red, either prove it is unrelated and stable, or stop and report.

## Test Assessment

Detect the repo's test infrastructure before planning:

- package scripts,
- language-specific test folders,
- existing focused tests near the target,
- integration or snapshot tests,
- manual QA scripts,
- plugin or package validation commands,
- generated-asset checks.

Then assess coverage:

```text
Behavior:
Existing tests:
Weak spots:
Characterization needed:
Manual QA needed:
```

Coverage is strong when a failing refactor would fail a test for the right reason. Coverage is weak when the test only checks that a command exits, a file exists, or a broad snapshot changed.

If no test infrastructure exists, create the smallest local reproduction or smoke script that can be run again after the move. If even that is impossible, stop and explain why the refactor is unsafe.

## Verification Checkpoints

Define checkpoints for each phase:

- baseline checkpoint before edits,
- import checkpoint after moved files,
- behavior checkpoint after call-site rewiring,
- docs checkpoint after public wording changes,
- package checkpoint after file layout changes,
- manual QA checkpoint after visual or CLI changes,
- final full-suite checkpoint.

Each checkpoint should name:

- command,
- expected signal,
- failure meaning,
- recovery action.

Example:

```text
Checkpoint: package surface
Command: npm pack --dry-run --json
Expected: changed files included, private/runtime files absent
Failure means: allowlist or ignore boundary changed
Recovery: inspect package files and restore boundary
```

## Planning Protocol

The plan should be stepwise and reversible:

1. Make compatibility-preserving changes first.
2. Move code before changing code.
3. Rename only after reference coverage is complete.
4. Extract pure logic before extracting IO.
5. Keep public exports stable until all call sites migrate.
6. Update docs only after behavior and command surfaces are confirmed.
7. Run checks after every step that can break imports or runtime paths.

Each step must include:

- files touched,
- reason,
- expected diff shape,
- check to run,
- rollback method.

## Stepwise Execution

Execute deterministically:

1. Confirm the current git state.
2. Run the baseline.
3. Apply one mechanical move.
4. Inspect the diff.
5. Run the narrow check.
6. Fix only issues caused by that move.
7. Mark the step complete.
8. Continue to the next move.

Do not batch unrelated moves just because they are easy to edit together. Reviewability matters; a future maintainer should be able to understand each structural change.

## Subagent Staffing

Use subagents when the refactor has independent unknowns:

- explorer for call-site discovery,
- librarian for current external API or platform evidence,
- planner for multi-phase migration design,
- reviewer for final verification.

Subagents should not edit unless explicitly assigned an implementation slice. Read-only exploration is safer for mapping.

For implementation slices:

- each slice owns a bounded file set,
- each slice receives the codemap and verification command,
- each slice reports diff summary and checks,
- the main agent integrates and reruns global checks.

Do not launch many implementation agents against overlapping files. Merge conflicts in a refactor are usually a sign that the responsibility boundary is unclear.

## Import And Export Discipline

When moving code:

- preserve import paths through re-export only when compatibility requires it,
- keep re-export files logic-free,
- avoid circular imports,
- keep side effects in the same runtime phase,
- do not move initialization into modules that are imported by tests or tools,
- update package entrypoints and bin paths deliberately.

New names should describe ownership:

- `statusline-payload` beats `helpers`,
- `installer-paths` beats `utils`,
- `hook-aliases` beats `common`,
- `cover-renderer` beats `misc`.

## Public Surface Guard

Treat these as public until proven otherwise:

- documented CLI commands and flags,
- hook aliases,
- installed config paths,
- status line output examples,
- package contents,
- exported modules,
- README commands,
- generated image dimensions and filenames,
- agent and skill names,
- plugin manifest keys.

Changing any public surface requires an explicit behavior-change plan, not a refactor plan.

## Deprecated Code And Migration

When the refactor includes deprecated paths:

1. Identify whether the deprecated path is public, internal, or test-only.
2. Search docs and package contents.
3. Search installed config examples.
4. Decide whether to keep a shim.
5. Test both old and new paths if compatibility is retained.
6. Remove only when the user requested removal or evidence proves it is private.

Migration refactors should report:

- old contract,
- new contract,
- compatibility plan,
- docs update,
- package impact,
- removal date or condition if a shim remains.

## Commit Checkpoints

If the user asked for commits, organize commits around reviewable behavior:

- characterization tests,
- mechanical move,
- import/call-site update,
- docs/package update,
- cleanup after green verification.

Do not commit red checkpoints. Do not mix a feature change with the refactor commit unless the user explicitly requested a combined commit.

Commit message should describe the structural change:

- `refactor(installer): split config path handling`,
- `refactor(hud): isolate quota formatting`,
- `refactor(skills): expand execution contracts`.

If the user did not ask for commit, leave the worktree ready and report status.

## Tool Usage Philosophy

Use precise tools early:

- text search for broad inventory,
- language diagnostics for moved imports,
- structured parsers for JSON, TOML, YAML, and package manifests,
- package manager commands for shipping boundaries,
- Antigravity plugin validation for plugin assets,
- generated asset scripts for images,
- terminal transcript for TUI changes.

Use direct file reads when a decision depends on exact wording. Do not rely on summary memory for refactor safety.

When a tool fails:

1. read the failure,
2. adjust the command,
3. retry once with a better scope,
4. choose a fallback,
5. report if the missing tool weakens verification.

Never claim a diagnostic passed unless it ran and the output was read.

## Failure Recovery Detail

When a check fails:

1. Record the failing command and exact symptom.
2. Identify the last structural move.
3. Inspect only files touched by that move first.
4. Revert the smallest hunk that caused the failure.
5. Add missing characterization if the failure reveals an untested behavior.
6. Retry with a smaller step.
7. Stop after two failed retries on the same move.

Never hide a failed check by weakening the test unless the test is proven wrong and the proof is documented.

## Abort Conditions

Abort and report when:

- the requested refactor requires changing observable behavior,
- call sites cannot be found reliably,
- generated files cannot be regenerated,
- the package surface changes unexpectedly,
- manual QA cannot be performed for a user-visible surface,
- a public compatibility shim appears necessary but undocumented,
- the same diagnostic fails after two targeted recovery attempts,
- a safer feature-first or test-first change is required.

## Final Refactor Report

Use this shape:

```text
REFACTOR REPORT
Scope:
Intent:
Codemap:
Characterization:
Steps:
Verification:
Manual QA:
Public surface:
Skipped:
Final status:
```

For every skipped refactor, include why it was skipped and what evidence would make it safe later.

## Quality Bar

The refactor is complete only when the code is easier to reason about and the user-facing behavior is proven unchanged.
