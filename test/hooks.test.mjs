import assert from "node:assert/strict";
import { mkdtemp, rm, writeFile, readFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { spawnSync } from "node:child_process";
import test from "node:test";

const repoRoot = new URL("..", import.meta.url).pathname;
const hookPath = join(repoRoot, "plugins", "antigravity-swarm", "scripts", "asw-hook.mjs");
const lspPath = join(repoRoot, "plugins", "antigravity-swarm", "scripts", "asw-lsp-check.mjs");

function runHook(script, payload, args = []) {
  return spawnSync("node", [script, ...args], {
    cwd: repoRoot,
    input: JSON.stringify(payload),
    encoding: "utf8",
    env: { ...process.env, FORCE_COLOR: "0" },
  });
}

test("#asw hook #injects plan directive for Antigravity PreInvocation payload", () => {
  const result = runHook(hookPath, {
    invocationNum: 1,
    initialNumSteps: 0,
    workspacePaths: [repoRoot],
    prompt: "asw-plan this migration",
  });

  assert.equal(result.status, 0, result.stderr);
  const output = JSON.parse(result.stdout);
  assert.equal(output.injectSteps.length, 1);
  assert.match(output.injectSteps[0].userMessage, /ASW PLAN MODE ENABLED/);
  assert.match(output.injectSteps[0].userMessage, /Antigravity CLI/);
  assert.match(output.injectSteps[0].userMessage, /\.omo\/plans\/<slug>\.md/);
  assert.match(output.injectSteps[0].userMessage, /## TODOs/);
  assert.match(output.injectSteps[0].userMessage, /Next: start-work <plan-name>/);
  assert.doesNotMatch(output.injectSteps[0].userMessage, /Let me know if you would like to proceed/i);
});

test("#asw hook #injects loop directive for asw and ulw compatibility aliases", () => {
  for (const prompt of ["asw fix this", "ulw fix this"]) {
    const result = runHook(hookPath, { prompt, workspacePaths: [repoRoot] });
    assert.equal(result.status, 0, result.stderr);
    const output = JSON.parse(result.stdout);
    assert.match(output.injectSteps[0].userMessage, /ASW LOOP MODE ENABLED/);
  }
});

test("#asw hook #injects goal directive for durable goal alias", () => {
  const result = runHook(hookPath, { prompt: "asw-goal define evidence criteria", workspacePaths: [repoRoot] });

  assert.equal(result.status, 0, result.stderr);
  const output = JSON.parse(result.stdout);
  assert.match(output.injectSteps[0].userMessage, /ASW GOAL MODE ENABLED/);
  assert.match(output.injectSteps[0].userMessage, /success criteria/);
});

test("#asw hook #injects start-work directive for plan execution aliases", () => {
  for (const prompt of ["start-work asw-v021", "asw-start-work .omo/plans/asw-v021.md"]) {
    const result = runHook(hookPath, { prompt, workspacePaths: [repoRoot] });
    assert.equal(result.status, 0, result.stderr);
    const output = JSON.parse(result.stdout);
    assert.match(output.injectSteps[0].userMessage, /ASW START-WORK MODE ENABLED/);
    assert.match(output.injectSteps[0].userMessage, /ORCHESTRATION COMPLETE/);
    assert.match(output.injectSteps[0].userMessage, /first unchecked top-level checkbox/);
  }
});

test("#asw hook #does not treat identifier-like start-work terms as aliases", () => {
  const result = runHook(hookPath, { prompt: "rename start-work_helper.mjs" });

  assert.equal(result.status, 0, result.stderr);
  assert.deepEqual(JSON.parse(result.stdout), {});
});

test("#asw hook #injects cleanup directive for AI slop removal aliases", () => {
  for (const prompt of ["asw-remove-ai-slops clean the diff", "asw-cleanup remove obvious AI comments"]) {
    const result = runHook(hookPath, { prompt, workspacePaths: [repoRoot] });
    assert.equal(result.status, 0, result.stderr);
    const output = JSON.parse(result.stdout);
    assert.match(output.injectSteps[0].userMessage, /ASW CLEANUP MODE ENABLED/);
    assert.match(output.injectSteps[0].userMessage, /Preserve behavior/);
  }
});

test("#asw hook #detects alias from Antigravity docs-shaped PreInvocation transcript", async () => {
  const dir = await mkdtemp(join(tmpdir(), "asw-transcript-"));
  try {
    const transcriptPath = join(dir, "transcript.jsonl");
    await writeFile(
      transcriptPath,
      [
        JSON.stringify({ role: "user", text: "ordinary setup" }),
        JSON.stringify({ type: "message", role: "user", content: [{ type: "text", text: "please asw-plan this port" }] }),
      ].join("\n"),
      "utf8",
    );

    const result = runHook(hookPath, {
      invocationNum: 3,
      initialNumSteps: 10,
      conversationId: "ec33ebf9-0cba-4100-8142-c61503f6c587",
      workspacePaths: [repoRoot],
      transcriptPath,
      artifactDirectoryPath: dir,
    });

    assert.equal(result.status, 0, result.stderr);
    assert.match(JSON.parse(result.stdout).injectSteps[0].userMessage, /ASW PLAN MODE ENABLED/);
  } finally {
    await rm(dir, { recursive: true, force: true });
  }
});

test("#asw hook #stays quiet for identifier-like terms and malformed stdin", () => {
  const identifier = runHook(hookPath, { prompt: "rename asw_helper.mjs" });
  assert.equal(identifier.status, 0, identifier.stderr);
  assert.deepEqual(JSON.parse(identifier.stdout), {});

  const malformed = spawnSync("node", [hookPath], {
    cwd: repoRoot,
    input: "{",
    encoding: "utf8",
  });
  assert.equal(malformed.status, 0, malformed.stderr);
  assert.deepEqual(JSON.parse(malformed.stdout), {});
});

test("#lsp hook #returns empty Antigravity JSON object and hook manifest wires PostToolUse", async () => {
  const result = runHook(lspPath, {
    stepIdx: 2,
    workspacePaths: [repoRoot],
    error: "",
  });
  assert.equal(result.status, 0, result.stderr);
  assert.deepEqual(JSON.parse(result.stdout), {});

  const manifest = JSON.parse(await readFile(join(repoRoot, "plugins", "antigravity-swarm", "hooks", "hooks.json"), "utf8"));
  assert.ok(manifest["antigravity-swarm"].PreInvocation);
  assert.match(manifest["antigravity-swarm"].PreInvocation[0].statusMessage, /ASW.*alias/i);
  const matcher = manifest["antigravity-swarm"].PostToolUse[0].matcher;
  assert.match(matcher, /write_to_file/);
  assert.match(matcher, /multi_replace_file_content/);
  assert.match(matcher, /write_file/);
  assert.match(matcher, /replace_file_content/);
  assert.match(matcher, /run_command/);
  assert.match(manifest["antigravity-swarm"].PostToolUse[0].hooks[0].statusMessage, /ASW.*diagnostics/i);
  assert.match(manifest["antigravity-swarm"].Stop[0].statusMessage, /ASW.*continuation/i);
});
