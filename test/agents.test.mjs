import assert from "node:assert/strict";
import { readdir, readFile } from "node:fs/promises";
import { join } from "node:path";
import test from "node:test";

const repoRoot = new URL("..", import.meta.url).pathname;
const agentsDir = join(repoRoot, "plugins", "antigravity-swarm", "agents");

test("#agents #ports every REFERENCE ultrawork core agent under ASW names", async () => {
  const files = (await readdir(agentsDir))
    .filter((name) => name.endsWith(".toml"))
    .sort();

  assert.deepEqual(files, [
    "asw-explorer.toml",
    "asw-librarian.toml",
    "asw-planner.toml",
    "asw-reviewer.toml",
  ]);

  for (const file of files) {
    const content = await readFile(join(agentsDir, file), "utf8");
    assert.match(content, /^name\s*=\s*"asw-.+"$/m);
    assert.match(content, /^description\s*=\s*".+"$/m);
    assert.match(content, /^nickname_candidates\s*=\s*\[.+\]$/m);
    assert.match(content, /^model\s*=\s*".+"$/m);
    assert.match(content, /^model_reasoning_effort\s*=\s*".+"$/m);
    assert.match(content, /^developer_instructions\s*=\s*"""/m);
    assert.doesNotMatch(content, /source_reference|ultrawork|ultragoal|REFERENCE_lazycodex|LazyCodex|OMO/);
  }
});
