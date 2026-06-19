#!/usr/bin/env node

import { readFileSync } from "node:fs";
import { join, resolve } from "node:path";

const root = resolve(process.argv[2] ?? new URL("..", import.meta.url).pathname);
const problems = [];

function read(path) {
  return readFileSync(join(root, path), "utf8");
}

function json(path) {
  return JSON.parse(read(path));
}

function expect(label, actual, expected) {
  if (actual !== expected) problems.push(`${label}: expected ${expected}, found ${actual}`);
}

function expectContains(path, expected, patterns) {
  const text = read(path);
  for (const pattern of patterns) {
    if (!pattern(expected).test(text)) problems.push(`${path}: missing ${expected} for ${pattern.name || "version pattern"}`);
  }
}

const pkg = json("package.json");
const version = pkg.version;
const lock = json("package-lock.json");

expect("package-lock.json version", lock.version, version);
expect("package-lock.json packages[''].version", lock.packages?.[""]?.version, version);
expect("plugins/antigravity-swarm/plugin.json", json("plugins/antigravity-swarm/plugin.json").version, version);

expectContains("plugins/antigravity-swarm/scripts/asw-statusline.mjs", version, [
  function statuslineConstant(v) { return new RegExp(`ASW_VERSION\\s*=\\s*["']${escapeRegExp(v)}["']`); },
]);
for (const path of ["README.md", "README_KO.md"]) {
  expectContains(path, version, [
    function badgeAlt(v) { return new RegExp(`ASW v${escapeRegExp(v)}`); },
    function badgeUrl(v) { return new RegExp(`ASW-v${escapeRegExp(v)}`); },
    function hudExample(v) { return new RegExp(`ASW v${escapeRegExp(v)}`); },
  ]);
}
expectContains("docs/RELEASE_CHECKLIST.md", version, [
  function packageCandidate(v) { return new RegExp(`antigravity-swarm@${escapeRegExp(v)}`); },
]);

if (problems.length > 0) {
  process.stderr.write(`version drift detected for ${version}:\n${problems.map((p) => `- ${p}`).join("\n")}\n`);
  process.exit(1);
}

process.stdout.write(`version lockstep ok: ${version}\n`);

function escapeRegExp(value) {
  return String(value).replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}
