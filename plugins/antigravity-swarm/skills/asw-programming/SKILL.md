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
