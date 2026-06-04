import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { join } from "node:path";
import test from "node:test";

const repoRoot = new URL("..", import.meta.url).pathname;

test("#asw-plan skill #requires executable start-work handoff", async () => {
  const skill = await readFile(join(repoRoot, "plugins", "antigravity-swarm", "skills", "asw-plan", "SKILL.md"), "utf8");

  assert.match(skill, /\.omo\/plans\/<slug>\.md/);
  assert.match(skill, /## TL;DR/);
  assert.match(skill, /## TODOs/);
  assert.match(skill, /QA scenarios/);
  assert.match(skill, /Next: `start-work <plan-name>`/);
  assert.doesNotMatch(skill, /Let me know if you would like to proceed/i);
});
