---
name: asw-comment-check
description: Comment and documentation hygiene for Antigravity Swarm edits.
---

# Antigravity Swarm Comment Check

Use this skill after editing comments, docs, or code with explanatory notes.

- Keep comments that explain why, constraints, contracts, non-obvious algorithms, or operational hazards.
- Remove comments that merely restate the next line of code.
- Avoid generated-sounding section banners and vague TODOs.
- Preserve domain notes, issue links, regex explanations, and compatibility warnings that future maintainers need.
- If a hook flags a comment, either fix it or explain why it is intentionally retained.

## Comment Review

For each changed file:

- Remove comments that say what the code already says.
- Keep comments that explain a constraint, upstream bug, security boundary, performance tradeoff, or user-visible compatibility.
- Replace vague TODOs with an issue link, owner, or remove them.
- Keep README prose product-facing; do not expose internal packaging notes or QA receipts unless the user needs them.

When documentation changes, read it as a new user would: install, first command, next step, and failure recovery should be obvious without internal implementation chatter.
