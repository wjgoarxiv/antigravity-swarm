---
name: asw-review
description: Antigravity Swarm review skill for diff, hook, package, and QA evidence inspection.
---

# Antigravity Swarm Review

Use this skill to review changes before release or publication.

Lead with findings. Prioritize:

- Broken observable behavior.
- Missing RED to GREEN proof.
- Missing manual QA artifact or cleanup receipt.
- Private/reference files entering git or npm packages.
- Hook, LSP, or skill manifests that do not match Antigravity CLI contracts.
- README claims that do not match tested behavior.

## Review Format

Lead with findings:

```text
Findings
- [severity] path:line - issue, impact, evidence needed

Open Questions
- ...

Verification Reviewed
- ...
```

No findings means say that clearly, then list residual risks or test gaps.

## Release-Surface Checks

For packages and plugins, inspect:

- git status and ignored private folders,
- npm or plugin package contents,
- installed file layout,
- hook manifests,
- skill and agent inventory,
- README examples against real output,
- private/reference wording and internal notes.
