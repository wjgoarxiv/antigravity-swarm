import assert from "node:assert/strict";
import { readdir, readFile } from "node:fs/promises";
import { spawnSync } from "node:child_process";
import test from "node:test";

const repoRoot = new URL("..", import.meta.url).pathname;
const expectedAgentFiles = [
  "asw-explorer.toml",
  "asw-librarian.toml",
  "asw-planner.toml",
  "asw-reviewer.toml",
];

test("#npm pack surface #includes Antigravity plugin and excludes private references", () => {
  const result = spawnSync("npm", ["pack", "--dry-run", "--json"], {
    cwd: repoRoot,
    encoding: "utf8",
  });

  assert.equal(result.status, 0, result.stderr);
  const [{ files, version }] = JSON.parse(result.stdout);
  const paths = files.map((file) => file.path);

  assert.equal(version, "0.2.1");
  assert.ok(paths.includes("bin/antigravity-swarm.js"));
  assert.ok(paths.includes("bin/installer/commands.mjs"));
  assert.ok(paths.includes("bin/installer/ui.mjs"));
  assert.ok(paths.includes("plugins/antigravity-swarm/plugin.json"));
  for (const agentFile of expectedAgentFiles) {
    assert.ok(paths.includes(`plugins/antigravity-swarm/agents/${agentFile}`));
  }
  assert.ok(paths.includes("plugins/antigravity-swarm/hooks/hooks.json"));
  assert.ok(paths.includes("plugins/antigravity-swarm/scripts/asw-statusline.mjs"));
  assert.ok(paths.includes("plugins/antigravity-swarm/skills/asw-goal/SKILL.md"));
  assert.ok(paths.includes("plugins/antigravity-swarm/skills/asw-plan/SKILL.md"));
  assert.ok(paths.includes("plugins/antigravity-swarm/skills/asw-start-work/SKILL.md"));
  assert.ok(paths.includes("plugins/antigravity-swarm/skills/asw-remove-ai-slops/SKILL.md"));
  assert.ok(paths.includes("cover.png"));

  assert.equal(paths.some((path) => path.startsWith("REFERENCE_" + ["lazy", "codex"].join("") + "/")), false);
  assert.equal(paths.some((path) => path.startsWith("worktree-swarm-lag-hardening/")), false);
  assert.equal(paths.some((path) => path.includes("__pycache__")), false);
  assert.equal(paths.some((path) => path.includes("/.omx/")), false);
});

test("#agent surface #ASW roles match the expected agent inventory", async () => {
  const aswDir = `${repoRoot}/plugins/antigravity-swarm/agents`;
  const aswFiles = (await readdir(aswDir)).filter((name) => name.endsWith(".toml")).sort();
  const expectedFiles = expectedAgentFiles;

  assert.deepEqual(expectedFiles, aswFiles);

  for (const aswFile of expectedFiles) {
    const asw = await readFile(`${aswDir}/${aswFile}`, "utf8");
    const legacyReasoningField = "model_" + "reasoning_effort";
    const legacyModelPrefix = "g" + "pt-";
    assert.doesNotMatch(asw, new RegExp(`^${legacyReasoningField}\\s*=`, "m"), `${aswFile} must avoid legacy reasoning-effort fields`);
    assert.doesNotMatch(asw, new RegExp(`^model\\s*=\\s*"${legacyModelPrefix}`, "m"), `${aswFile} must avoid legacy model presets`);
    assert.equal(/developer_instructions = """[\s\S]+"""/.test(asw), true, `${aswFile} must carry role instructions`);
  }

  assert.match(await readFile(`${aswDir}/asw-planner.toml`, "utf8"), /planner|plan/i);
  assert.match(await readFile(`${aswDir}/asw-explorer.toml`, "utf8"), /read-only|inspect|search/i);
  assert.match(await readFile(`${aswDir}/asw-librarian.toml`, "utf8"), /source|documentation|citation/i);
  assert.match(await readFile(`${aswDir}/asw-reviewer.toml`, "utf8"), /ASW APPROVED|ASW REJECTED/);
});
