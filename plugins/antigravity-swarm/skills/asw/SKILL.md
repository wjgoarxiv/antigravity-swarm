---
name: asw
description: Antigravity Swarm execution loop for evidence-driven implementation with tests, subagents, hooks, and manual QA.
---

# Antigravity Swarm Loop

Use this skill when the user asks to complete a non-trivial coding, documentation, packaging, or automation task through Antigravity CLI.

## Operating Contract

1. Define the observable outcome before editing.
2. Read repository guidance and the files that own the behavior.
3. Write a failing automated test for each production behavior change.
4. Implement the smallest change that makes the test pass.
5. Run the real user-facing surface through tmux, HTTP, browser, or computer-use QA.
6. Capture the artifact path or transcript and clean up spawned state.
7. Use Antigravity subagents for independent research, test, or review lanes.

## Hook Aliases

The installed PreInvocation hook wakes this mode from `asw`, `asw-loop`, and `swarmwork`.

## Loop Discipline

- Keep a visible success contract near the top of the working notes.
- Prefer one thin vertical slice over many half-edited files.
- Spawn explorers for read-only mapping, librarians for current external docs, and reviewers for final verification.
- Keep dependent edits in the main thread so file ownership stays clear.
- When the task touches install, hooks, package contents, README, or screenshots, verify the shipped surface instead of only unit tests.
- Stop and surface a blocker only after local discovery and at least one fallback path fail.

## Completion Gate

Before saying the work is done, confirm:

- requested behavior is present,
- relevant tests or diagnostics passed,
- real user-facing surface was exercised,
- temporary state was cleaned up,
- git/npm/package boundaries do not include private or generated material,
- docs describe what was actually verified.

## Binding Success Criteria

For non-trivial work, write a compact success contract before editing:

```text
Deliverable:
Criteria:
- happy path:
- edge case:
- regression:
Tests:
- file + test id:
Manual QA:
- channel:
- command or action:
- expected observable:
Cleanup:
```

Each criterion needs automated evidence and real-surface evidence when users can observe the behavior. Tests are necessary; they are not the whole completion proof.

## Manual QA Channels

Pick the channel that matches the surface:

- HTTP call: API endpoints and service contracts.
- tmux: terminal applications, installers, hooks, CLIs, and status lines.
- Browser use: web pages and browser-visible flows.
- Computer use: desktop or IDE surfaces.

Auxiliary checks such as parsed config dumps, package file lists, and stdout inspection are valid supporting evidence for data-shaped work. They do not replace a channel scenario when the user interacts with the surface.

Every scenario must name:

- exact command or action,
- concrete input,
- expected binary pass/fail observable,
- artifact path or transcript,
- cleanup receipt.

## Durable Notepad

Keep a durable working note for complex work. Prefer `.asw/` runtime state when it belongs to the workflow, or a temp note when the work should not create repo files.

Suggested sections:

```text
Plan:
Success criteria + QA scenarios:
Now:
Todo:
Findings:
Learnings:
Evidence:
Cleanup:
```

Append updates as work progresses. Do not rewrite history in the note; add a correction when assumptions change.

## Todo Discipline

Use small todos:

- one observable criterion at a time,
- one production edit wave at a time,
- one active item at a time,
- mark completion only after evidence exists.

Good todo shape:

```text
path: action for criterion — verify by command/artifact
```

## Verification Gate

Trigger a reviewer pass when the work is broad, risky, release-related, package-related, refactor-heavy, or explicitly requested as rigorous.

The reviewer must receive:

- user goal,
- success criteria,
- diff,
- tests run,
- manual QA artifacts,
- package/private scans,
- residual risks.

Treat reviewer concerns as blockers until fixed or explicitly handed back to the user as a product decision.

## Cleanup Receipts

Every spawned resource needs a receipt:

- tmux session closed,
- temp directory removed,
- browser context closed,
- server stopped,
- generated preview deleted,
- config restored or intentionally kept,
- package tarball removed if produced.

Leftover QA state means the loop is not complete.

## Final Report

Return:

```text
ASW REPORT
Outcome:
Criteria:
Tests:
Manual QA:
Cleanup:
Package/private surface:
Reviewer:
Commit:
Residual risk:
```
