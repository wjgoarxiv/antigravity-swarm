import assert from "node:assert/strict";
import { existsSync, statSync } from "node:fs";
import { spawnSync } from "node:child_process";
import test from "node:test";

const repoRoot = new URL("..", import.meta.url).pathname;

test("#cover #generator exists and can reproduce the ASW hero image", () => {
  assert.equal(existsSync(`${repoRoot}/generate_cover.py`), true);

  const result = spawnSync("python3", ["generate_cover.py", "--check"], {
    cwd: repoRoot,
    encoding: "utf8",
  });

  assert.equal(result.status, 0, result.stderr);
  assert.match(result.stdout, /antigravity-swarm/);
  assert.match(result.stdout, /2560x1280/);

  const cover = statSync(`${repoRoot}/cover.png`);
  assert.ok(cover.size > 2_500_000, "cover should be a full hero image, not a tiny placeholder");
});
