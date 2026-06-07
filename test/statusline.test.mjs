import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { join } from "node:path";
import test from "node:test";

const repoRoot = new URL("..", import.meta.url).pathname;
const statuslinePath = join(repoRoot, "plugins", "antigravity-swarm", "scripts", "asw-statusline.mjs");

test("#statusline #renders compact Antigravity CLI HUD text", () => {
  const result = spawnSync("node", [statuslinePath], {
    cwd: repoRoot,
    input: JSON.stringify({
      cwd: repoRoot,
      agent_state: "working",
      model: { display_name: "Gemini" },
      context_window: { used_percentage: 42.4 },
      subagents: [{ name: "asw-reviewer" }],
      background_tasks: [{ name: "npm test" }],
      vcs: { branch: "main", dirty: true },
    }),
    encoding: "utf8",
    env: { ...process.env, FORCE_COLOR: "0" },
  });

  assert.equal(result.status, 0, result.stderr);
  assert.match(result.stdout, /\[✨ASW v0\.2\.2\]/);
  assert.match(result.stdout, /ctx \[▉░\] 42%/);
  assert.match(result.stdout, /git main !/);
  assert.doesNotMatch(result.stdout, /5h|1w|\?/);
});

test("#statusline #renders visible ANSI output from Antigravity-shaped payload", () => {
  const result = spawnSync("node", [statuslinePath], {
    cwd: repoRoot,
    input: JSON.stringify({
      cwd: repoRoot,
      product: "antigravity-cli",
      version: "1.0.5",
      agent_state: "thinking",
      model: { display_name: "Gemini 3.5 Flash" },
      context_window: { used_percentage: 17, remaining_percentage: 83 },
      subagents: [{ name: "planner", status: "running" }],
      background_tasks: [{ name: "npm test", status: "running" }],
      terminal_width: 120,
    }),
    encoding: "utf8",
    env: { ...process.env, FORCE_COLOR: "1" },
  });

  assert.equal(result.status, 0, result.stderr);
  assert.match(result.stdout, /\x1b\[1;38;5;51m\[✨ASW v0\.2\.2\]\x1b\[0m/);
  assert.match(result.stdout, /ASW/);
  assert.match(result.stdout, /ctx \[▍░\] 17%/);
  assert.doesNotMatch(result.stdout, /5h|1w|\?/);
});

test("#statusline #renders ASW gauge format with selected palette and quotas", () => {
  const result = spawnSync("node", [statuslinePath], {
    cwd: repoRoot,
    input: JSON.stringify({
      version: "1.0.5",
      cwd: repoRoot,
      model: { display_name: "Gemini 3.5 Flash" },
      context_window: { used_percentage: 9, context_window_size: 1_000_000 },
      quota: {
        five_hour: { used_percentage: 4, reset_in_seconds: 8100 },
        weekly: { used_percentage: 35, reset_in_seconds: 280800 },
      },
      vcs: { branch: "main", dirty: false, added: 3 },
    }),
    encoding: "utf8",
    env: { ...process.env, FORCE_COLOR: "1", ASW_HUD_COLOR: "rose" },
  });

  assert.equal(result.status, 0, result.stderr);
  assert.match(result.stdout, /\[✨ASW v0\.2\.2\]/);
  assert.match(result.stdout, /G-f 3\.5/);
  assert.match(result.stdout, /ctx \[▎░\] 9%\/1000k/);
  assert.match(result.stdout, /5h \[▏░\] 4% ↻2h15m/);
  assert.match(result.stdout, /1w \[▊░\] 35% ↻3d6h/);
  assert.match(result.stdout, /git main \+3 ✓/);
  assert.match(result.stdout, /\x1b\[1;38;5;213m/);
});

test("#statusline #applies selected HUD color to every visible segment", () => {
  const result = spawnSync("node", [statuslinePath], {
    cwd: repoRoot,
    input: JSON.stringify({
      model: { display_name: "Gemini 3.5 Flash" },
      context_window: { used_percentage: 4, context_window_size: 1_049_000 },
      vcs: { branch: "main", dirty: false, added: 3 },
    }),
    encoding: "utf8",
    env: { ...process.env, FORCE_COLOR: "1", ASW_HUD_COLOR: "rose" },
  });

  assert.equal(result.status, 0, result.stderr);
  assert.match(result.stdout, /\x1b\[1;38;5;213m\[✨ASW v0\.2\.2\]\x1b\[0m/);
  assert.match(result.stdout, /\x1b\[1;38;5;213mG-f 3\.5\x1b\[0m/);
  assert.match(result.stdout, /\x1b\[1;38;5;213mctx \[▏░\] 4%\/1049k\x1b\[0m/);
  assert.match(result.stdout, /\x1b\[1;38;5;213mgit main \+3 ✓\x1b\[0m/);
});

test("#statusline #preserves Gemini effort tier in compact model label", () => {
  const result = spawnSync("node", [statuslinePath], {
    cwd: repoRoot,
    input: JSON.stringify({
      model: { display_name: "Gemini 3.5 Flash (Medium)" },
      context_window: { used_percentage: 4, context_window_size: 1_049_000 },
    }),
    encoding: "utf8",
    env: { ...process.env, FORCE_COLOR: "0" },
  });

  assert.equal(result.status, 0, result.stderr);
  assert.match(result.stdout, /G-f \(Medium\) 3\.5/);
});

test("#statusline #does not render midrange context usage as a full gauge", () => {
  const result = spawnSync("node", [statuslinePath], {
    cwd: repoRoot,
    input: JSON.stringify({
      model: { display_name: "GPT-OSS 120B (Medium)" },
      context_window: { used_percentage: 55, context_window_size: 131_000 },
    }),
    encoding: "utf8",
    env: { ...process.env, FORCE_COLOR: "0" },
  });

  assert.equal(result.status, 0, result.stderr);
  assert.match(result.stdout, /GPT-OSS 120B \(Medium\)/);
  assert.match(result.stdout, /ctx \[█▏\] 55%\/131k/);
  assert.doesNotMatch(result.stdout, /ctx \[██\] 55%\/131k/);
});

test("#statusline #renders compact model quota rows from usage-shaped payload", () => {
  const result = spawnSync("node", [statuslinePath], {
    cwd: repoRoot,
    input: JSON.stringify({
      model: { display_name: "Gemini 3.5 Flash (Medium)" },
      context_window: { used_percentage: 4, context_window_size: 1_049_000 },
      usage: {
        model_quota: [
          { model: "Gemini 3.5 Flash (Medium)", remaining_percentage: 60, refreshes_in_seconds: 599640 },
          { model: "Gemini 3.5 Flash (High)", remaining_percentage: 60, refreshes_in_seconds: 599640 },
          { model: "Gemini 3.5 Flash (Low)", remaining_percentage: 60, refreshes_in_seconds: 599640 },
          { model: "Gemini 3.1 Pro (Low)", remaining_percentage: 60, refreshes_in_seconds: 599640 },
        ],
      },
    }),
    encoding: "utf8",
    env: { ...process.env, FORCE_COLOR: "0" },
  });

  assert.equal(result.status, 0, result.stderr);
  assert.match(result.stdout, /mq /);
  assert.match(result.stdout, /G-f\(M\) \[█░\] 60%/);
  assert.match(result.stdout, /G-f\(H\) 60%/);
  assert.match(result.stdout, /G-f\(L\) 60%/);
  assert.match(result.stdout, /G-p\(L\) 60%/);
  assert.match(result.stdout, /↻6d22h/);
});
