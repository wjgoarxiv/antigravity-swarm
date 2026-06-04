#!/usr/bin/env node

import { readFileSync } from "node:fs";

const WORD = "(?<![A-Za-z0-9_-])";
const END = "(?![A-Za-z0-9_-])";
const PLAN_RE = new RegExp(`${WORD}(?:asw-plan|swarmwork-plan)${END}`, "i");
const GOAL_RE = new RegExp(`${WORD}(?:asw-goal|swarmwork-goal)${END}`, "i");
const START_WORK_RE = new RegExp(`${WORD}(?:start-work|asw-start-work|swarmwork-start)${END}`, "i");
const CLEANUP_RE = new RegExp(`${WORD}(?:asw-cleanup|asw-remove-ai-slops|swarmwork-cleanup)${END}`, "i");
const LOOP_RE = new RegExp(`${WORD}(?:asw-loop|asw|swarmwork)${END}`, "i");
const REVIEW_RE = new RegExp(`${WORD}(?:asw-review|swarmwork-review)${END}`, "i");

function readPayload() {
  try {
    const raw = readFileSync(0, "utf8");
    return raw.trim() ? JSON.parse(raw) : {};
  } catch {
    return {};
  }
}

function promptFrom(payload) {
  if (typeof payload.prompt === "string") return payload.prompt;
  if (typeof payload.userMessage === "string") return payload.userMessage;
  if (Array.isArray(payload.steps)) {
    const lastUser = payload.steps
      .map((step) => step?.userMessage)
      .filter((value) => typeof value === "string")
      .at(-1);
    return lastUser ?? "";
  }
  if (typeof payload.transcriptPath === "string") {
    return promptFromTranscript(payload.transcriptPath);
  }
  return "";
}

function stringsFrom(value, out = []) {
  if (typeof value === "string") {
    out.push(value);
  } else if (Array.isArray(value)) {
    for (const item of value) stringsFrom(item, out);
  } else if (value && typeof value === "object") {
    for (const item of Object.values(value)) stringsFrom(item, out);
  }
  return out;
}

function promptFromTranscript(transcriptPath) {
  try {
    const lines = readFileSync(transcriptPath, "utf8").trim().split(/\r?\n/).slice(-200);
    for (let i = lines.length - 1; i >= 0; i -= 1) {
      const line = lines[i];
      if (!line) continue;
      try {
        const record = JSON.parse(line);
        const role = record.role ?? record.type ?? record.kind ?? "";
        if (typeof role === "string" && /assistant|system|tool/i.test(role)) continue;
        const joined = stringsFrom(record).join("\n");
        if (directiveFor(joined)) return joined;
      } catch {
        if (directiveFor(line)) return line;
      }
    }
  } catch {
    return "";
  }
  return "";
}

const PLAN_DIRECTIVE = `ASW PLAN MODE ENABLED!

You are Antigravity Swarm's planning specialist. Convert the user request into a decision-complete implementation plan for Antigravity CLI.

Required behavior:
- Ground the plan in the current repository before asking questions.
- Use Antigravity subagents for independent research, implementation, or review lanes.
- Write the plan to .asw/plans/<slug>.md with ## TL;DR, ## TODOs, exact files, tests, hook surfaces, and manual QA commands.
- Make every TODO atomic: lane, files, RED test or reproduction, GREEN command, real-surface QA channel, artifact path, and cleanup receipt.
- Include happy-path, edge-case, and adjacent-surface regression QA scenarios; tests are supporting evidence, not completion proof.
- Include privacy/package safeguards and cleanup receipts for any spawned QA state.
- End with Next: start-work <plan-name>; do not end with a passive "let me know" handoff.
- Do not implement code while in plan mode unless the user explicitly asks to execute.`;

const GOAL_DIRECTIVE = `ASW GOAL MODE ENABLED!

You are Antigravity Swarm's durable goal orchestrator. Convert the request into explicit goals, success criteria, and evidence requirements.

Required behavior:
- Preserve the user's full objective across turns and sessions.
- Define concrete success criteria before implementation begins.
- Assign each criterion to observable evidence from tests plus a real surface such as tmux, browser, HTTP, or desktop QA.
- Track blockers, retries, cleanup receipts, and completion audits.
- Do not mark completion until every criterion is proven by current evidence.`;

const START_WORK_DIRECTIVE = `ASW START-WORK MODE ENABLED!

You are Antigravity Swarm's plan executor. Execute an existing ASW plan until every top-level checkbox is complete.

Required behavior:
- Select the named plan, or the only active plan under .asw/plans when the user did not name one.
- Re-read the plan before each step and execute the first unchecked top-level checkbox.
- Use Antigravity subagents for independent subtasks; keep dependent edits serialized.
- For every checkbox, capture RED-to-GREEN tests, real-surface QA, adversarial checks where relevant, and cleanup receipts before marking it done.
- Keep local continuation state in .asw/start-work/ and update the plan only after verification passes.
- When all top-level checkboxes are complete, print ORCHESTRATION COMPLETE with the plan path, verification commands, artifacts, and cleanup receipts.`;

const CLEANUP_DIRECTIVE = `ASW CLEANUP MODE ENABLED!

You are Antigravity Swarm's cleanup specialist. Remove AI-looking clutter while preserving behavior.

Required behavior:
- Bound the scope to the named files or changed branch diff.
- Preserve behavior with existing tests or a narrow characterization test before cleanup edits.
- Remove obvious comments, dead code, needless defensive code, stale compatibility shims, duplicate branches, and oversized structure only when the behavior is proven safe.
- Keep validation at real boundaries and preserve comments that explain why.
- Run relevant verification and real-surface QA when cleanup affects user-visible behavior.`;

const LOOP_DIRECTIVE = `ASW LOOP MODE ENABLED!

You are Antigravity Swarm's evidence-driven execution loop. Ship the requested outcome end-to-end through Antigravity CLI surfaces.

Required behavior:
- Start with a concrete success contract.
- Write failing tests before production changes.
- Run the smallest implementation that flips RED to GREEN.
- Drive the real surface through tmux, HTTP, browser, or computer-use QA.
- Capture artifacts and cleanup receipts.
- Use subagents when work can proceed in parallel without shared-state conflicts.`;

const REVIEW_DIRECTIVE = `ASW REVIEW MODE ENABLED!

You are Antigravity Swarm's reviewer. Inspect the diff for behavioral regressions, missing tests, unsafe packaging, stale docs, and hook/LSP failures.

Lead with findings ordered by severity. Treat missing manual QA evidence as a blocking issue.`;

function directiveFor(prompt) {
  if (PLAN_RE.test(prompt)) return PLAN_DIRECTIVE;
  if (GOAL_RE.test(prompt)) return GOAL_DIRECTIVE;
  if (START_WORK_RE.test(prompt)) return START_WORK_DIRECTIVE;
  if (CLEANUP_RE.test(prompt)) return CLEANUP_DIRECTIVE;
  if (REVIEW_RE.test(prompt)) return REVIEW_DIRECTIVE;
  if (LOOP_RE.test(prompt)) return LOOP_DIRECTIVE;
  return "";
}

const directive = directiveFor(promptFrom(readPayload()));
if (!directive) {
  process.stdout.write("{}");
} else {
  process.stdout.write(JSON.stringify({ injectSteps: [{ userMessage: directive }] }));
}
