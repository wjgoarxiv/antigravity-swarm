---
name: asw-rules
description: Antigravity Swarm project-rule loading and instruction precedence guidance.
---

# Antigravity Swarm Rules

Use this skill when project instructions, rule files, or hook-injected guidance affect the work.

- Read `AGENTS.md`, `GEMINI.md`, `CONTEXT.md`, and repository-local rule folders before edits.
- Deeper instructions override higher-level instructions for files under their scope.
- Direct user, developer, and system instructions outrank repository files.
- Do not copy private reference text into public package surfaces.
- If rule sources disagree, name the conflict and follow the highest-priority applicable source.

## Rule Search

- Check the working directory and every parent inside the workspace.
- Check deeper instruction files before editing nested folders.
- For generated or vendored files, follow the generation contract first.
- If a rule mentions release wording, commit format, test commands, or package exclusions, treat it as part of the task.

## Reporting

Mention only rules that changed the action you took. Do not clutter the final answer with generic precedence theory.
