import assert from "node:assert/strict";
import { readdir, readFile } from "node:fs/promises";
import { join } from "node:path";
import test from "node:test";

const repoRoot = new URL("..", import.meta.url).pathname;
const agentsDir = join(repoRoot, "plugins", "antigravity-swarm", "agents");

const forbiddenFragments = [
  "source" + "_reference",
  "ultra" + "work",
  "ultra" + "goal",
  "REFERENCE_" + ["lazy", "codex"].join(""),
  "Lazy" + "Cod" + "ex",
  "O" + "MO",
  "Cod" + "ex",
  "g" + "pt-",
];

test("#agents #ships complete ASW core agent inventory", async () => {
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
    assert.match(content, /^developer_instructions\s*=\s*"""/m);
    assert.doesNotMatch(content, new RegExp(`^model\\s*=\\s*"${"g" + "pt-"}`, "m"));
    assert.doesNotMatch(content, new RegExp(`^${"model_" + "reasoning_effort"}\\s*=`, "m"));
    for (const fragment of forbiddenFragments) {
      assert.equal(content.includes(fragment), false, `${file} includes private/reference fragment ${fragment}`);
    }
  }
});

test("#agents #use Antigravity-native role contracts instead of legacy harness presets", async () => {
  const expected = {
    "asw-explorer.toml": ["Antigravity repository explorer", "Output contract", "When to invoke", "Read-only"],
    "asw-librarian.toml": ["Antigravity external researcher", "official documentation", "version", "citations"],
    "asw-planner.toml": [".asw/plans/<slug>.md", "Plan only", "QA scenarios", "Next: start-work <plan-name>"],
    "asw-reviewer.toml": ["ASW APPROVED", "ASW REJECTED", "package/privacy", "real-surface evidence"],
  };

  for (const [file, needles] of Object.entries(expected)) {
    const content = await readFile(join(agentsDir, file), "utf8");
    assert.ok(content.split(/\r?\n/).length >= 45, `${file} must carry a substantial Antigravity-native contract`);
    for (const needle of needles) assert.match(content, new RegExp(needle.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "i"));
  }
});
