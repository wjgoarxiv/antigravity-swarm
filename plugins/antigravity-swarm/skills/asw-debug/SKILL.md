---
name: asw-debug
description: Hypothesis-driven Antigravity Swarm debugging for crashes, hangs, wrong output, and runtime drift.
---

# Antigravity Swarm Debug

Use this skill for real runtime failures.

1. Reproduce the failure before explaining it.
2. Write at least three plausible hypotheses with distinguishing evidence.
3. Inspect runtime truth: logs, process state, debugger output, network traces, browser traces, or CLI transcripts.
4. After two failed investigation rounds, split the search across independent subagents.
5. Confirm root cause by toggling the suspected cause and observing the behavior change.
6. Add or update the narrowest regression check.
7. Fix minimally, then rerun the original reproduction through the real surface.
8. Remove temporary debugging artifacts and report the cleanup receipt.

## Hypothesis Table

Keep a small table while investigating:

| Hypothesis | Evidence that supports it | Evidence that falsifies it | Next probe |
|---|---|---|---|

Use probes that distinguish between explanations. Re-running the same failing command without a new observation is not progress.

## Runtime Evidence

Choose the surface that matches the bug:

- CLI: command transcript, exit code, stderr, config paths.
- Web: browser screenshot, console log, network trace, route state.
- API: request, response, status, logs, database row if relevant.
- Desktop/IDE: visible UI state, settings file, extension/plugin registration, logs.

After the fix, rerun the original reproduction first, then the broader regression suite.

## Runtime Setup

Before attaching theories to the failure, map the runtime:

- command or UI entrypoint,
- working directory,
- config files read,
- environment variables used,
- process tree or server process,
- logs and where they are written,
- external services involved,
- package or plugin install path,
- user-visible output surface.

Capture the exact reproduction:

```text
Command:
Input:
Expected:
Actual:
Exit code:
Stdout:
Stderr:
Files changed:
```

If the failure is intermittent, record frequency and timing. Do not collapse intermittent behavior into a single deterministic story.

## Specialist Tools

Use the tool that can falsify the current hypothesis:

- process listing for hangs,
- logs for server or hook failures,
- browser traces for frontend failures,
- network traces for API failures,
- package dry-run for missing shipped files,
- plugin validation for Antigravity plugin failures,
- language diagnostics for import/type failures,
- screenshot inspection for visual failures,
- temp install smoke for installer failures,
- git diff for accidental behavior changes.

Do not keep rerunning the same command without a new probe.

## Phase Loop

Use a tight loop:

### Phase 1: Reproduce

- run the failing surface,
- capture exact output,
- confirm it fails now,
- reduce the reproduction if possible.

### Phase 2: Hypothesize

Write at least three plausible hypotheses. Each must have a falsifier.

### Phase 3: Probe

Choose the cheapest probe that distinguishes hypotheses.

### Phase 4: Narrow

Update the table. Remove falsified hypotheses. Add new hypotheses only when the evidence requires them.

### Phase 5: Fix

Make the smallest change that addresses the proven cause.

### Phase 6: Verify

Run:

1. the original reproduction,
2. the new regression check,
3. relevant diagnostics,
4. the real user-visible surface.

## Safety Invariants

- Do not change behavior before proving the cause.
- Do not delete error handling to make a symptom disappear.
- Do not weaken tests to match broken behavior.
- Do not hide flaky failures by increasing timeouts unless timing is proven root cause.
- Do not mutate real user config unless the task is explicitly about install/config and the path is confirmed.
- Do not leave temporary logs, debug prints, or probe files in the final diff.
- Do not claim root cause when the evidence only shows correlation.

## Debug Report

Return:

```text
DEBUG REPORT
Reproduction:
Hypotheses:
Evidence:
Root cause:
Fix:
Regression:
Verification:
Cleanup:
Residual risk:
```
