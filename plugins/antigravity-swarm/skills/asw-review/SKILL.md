---
name: asw-review
description: Antigravity Swarm review skill for diff, evidence, hook, package, docs, installer, and real-surface QA inspection.
---

# Antigravity Swarm Review

Use this skill before release, publication, merge, or any claim that broad work is complete.

Lead with findings. Approval is earned by evidence.

## Review Lanes

### Lane 1: Goal Fidelity

Check:

- newest user request,
- explicit non-goals,
- version and publish constraints,
- requested commit/push behavior,
- language and tone constraints,
- private/reference exclusion requirements.

Reject if the diff solves a different problem or leaves a requested criterion unaddressed.

### Lane 2: Behavior

Check:

- changed behavior has RED-to-GREEN proof,
- refactors have characterization coverage,
- errors and edge cases are preserved,
- public API or CLI flags are stable unless intentionally changed,
- status line examples match real output,
- installer menu output matches tests and manual smoke.

Reject if behavior is inferred instead of proven.

### Lane 3: Real Surface

Check the surface the user actually touches:

- tmux transcript for CLI and terminal UX,
- HTTP transcript for APIs,
- browser screenshot and action log for web,
- desktop automation evidence for GUI,
- package install transcript for npm installers,
- plugin validation transcript for Antigravity plugin surfaces.

Tests alone are not enough for user-visible behavior.

### Lane 4: Code Quality

Check:

- local patterns,
- type and diagnostic output,
- dead code,
- needless abstraction,
- duplicated logic,
- oversized modules,
- comments and docs quality,
- generated-looking filler.

Reject if cleanup removes meaningful behavior or adds broad speculative architecture.

### Lane 5: Release Surface

Check:

- git status,
- ignored private/runtime files,
- package allowlist,
- tarball file list,
- hook manifest,
- skill inventory,
- agent inventory,
- generated assets,
- README examples,
- version fields.

Reject if private/reference/runtime material can ship.

### Lane 6: Antigravity Compatibility

Check:

- Antigravity plugin validation,
- hook phase registration,
- hook command paths after install,
- global skill shims,
- agent TOML shape,
- status line command,
- IDE-compatible config path,
- no stale platform claims.

## Evidence

Every review should list evidence actually inspected:

- test commands and outcomes,
- manual QA channel and artifact,
- package dry-run output,
- plugin validation output,
- residue scan,
- git status,
- installed-path smoke,
- screenshots or captured panes when visual output changed.

Missing evidence is a blocker.

## Verdict

Return one of:

- `ASW APPROVED` when every criterion is proven and no blockers remain.
- `ASW REJECTED` when any issue blocks release.

"Looks good except" is rejected.

## Findings Format

```text
Findings
- [severity] path:line - issue. Impact. Required evidence or fix.

Open Questions
- ...

Evidence Reviewed
- ...

Verdict: ASW APPROVED | ASW REJECTED
```

Severity:

- Critical: leaks private material, breaks install/package, unsafe destructive behavior.
- High: user-visible behavior broken, missing test for changed behavior, false README claim.
- Medium: weak diagnostics, missing edge coverage, stale wording.
- Low: polish, maintainability, naming.

## Package Review Checklist

- `npm pack --dry-run --json` inspected.
- `bad` list is empty for private/runtime patterns.
- `README.md`, `README_KO.md`, `cover.png`, `LICENSE`, package entrypoints included.
- Reference folders excluded.
- Runtime folders excluded.
- Env and logs excluded.
- Version matches intended publish.

## Hook Review Checklist

- Alias detection covers documented aliases.
- Identifier-like strings are ignored.
- Hook output is valid JSON.
- Malformed stdin is safe.
- Installed hook path runs from the user's config root.
- Status message is visible enough for users.

## Skill Review Checklist

- Skill names match plugin inventory.
- Skills are substantial enough to guide execution.
- Planning skills do not implement.
- Execution skills require tests and real-surface QA.
- Review skills lead with findings.
- No stale harness or private source terminology.

## Agent Review Checklist

- Agent names match plugin inventory.
- Agents describe Antigravity roles.
- Read-only agents forbid edits.
- Planner writes `.asw/plans`.
- Reviewer uses ASW verdicts.
- No legacy model presets or reasoning-effort fields.

## Docs Review Checklist

- The first viewport states the product clearly.
- README install commands work.
- Alias table matches hook behavior.
- HUD examples match real status line output.
- Internal QA notes are absent.
- Claims about quota or IDE support are qualified when data-dependent.

## Completion

Approve only after:

- all findings are fixed,
- full verification reran,
- manual QA reran when a fix touched user-visible behavior,
- cleanup receipts exist,
- working tree state is understood.
