import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

const repoRoot = new URL("..", import.meta.url).pathname;

const shippedSources = [
  "bin/antigravity-swarm.js",
  "bin/installer/commands.mjs",
  "bin/installer/files.mjs",
  "bin/installer/hud.mjs",
  "bin/installer/main.mjs",
  "bin/installer/options.mjs",
  "bin/installer/paths.mjs",
  "bin/installer/ui.mjs",
  "plugins/antigravity-swarm/scripts/asw-hook.mjs",
  "plugins/antigravity-swarm/scripts/asw-lsp-check.mjs",
  "plugins/antigravity-swarm/scripts/asw-statusline.mjs",
  "plugins/antigravity-swarm/scripts/asw-stop-check.mjs",
];

function pureLoc(source) {
  return source
    .split("\n")
    .filter((line) => line.trim() && !line.trim().startsWith("//") && !line.trim().startsWith("#"))
    .length;
}

test("#code health #shipped JS entrypoints stay review-sized", async () => {
  for (const file of shippedSources) {
    const source = await readFile(`${repoRoot}/${file}`, "utf8");
    assert.ok(pureLoc(source) <= 250, `${file} exceeds 250 pure LOC`);
  }
});
