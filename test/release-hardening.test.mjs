import assert from "node:assert/strict";
import { mkdtemp, mkdir, readFile, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { spawnSync } from "node:child_process";
import test from "node:test";
import { redactSecrets } from "../plugins/antigravity-swarm/scripts/asw-redact.mjs";

const repoRoot = new URL("..", import.meta.url).pathname;
const hookPath = join(repoRoot, "plugins", "antigravity-swarm", "scripts", "asw-hook.mjs");
const stopPath = join(repoRoot, "plugins", "antigravity-swarm", "scripts", "asw-stop-check.mjs");
const lspPath = join(repoRoot, "plugins", "antigravity-swarm", "scripts", "asw-lsp-check.mjs");
const statuslinePath = join(repoRoot, "plugins", "antigravity-swarm", "scripts", "asw-statusline.mjs");
const lockstepPath = join(repoRoot, "scripts", "check-version-lockstep.mjs");

async function packageVersion() {
  return JSON.parse(await readFile(join(repoRoot, "package.json"), "utf8")).version;
}

function runNode(script, payload, env = {}) {
  return spawnSync("node", [script], {
    cwd: repoRoot,
    input: typeof payload === "string" ? payload : JSON.stringify(payload),
    encoding: "utf8",
    env: { ...process.env, FORCE_COLOR: "0", ...env },
  });
}

test("#release #version lockstep preflight passes current surfaces and catches drift", async () => {
  const expectedVersion = await packageVersion();
  const clean = spawnSync("node", [lockstepPath], { cwd: repoRoot, encoding: "utf8" });
  assert.equal(clean.status, 0, clean.stderr);
  assert.match(clean.stdout, new RegExp(`version lockstep ok: ${expectedVersion.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}`));

  const temp = await mkdtemp(join(tmpdir(), "asw-lockstep-"));
  try {
    for (const dir of ["plugins/antigravity-swarm/scripts", "plugins/antigravity-swarm", "docs"]) {
      await mkdir(join(temp, dir), { recursive: true });
    }
    for (const file of [
      "package.json",
      "package-lock.json",
      "README.md",
      "README_KO.md",
      "plugins/antigravity-swarm/plugin.json",
      "plugins/antigravity-swarm/scripts/asw-statusline.mjs",
      "docs/RELEASE_CHECKLIST.md",
    ]) {
      await writeFile(join(temp, file), await readFile(join(repoRoot, file), "utf8"), "utf8");
    }
    const pluginPath = join(temp, "plugins/antigravity-swarm/plugin.json");
    const plugin = await readFile(pluginPath, "utf8");
    await writeFile(pluginPath, plugin.replace(/\"version\": \"[^\"]+\"/, "\"version\": \"9.9.9\""), "utf8");

    const drift = spawnSync("node", [lockstepPath, temp], { cwd: repoRoot, encoding: "utf8" });
    assert.notEqual(drift.status, 0);
    assert.match(drift.stderr, /version drift/i);
    assert.match(drift.stderr, /plugin\.json/);
  } finally {
    await rm(temp, { recursive: true, force: true });
  }
});

test("#release #human gated checklist documents command-backed preflight without publishing", async () => {
  const expectedVersion = await packageVersion();
  const checklist = await readFile(join(repoRoot, "docs", "RELEASE_CHECKLIST.md"), "utf8");
  assert.match(checklist, new RegExp(`antigravity-swarm@${expectedVersion.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}`));
  for (const command of [
    "npm test",
    "npm run pack:dry-run",
    "agy plugin validate plugins/antigravity-swarm",
    "npm view antigravity-swarm version",
    "node bin/antigravity-swarm.js --help",
    "node scripts/check-version-lockstep.mjs",
  ]) {
    assert.match(checklist, new RegExp(command.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")));
  }
  assert.match(checklist, /Do not run `npm publish`/i);
  assert.match(checklist, /manual publish command/i);
});

test("#redaction #statusline redacts common secret shapes from visible content", () => {
  const result = runNode(statuslinePath, {
    model: { display_name: "Gemini Bearer abc.def.secret" },
    context_window: { used_percentage: 12 },
    usage: { model_quota: [{ model: "sk-live_1234567890abcdef", remaining_percentage: 80 }] },
    vcs: { branch: "feature/ghp_1234567890abcdef1234567890abcdef1234", dirty: true },
  });

  assert.equal(result.status, 0, result.stderr);
  assert.doesNotMatch(result.stdout, /abc\.def\.secret|ghp_1234567890abcdef|sk-live_1234567890abcdef/);
  assert.match(result.stdout, /\[REDACTED(?:_TOKEN)?\]/);
});

test("#redaction #helper redacts bearer github slack api-key and key-value secrets deterministically", () => {
  const input = [
    "Authorization: Bearer abc.def.secret",
    "github=ghp_1234567890abcdef1234567890abcdef1234",
    "slack=xoxb-1234567890-abcdefSECRET",
    "api_key=live-secret-value",
    "password: hunter2",
    "token='opaque-token-value'",
    "secret=topsecret",
  ].join("\n");
  const output = redactSecrets(input);

  assert.doesNotMatch(output, /abc\.def\.secret|ghp_1234567890abcdef|xoxb-1234567890|live-secret-value|hunter2|opaque-token-value|topsecret/);
  assert.match(output, /Bearer \[REDACTED_TOKEN\]/);
  assert.match(output, /api_key=\[REDACTED\]/);
  assert.match(output, /password:\[REDACTED\]/);
});

test("#hooks #safe mode makes hook scripts no-op", () => {
  const env = { ASW_SAFE_MODE: "1" };
  assert.deepEqual(JSON.parse(runNode(hookPath, { prompt: "asw-plan ship" }, env).stdout), {});
  assert.deepEqual(JSON.parse(runNode(lspPath, { tool: "write_file" }, env).stdout), {});
  assert.deepEqual(JSON.parse(runNode(stopPath, { fullyIdle: false }, env).stdout), { decision: "" });
});

test("#hooks #fail open on malformed missing stale and misleading payloads", () => {
  assert.deepEqual(JSON.parse(runNode(hookPath, "{").stdout), {});
  assert.deepEqual(JSON.parse(runNode(hookPath, { unexpected: true }).stdout), {});
  assert.deepEqual(JSON.parse(runNode(hookPath, { transcriptPath: "/tmp/asw-missing-transcript.jsonl" }).stdout), {});
  assert.deepEqual(JSON.parse(runNode(stopPath, { fullyIdle: true, output: "success: background job still running" }).stdout), { decision: "" });
});

test("#hooks #natural ASW phrases route modes without code slash or acronym false positives", () => {
  const accepts = new Map([
    ["please asw plan this release", /ASW PLAN MODE ENABLED/],
    ["asw review the diff", /ASW REVIEW MODE ENABLED/],
    ["asw goal define evidence", /ASW GOAL MODE ENABLED/],
    ["asw start work .asw/plans/release.md", /ASW START-WORK MODE ENABLED/],
  ]);
  for (const [prompt, pattern] of accepts) {
    const output = JSON.parse(runNode(hookPath, { prompt }).stdout);
    assert.match(output.injectSteps[0].userMessage, pattern, prompt);
  }

  for (const prompt of [
    "what does ASW mean in anti-submarine warfare?",
    "do not leak passwords when rendering status",
    "mention `asw plan` in docs",
    "```\nasw review\n```",
    "/asw-plan should stay a slash command mention",
    "open docs/asw-plan.md",
  ]) {
    assert.deepEqual(JSON.parse(runNode(hookPath, { prompt }).stdout), {}, prompt);
  }
});

test("#lsp #diagnostic hook is explicit guidance no-op, not active diagnostics", async () => {
  const readme = await readFile(join(repoRoot, "README.md"), "utf8");
  const ko = await readFile(join(repoRoot, "README_KO.md"), "utf8");
  const manifest = JSON.parse(await readFile(join(repoRoot, "plugins", "antigravity-swarm", "hooks", "hooks.json"), "utf8"));
  const statusMessage = manifest["antigravity-swarm"].PostToolUse[0].hooks[0].statusMessage;

  assert.match(runNode(lspPath, { tool: "write_file", filePath: "broken.ts" }).stdout, /^\{\}$/);
  assert.match(readme, /diagnostics guidance hook/i);
  assert.match(readme, /does not run a language server/i);
  assert.match(ko, /진단 가이드 hook/i);
  assert.match(statusMessage, /guidance/i);
});
