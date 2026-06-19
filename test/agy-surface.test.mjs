import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { spawnSync } from "node:child_process";
import test from "node:test";

const repoRoot = new URL("..", import.meta.url).pathname;

test("#agy plugin validate #processes Antigravity Swarm plugin surface", () => {
  const result = spawnSync("agy", ["plugin", "validate", "plugins/antigravity-swarm"], {
    cwd: repoRoot,
    encoding: "utf8",
    env: { ...process.env, FORCE_COLOR: "0" },
  });

  assert.equal(result.status, 0, result.stderr);
  assert.match(result.stdout, /skills\s+:\s+15 processed/);
  assert.match(result.stdout, /agents\s+:\s+6 processed/);
  assert.doesNotMatch(result.stdout, /agents\s+:\s+skipped \(not found\)/);
  assert.match(result.stdout, /hooks\s+:\s+(1 processed|skipped \(not found\))/);
});

test("#agents #planner and reviewer preserve ASW execution contracts", async () => {
  const planner = await readFile(`${repoRoot}/plugins/antigravity-swarm/agents/asw-planner.toml`, "utf8");
  const analysis = await readFile(`${repoRoot}/plugins/antigravity-swarm/agents/asw-planning-analysis.toml`, "utf8");
  const audit = await readFile(`${repoRoot}/plugins/antigravity-swarm/agents/asw-plan-audit.toml`, "utf8");
  const reviewer = await readFile(`${repoRoot}/plugins/antigravity-swarm/agents/asw-reviewer.toml`, "utf8");

  assert.match(planner, /\.asw\/plans\/<slug>\.md/);
  assert.match(planner, /## TODOs/);
  assert.match(planner, /Next: start-work <plan-name>/);
  assert.match(planner, /real-surface QA/i);

  assert.match(analysis, /planning analysis/i);
  assert.match(analysis, /execution risks/i);
  assert.match(audit, /ASW PLAN APPROVED/);
  assert.match(audit, /QA scenario/i);

  assert.match(reviewer, /ASW APPROVED/);
  assert.match(reviewer, /ASW REJECTED/);
  assert.match(reviewer, /missing evidence/i);
});
