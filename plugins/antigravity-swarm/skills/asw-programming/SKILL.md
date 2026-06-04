---
name: asw-programming
description: Strict Antigravity implementation discipline for Python, TypeScript, JavaScript, Go, and Rust work.
---

# Antigravity Swarm Programming

Use this skill when editing source code, tests, hook scripts, installer logic, package scripts, or generated-asset tooling.

## Language Gate

Before editing:

1. Identify the language and runtime.
2. Read local project conventions.
3. Find the authoritative test command.
4. Find typecheck, lint, format, and package commands if present.
5. Write or identify the RED test before production edits.

Do not start implementation from memory. Let the repo tell you how code is shaped.

## Shared Philosophy

### The Type System Is A Proof System

Make invalid states hard to express:

- use semantic names for IDs, paths, modes, states, and options,
- prefer discriminated variants over loose strings,
- keep nullable values near the boundary,
- do not use catch-all shapes when the variants are known.

### Parse, don't validate

Untrusted input crosses a boundary once:

- CLI args,
- JSON payloads,
- config files,
- environment variables,
- hook payloads,
- package manifests,
- external API responses.

At that boundary, parse into a typed or structured value. Inside the code, operate on parsed values instead of re-validating the same assumptions.

### One name, one concept

Avoid using one primitive to represent several concepts. A path, package name, plugin id, color, model label, and command are different concepts even if all are strings.

### Exhaustive variants

When handling modes, commands, languages, colors, result states, or hook phases, make the handling exhaustive. Unknown values should fail clearly at the boundary.

### Small files, honest ownership

Use a 250 pure LOC ceiling as a warning. A file above that line count needs either a clear reason or a split by responsibility. Split by concept, never by chunk number.

## TDD Contract

Use RED to GREEN for behavior changes:

1. Name the observable behavior.
2. Write the failing test or reproduction.
3. Capture RED output.
4. Implement the smallest change.
5. Capture GREEN output.
6. Run the real surface when users can observe the change.

For refactors, write or identify characterization coverage first. The test should be green before the refactor and stay green after.

### Test Pyramid

Use the smallest test that proves the behavior, then climb only when needed:

- pure function tests for deterministic formatting and parsing,
- command tests for CLI arguments and stdout,
- file-system tests for installers and package layout,
- hook payload tests for Antigravity lifecycle behavior,
- integration tests for config merge and installed paths,
- manual QA for terminal rendering, browser rendering, IDE behavior, or generated images.

Avoid replacing a narrow deterministic test with a broad smoke test. Broad smoke tests are useful after the narrow test has made the failure easy to locate.

### Given / When / Then

Behavior tests should make the scenario obvious:

- Given: existing config, payload, files, flags, or state.
- When: the command, hook, helper, or UI action runs.
- Then: the observable output, file, error, or status line is asserted.

BDD comments are allowed when they clarify the shape of the scenario. Do not delete them as clutter.

### Less Mocking

Prefer real temp directories, real files, real JSON parsing, real process execution, and real stdout when the behavior depends on those surfaces.

Mocks are appropriate when:

- the external service is slow or unavailable,
- the test would mutate a real user account,
- the dependency is nondeterministic,
- the mock captures a stable contract.

If a mock hides path handling, shell output, terminal width, package contents, or config merge behavior, it is probably the wrong test.

### Prompt And Skill Tests

Markdown skills and agent prompts are product code in this repo. Test them when they define behavior:

- inventory tests for names,
- section tests for required execution contracts,
- residue tests for private terminology,
- line-depth tests when a port must preserve operational substance,
- README tests when examples must match hook or HUD output.

Do not treat docs as harmless if users copy commands from them.

## TypeScript And JavaScript

Prefer:

- explicit command parsing,
- small pure helpers around string formatting,
- `Map` or object lookup tables for closed sets,
- narrow error handling,
- package tests for npm surfaces,
- no implicit mutation of shared process env unless scoped to the command.

Avoid:

- broad `any` shapes,
- hidden process exits inside helpers,
- catch-all `catch` blocks that swallow errors,
- stringly config updates when JSON parsing is available,
- long functions combining parse, IO, rendering, and write phases.

Recommended checks:

- `npm test`,
- project typecheck if defined,
- targeted script smoke,
- package dry run when shipped files changed.

## Python

Prefer:

- small scripts with explicit `main`,
- typed helper signatures,
- `Path` for filesystem paths,
- structured command arguments,
- deterministic output for generated assets,
- narrow exceptions around optional fonts or platform-specific paths.

Avoid:

- broad exceptions around core logic,
- comments explaining what a function name already says,
- global writes that cannot be overridden in tests,
- mutable default arguments,
- silently ignoring missing dependencies.

Recommended checks:

- `python3 -m py_compile <file>`,
- project test,
- run the script through the real command path.

## Go

Prefer:

- explicit context propagation,
- structured logging at boundaries,
- small interfaces only where they decouple real implementations,
- table tests for variants,
- clear error wrapping.

Avoid:

- panic for ordinary errors,
- global mutable state,
- broad utility packages,
- interface definitions with one local implementation and no test seam.

## Rust

Prefer:

- typed errors,
- exhaustive matches,
- small modules,
- `Result` over panic,
- clear ownership boundaries.

Avoid:

- unwrap in non-test paths,
- large enum matches without default audit,
- hidden clones in loops,
- unsafe code unless the task explicitly requires it and tests cover it.

## Cross-language Iron List

These rules apply everywhere:

- no behavior change without behavior proof,
- no catch-all type when variants are known,
- no duplicate validation inside trusted internal paths,
- no global mutable state unless it is the platform contract,
- no hidden IO inside pure-named helpers,
- no silent fallback that hides broken config,
- no broad exception swallowing,
- no public API removal without explicit request,
- no generated asset change without regeneration proof,
- no package surface claim without dry-run evidence,
- no user-visible text drift from README examples,
- no oversized module split by arbitrary chunk names,
- no new dependency for a small local helper,
- no final status that hides skipped checks.

## Canonical Libraries

Prefer established standard or project-local facilities:

- filesystem paths through the language path library,
- JSON through structured parsers,
- TOML/YAML through the project parser when already present,
- CLI args through the existing command parser,
- subprocesses through explicit argv arrays,
- colors through the existing palette or UI helper,
- terminal rendering through tested width-aware helpers,
- image generation through deterministic scripts,
- package validation through the package manager,
- plugin validation through the Antigravity CLI.

Adding a dependency is justified only when it removes real complexity and is acceptable for the package surface.

## Modern Toolchain Expectations

Before adding new tools, inspect what the repo already uses. Prefer:

- `npm test` or the package's test script for Node repos,
- project typecheck when configured,
- focused `node --test` files for fast RED/GREEN,
- `python3 -m py_compile` for standalone Python scripts,
- project linters when present,
- package dry-run for npm shipping,
- plugin validation for Antigravity plugins,
- temp install smoke for installer changes.

If a tool is absent, say `N/A` with reason instead of pretending the check passed.

## Implementation Order

1. Read local rules and nearby patterns.
2. Determine behavior owner and test owner.
3. Add or identify RED.
4. Implement the smallest production change.
5. Run narrow GREEN.
6. Run language diagnostics.
7. Run full relevant suite.
8. Run real-surface QA.
9. Clean temporary state.
10. Review package/git boundaries when files can ship.

## Error Handling

- Preserve boundary error handling.
- Narrow broad catches where safe.
- Rethrow unknown errors after handling known cases.
- Keep user-facing error messages stable unless the request changes them.
- Do not hide failures to make tests green.

## File Size And Structure

Measure pure LOC for files that feel oversized. If a file is over 250 pure LOC:

- identify responsibilities,
- split by concept,
- preserve imports and exports,
- run tests after each split,
- avoid catch-all names like `utils` or `helpers`.

Standalone scripts may exceed the ceiling only when they are truly one responsibility and easier to ship as one file.

## 250 Pure LOC Ceiling

The 250 pure LOC ceiling is architectural pressure, not a style game. Count non-blank, non-comment lines. When a source file crosses the ceiling:

1. Identify responsibilities.
2. Name the owner module for each responsibility.
3. Split by concept.
4. Preserve public imports through logic-free re-exports when needed.
5. Run tests after each split.
6. Re-check the line count.

Forbidden escapes:

- "It is generated" when it is actually source,
- "It is almost 250",
- `utils`, `helpers`, `common`, `part1`, or chunk-number names,
- moving code without moving tests,
- counting comments or blanks to justify staying.

Acceptable exceptions are rare. They require a note explaining why the file is one responsibility and easier to maintain as one file.

## Post-write Review Loop

After writing code, review it before claiming completion:

1. Measure changed source files that may be oversized.
2. Re-read the diff as a reviewer.
3. Check for behavior drift.
4. Check for missing tests.
5. Check for boundary validation.
6. Check for duplicated parsing.
7. Check for broad catches.
8. Check for stale docs or examples.
9. Check for package/private leakage.
10. Run the verification plan.

If the diff would make you ask a reviewer to trust intent instead of evidence, add evidence.

## Companion Skills

Invoke or follow the relevant ASW skill when the request crosses into another mode:

- use `asw-refactor` for behavior-preserving structural change,
- use `asw-debug` for runtime failures,
- use `asw-review` before release or merge claims,
- use `asw-remove-ai-slops` for branch-wide generated-looking cleanup,
- use `asw-lsp` for diagnostics when language tooling matters,
- use `asw-ui-ux` for visual, README, terminal UI, and cover work,
- use `asw-plan` when scope is broad and execution should wait for a plan.

Do not blend all modes into one vague implementation pass. Name the mode and use its safety contract.

## Package And Hook Work

When editing installer, hooks, skills, agents, or status line:

- test the function,
- test the installed package surface,
- validate the plugin,
- smoke the command through an installed path,
- keep README examples in sync with real output.

## Completion Gate

Do not declare done until:

- RED and GREEN evidence exist for changed behavior,
- diagnostics or fallback checks are clean,
- the user-facing surface was exercised,
- package/private boundaries are clean,
- temporary QA state is cleaned.
- README or user-facing examples are updated when behavior changed.
- The final report names residual risk instead of hiding uncertainty.

## Stop Conditions

Stop and report if:

- no green baseline can be established,
- a requested change conflicts with repo rules,
- behavior cannot be characterized safely,
- an external platform contract is unknown and current docs are needed,
- two attempts fail the same gate for the same reason.
