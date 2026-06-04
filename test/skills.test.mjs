import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { join } from "node:path";
import test from "node:test";

const repoRoot = new URL("..", import.meta.url).pathname;
const privateSkillPattern = new RegExp([
  "Cod" + "ex",
  "Lazy" + "Cod" + "ex",
  "u" + "lw",
  "ultra" + "work",
  "ultra" + "goal",
  "\\.o" + "mo",
  "O" + "MO",
  "g" + "pt-",
  "model_" + "reasoning_effort",
  "REFERENCE_" + ["lazy", "codex"].join(""),
].join("|"));

test("#asw-plan skill #requires executable start-work handoff", async () => {
  const skill = await readFile(join(repoRoot, "plugins", "antigravity-swarm", "skills", "asw-plan", "SKILL.md"), "utf8");

  assert.match(skill, /\.asw\/plans\/<slug>\.md/);
  assert.match(skill, /## TL;DR/);
  assert.match(skill, /## TODOs/);
  assert.match(skill, /QA scenarios/);
  assert.match(skill, /Next: `start-work <plan-name>`/);
  assert.doesNotMatch(skill, /Let me know if you would like to proceed/i);
});

test("#skills #core ports preserve reference depth in Antigravity terms", async () => {
  const required = {
    "asw-remove-ai-slops": {
      minLines: 240,
      sections: [
        "## Inputs",
        "## What this skill does",
        "## Categories",
        "Performance equivalences",
        "Oversized modules",
        "## Quality Gates",
        "## Process",
        "Phase 1: Determine scope",
        "Phase 2: Lock behavior",
        "Phase 4: Parallel cleanup",
        "Final Status",
      ],
    },
    "asw-programming": {
      minLines: 220,
      sections: ["## Language Gate", "Parse, don't validate", "250 pure LOC", "TypeScript", "Python", "Go", "Rust"],
    },
    "asw-refactor": {
      minLines: 160,
      sections: ["## Refactor Modes", "## Characterization", "## Execution", "## Stop Conditions"],
    },
    "asw-review": {
      minLines: 160,
      sections: ["## Review Lanes", "## Evidence", "## Verdict", "ASW APPROVED", "ASW REJECTED"],
    },
    "asw-goal": {
      minLines: 120,
      sections: [".asw/goals", "Manual QA channels", "success criteria", "ledger"],
    },
  };

  for (const [name, rule] of Object.entries(required)) {
    const skill = await readFile(join(repoRoot, "plugins", "antigravity-swarm", "skills", name, "SKILL.md"), "utf8");
    assert.ok(skill.split(/\r?\n/).length >= rule.minLines, `${name} is too shallow to be a proper port`);
    for (const section of rule.sections) assert.match(skill, new RegExp(section.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "i"));
    assert.doesNotMatch(skill, privateSkillPattern);
  }
});

test("#skills #low-ratio ports carry operational depth", async () => {
  const required = {
    "asw-refactor": {
      minLines: 520,
      sections: [
        "Intent Gate",
        "Parallel Exploration",
        "Codemap",
        "Verification Plan",
        "Test Assessment",
        "Stepwise Execution",
        "Commit Checkpoints",
        "Tool Usage Philosophy",
        "Failure Recovery",
        "Abort Conditions",
      ],
    },
    "asw-review": {
      minLines: 360,
      sections: [
        "Review Context",
        "Parallel Review",
        "Goal Fidelity Reviewer",
        "QA Reviewer",
        "Security Reviewer",
        "Context Mining Reviewer",
        "Verdict Assembly",
      ],
    },
    "asw-programming": {
      minLines: 340,
      sections: [
        "Test Pyramid",
        "Given / When / Then",
        "Cross-language Iron List",
        "Canonical Libraries",
        "Post-write Review Loop",
        "Companion Skills",
      ],
    },
    "asw-debug": {
      minLines: 100,
      sections: ["Runtime Setup", "Phase Loop", "Specialist Tools", "Safety Invariants"],
    },
    "asw-ui-ux": {
      minLines: 75,
      sections: ["Design Process", "Aesthetic Guidelines", "Anti-Patterns", "Execution"],
    },
    "asw-cleanup": {
      minLines: 120,
      sections: ["Detection Criteria", "Deep Consideration", "Detailed Report", "Safety Rules", "When No Clutter Is Found"],
    },
  };

  for (const [name, rule] of Object.entries(required)) {
    const skill = await readFile(join(repoRoot, "plugins", "antigravity-swarm", "skills", name, "SKILL.md"), "utf8");
    assert.ok(skill.split(/\r?\n/).length >= rule.minLines, `${name} still looks under-ported`);
    for (const section of rule.sections) assert.match(skill, new RegExp(section.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "i"));
    assert.doesNotMatch(skill, privateSkillPattern);
  }
});

test("#skills #ASW orchestration ports strict execution safeguards without source traces", async () => {
  const required = {
    "asw": {
      minLines: 110,
      sections: [
        "Binding Success Criteria",
        "Manual QA Channels",
        "Durable Notepad",
        "Verification Gate",
        "Cleanup Receipts",
      ],
    },
    "asw-loop": {
      minLines: 110,
      sections: [
        "Criterion Loop",
        "RED to GREEN",
        "Surface Scenario",
        "Cleanup Pairing",
        "Reviewer Gate",
      ],
    },
    "asw-plan": {
      minLines: 150,
      sections: [
        "Parallel Execution Waves",
        "Dependency Matrix",
        "QA Scenarios",
        "Commit Strategy",
        "Final Verification Wave",
      ],
    },
    "asw-start-work": {
      minLines: 130,
      sections: [
        "Resume Protocol",
        "Evidence Ledger",
        "Manual QA Channels",
        "Reviewer Gate",
        "Cleanup Receipts",
      ],
    },
  };

  for (const [name, rule] of Object.entries(required)) {
    const skill = await readFile(join(repoRoot, "plugins", "antigravity-swarm", "skills", name, "SKILL.md"), "utf8");
    assert.ok(skill.split(/\r?\n/).length >= rule.minLines, `${name} is missing orchestration depth`);
    for (const section of rule.sections) assert.match(skill, new RegExp(section.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "i"));
    assert.doesNotMatch(skill, privateSkillPattern);
  }
});
