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

## Review Context

Gather context before launching review lanes:

1. Read the newest user request.
2. Confirm the current branch and dirty state.
3. Identify changed files.
4. Inspect the diff.
5. Identify generated files.
6. Identify package or install surfaces.
7. Identify user-visible surfaces.
8. Identify requested commit, push, publish, or no-publish constraints.
9. Identify private/runtime exclusion constraints.
10. Identify the commands already run by the implementer.

Context packet:

```text
Goal:
Non-goals:
Changed files:
Generated files:
User-visible surfaces:
Package surfaces:
Private/runtime risks:
Verification already run:
Missing verification:
```

Do not review from memory. The review starts from the actual diff and the newest request.

## Parallel Review

For broad changes, run independent review lanes in parallel or simulate them one by one if subagents are unavailable. The lanes are intentionally redundant; overlap catches false confidence.

Required lanes:

- Goal Fidelity Reviewer,
- QA Reviewer,
- Code Quality Reviewer,
- Security Reviewer,
- Context Mining Reviewer.

Each reviewer returns:

```text
Lane:
Files inspected:
Evidence:
Findings:
Blockers:
Recommended checks:
Verdict:
```

If any lane rejects, the final verdict rejects.

## Goal Fidelity Reviewer

Mission:

- compare the diff to the user's exact request,
- check that newer user messages override older assumptions,
- check version constraints,
- check naming constraints,
- check language constraints,
- check commit/push/publish constraints,
- check that README claims match actual behavior.

Questions:

- Did the implementation solve the requested problem?
- Did it solve an older problem instead?
- Did it add marketing or internal notes the user rejected?
- Did it preserve the requested package/version policy?
- Did it avoid private/reference leakage?
- Did it leave a requested workflow incomplete?

Reject on:

- missing requested file,
- stale README example,
- wrong version,
- unrequested publish,
- missing commit/push when explicitly asked,
- internal management notes in public docs.

## QA Reviewer

Mission:

- exercise the surface users actually touch,
- verify terminal, CLI, HUD, package, browser, or IDE behavior as applicable,
- compare screenshots or transcripts to documentation,
- verify failure paths when the change affects error handling.

QA scenario process:

1. Brainstorm realistic user scenarios.
2. Pick the smallest scenarios that cover changed behavior.
3. Execute through the real surface.
4. Capture command, output, screenshot, or transcript.
5. Compare to README and tests.
6. Report gaps.

For Antigravity Swarm changes, QA may include:

- `agy plugin validate`,
- temp install and verify,
- hook alias smoke,
- status line payload smoke,
- `npm pack --dry-run`,
- README rendering inspection,
- cover image visual inspection,
- installed config path inspection.

Reject when user-visible behavior is only unit-tested but not exercised through the real surface.

## Code Quality Reviewer

Mission:

- inspect maintainability,
- inspect local pattern consistency,
- inspect whether abstractions pay for themselves,
- inspect test quality,
- inspect generated-looking clutter,
- inspect file sizes and responsibility boundaries.

Focus areas:

- behavior hidden in UI helpers,
- IO mixed with rendering,
- parsing repeated across layers,
- broad exception swallowing,
- string manipulation where structured parsing exists,
- stale compatibility paths,
- duplicated tests that do not assert behavior,
- oversized files without ownership split.

Reject when cleanup or refactor weakens behavior proof.

## Security Reviewer

Mission:

- inspect secrets, env files, logs, tokens, local paths, and private references,
- inspect npm package contents,
- inspect shell command construction,
- inspect hook scripts,
- inspect config writes,
- inspect generated artifacts,
- inspect destructive command risk.

For installers and hooks:

- paths must be explicit,
- writes must be scoped,
- user config must not be clobbered,
- malformed input must not crash,
- shell execution must avoid untrusted interpolation,
- package allowlists must exclude runtime state.

Reject on:

- private files in package,
- logs or env files in package,
- untrusted shell construction,
- config overwrite without merge,
- unsafe deletion behavior,
- hidden network operation in install.

## Context Mining Reviewer

Mission:

- search for old names,
- search for contradictory docs,
- search for stale examples,
- search for unported reference terminology,
- search for package metadata drift,
- search for tests that only pass because they stopped checking the real thing.

Search areas:

- README files,
- package metadata,
- plugin manifest,
- hooks,
- agents,
- skills,
- tests,
- installer output,
- generated assets,
- ignored runtime directories only when needed to understand local QA.

Reject if a stale claim remains on a public surface, even when tests pass.

## Verdict Assembly

After collecting lanes:

1. Deduplicate findings.
2. Order by severity.
3. Convert vague concerns into concrete file/line issues.
4. Separate blockers from follow-ups.
5. List evidence actually reviewed.
6. State missing evidence.
7. Return exactly one verdict.

Approval requires:

- no critical or high findings,
- no unresolved medium finding that affects release safety,
- no missing evidence for changed user-visible behavior,
- package/private scan complete when package files changed,
- current git state understood.

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
