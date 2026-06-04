---
name: asw-lsp
description: Antigravity Swarm language diagnostics and symbol-safety workflow.
---

# Antigravity Swarm LSP

Use this skill when edits touch code that has language-server or compiler diagnostics.

1. Identify the changed files and their language.
2. Prefer project-native diagnostics: `npm test`, `tsc --noEmit`, `ruff`, `pyright`, `cargo check`, `go test`, or the repo's configured checker.
3. Use symbol-aware rename/reference tools when available in the active harness.
4. Treat hook diagnostics as early warning only; rerun the authoritative project command before completion.
5. If a language server is unavailable, report the fallback command you used.

## Diagnostic Triage

- Separate pre-existing diagnostics from diagnostics introduced by the current diff.
- Fix introduced diagnostics before broad refactors.
- When a diagnostic is caused by generated files, verify the generator or package output instead of hand-editing generated code.
- For renamed symbols, check imports, tests, docs examples, and package exports.

## Fallbacks

If no language server is available, use the project-native static check:

- TypeScript/JavaScript: `npm test`, `npm run typecheck`, `tsc --noEmit`, or configured lint.
- Python: `pytest`, `ruff`, `pyright`, or `python -m py_compile` for small scripts.
- Rust: `cargo check` and targeted tests.
- Go: `go test ./...`.

Report exactly which fallback ran.
