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
