---
name: antigravity-swarm
description: Installs and uses Antigravity CLI ASW skills, hooks, diagnostics, and swarm workflow guidance.
---

# Antigravity Swarm

Use this repository as an Antigravity CLI plugin package.

## Primary Commands

```bash
npx antigravity-swarm --dry-run install
npx antigravity-swarm install
npx antigravity-swarm verify
```

## Agent Usage

- Use `asw-plan` for large or ambiguous work.
- Use `asw` or `asw-loop` for test-first implementation plus real-surface QA.
- Use `asw-review` for review.
- Use `start-work` after an `asw-plan` handoff.

## Safety

Do not include local reference material, runtime state, logs, pycache, env files, or private workspace paths in git commits or npm packages.
