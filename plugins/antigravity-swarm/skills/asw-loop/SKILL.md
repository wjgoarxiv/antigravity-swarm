---
name: asw-loop
description: Antigravity Swarm Loop executes RED to GREEN to real-surface QA with cleanup receipts.
---

# Antigravity Swarm Loop

Use this skill when a plan exists or the work is clear enough to execute.

## Loop

1. Pick one criterion.
2. Write the failing test and capture RED output.
3. Implement the smallest production change.
4. Capture GREEN output.
5. Run the real Antigravity or application surface.
6. Record cleanup.
7. Re-run the full relevant suite.

Never claim completion from tests alone.

## Subagent Use

- Explorer lane: locate owners, tests, configs, and prior art.
- Librarian lane: check current official docs for libraries or external CLIs.
- Reviewer lane: inspect the diff after implementation.
- Keep all write operations in the execution lane unless the caller explicitly delegates file edits.

## Evidence Ledger

For each criterion, keep a terse ledger:

```text
Criterion:
RED:
Change:
GREEN:
Real surface:
Cleanup:
```

If any row is empty, the loop is still running.

## Criterion Loop

Run one criterion at a time:

```text
Criterion:
Automated test:
Manual QA channel:
Expected observable:
Cleanup target:
```

If the criterion is too broad, split it before editing. A criterion should be small enough that one failing test and one real-surface scenario can prove it.

## RED to GREEN

For behavior changes:

1. Write the automated test first.
2. Run it and capture the failing assertion.
3. Make the smallest production change.
4. Run the same test and capture the passing output.
5. Run adjacent regression tests.

For refactors:

1. Identify characterization coverage.
2. Run it green before the refactor.
3. Change structure only.
4. Run it green again.

Do not write production code first and backfill a test later.

## Surface Scenario

After GREEN, run the real surface:

- CLI and installer: tmux transcript.
- Hook: installed or script-level payload smoke with exact input.
- HUD/status line: status payload through the real script.
- Package: dry-run file list and bad-pattern scan.
- Browser: action log and screenshot.
- Desktop/IDE: visible action log and screenshot.

Record:

```text
Scenario:
Tool/channel:
Input:
Expected:
Artifact:
PASS/FAIL:
```

## Cleanup Pairing

Pair every scenario with cleanup:

- close tmux session,
- remove temp config,
- remove temp package output,
- stop servers,
- close browser context,
- remove generated scratch files.

Record cleanup beside the scenario. Do not leave cleanup for the end when multiple scenarios run.

## Reviewer Gate

Run review when:

- 3 or more files changed,
- package contents changed,
- hooks changed,
- public docs changed,
- refactor/migration work occurred,
- the user requested deep or final review.

Reviewer input:

- criteria ledger,
- RED/GREEN evidence,
- surface artifacts,
- diff,
- package/private scan,
- cleanup receipts.

Approval requires no blockers and no missing evidence.

## Stop Rules

Stop and report instead of guessing when:

- a green baseline cannot be established,
- a criterion cannot be tied to a real surface,
- cleanup cannot be verified,
- the same failure repeats after two targeted fixes,
- the user-visible contract is ambiguous.

## Final Output

```text
Criterion ledger:
Tests:
Surface QA:
Cleanup:
Reviewer:
Final status:
```
