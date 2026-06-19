import assert from "node:assert/strict";
import { access, constants } from "node:fs/promises";
import { mkdir, mkdtemp, readFile, rm, stat, writeFile } from "node:fs/promises";
import { homedir } from "node:os";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { spawnSync } from "node:child_process";
import test from "node:test";

const repoRoot = new URL("..", import.meta.url).pathname;
const binPath = join(repoRoot, "bin", "antigravity-swarm.js");
const defaultAgyConfigRoot = join(homedir(), ".gemini", "config");

function runCli(args, options = {}) {
  return spawnSync("node", [binPath, ...args], {
    cwd: repoRoot,
    encoding: "utf8",
    input: options.input,
    env: { ...process.env, FORCE_COLOR: "0", ...options.env },
  });
}

test("#installer dry-run #does not write target and prints planned Antigravity paths", async () => {
  const target = await mkdtemp(join(tmpdir(), "asw-dry-run-"));
  await rm(target, { recursive: true, force: true });

  const result = runCli(["--dry-run", "install", "--target", target]);

  assert.equal(result.status, 0, result.stderr);
  assert.match(result.stdout, /\bASW\b/);
  assert.match(result.stdout, /DRY RUN/);
  assert.match(result.stdout, /plugins\/antigravity-swarm/);
  assert.match(result.stdout, /skills\/asw-plan/);
  await assert.rejects(stat(target), /ENOENT/);
});

test("#installer permissions #help documents permission profile selection", () => {
  const result = runCli(["--help"]);

  assert.equal(result.status, 0, result.stderr);
  assert.match(result.stdout, /--permission-profile <safe\|balanced\|full\|none>/);
  assert.match(result.stdout, /ASW_PERMISSION_PROFILE/);
  assert.match(result.stdout, /--force-permission/);
  assert.match(result.stdout, /custom.*future work/i);
});

test("#installer permissions #dry-run prints safe profile target and writes nothing", async () => {
  const home = await mkdtemp(join(tmpdir(), "asw-perm-dry-"));
  const target = join(home, ".gemini", "config");
  const settingsTarget = join(home, ".gemini", "antigravity-cli", "settings.json");
  try {
    const result = runCli(["--dry-run", "install", "--target", target, "--settings-target", settingsTarget, "--permission-profile", "safe"]);

    assert.equal(result.status, 0, result.stderr);
    assert.match(result.stdout, /permission profile safe/i);
    assert.match(result.stdout, new RegExp(settingsTarget.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")));
    await assert.rejects(stat(target), /ENOENT/);
    await assert.rejects(stat(settingsTarget), /ENOENT/);
  } finally {
    await rm(home, { recursive: true, force: true });
  }
});

test("#installer permissions #writes supported profiles and schema-compatible keys", async () => {
  const supportedKeys = new Set(["read", "edit", "glob", "grep", "list", "bash", "task", "external_directory", "todowrite", "question", "webfetch", "websearch", "lsp", "doom_loop", "skill"]);
  for (const profile of ["safe", "balanced", "full"]) {
    const home = await mkdtemp(join(tmpdir(), `asw-perm-${profile}-`));
    const target = join(home, ".gemini", "config");
    const settingsTarget = join(home, ".gemini", "antigravity-cli", "settings.json");
    try {
      const result = runCli(["install", "--target", target, "--settings-target", settingsTarget, "--permission-profile", profile]);
      assert.equal(result.status, 0, result.stderr);
      assert.match(result.stdout, new RegExp(`permission profile ${profile}`, "i"));
      const settings = JSON.parse(await readFile(settingsTarget, "utf8"));
      assert.equal(settings.$schema, "https://opencode.ai/config.json");
      if (profile === "full") {
        assert.equal(settings.permission, "allow");
      } else {
        for (const key of Object.keys(settings.permission)) assert.equal(supportedKeys.has(key), true, `${key} is not an OpenCode permission key`);
        assert.equal(settings.permission.read, "allow");
        assert.equal(settings.permission.glob, "allow");
        assert.equal(settings.permission.grep, "allow");
        assert.equal(settings.permission.edit, profile === "safe" ? "ask" : "ask");
        assert.equal(settings.permission.bash, "ask");
      }
    } finally {
      await rm(home, { recursive: true, force: true });
    }
  }
});

test("#installer permissions #none profile skips settings permission changes", async () => {
  const home = await mkdtemp(join(tmpdir(), "asw-perm-none-"));
  const target = join(home, ".gemini", "config");
  const settingsTarget = join(home, ".gemini", "antigravity-cli", "settings.json");
  try {
    const result = runCli(["install", "--target", target, "--settings-target", settingsTarget, "--permission-profile", "none"]);

    assert.equal(result.status, 0, result.stderr);
    assert.match(result.stdout, /permission profile none/i);
    await assert.rejects(readFile(settingsTarget, "utf8"), /ENOENT/);
  } finally {
    await rm(home, { recursive: true, force: true });
  }
});

test("#installer permissions #defaults from non-TTY safe and env fallback", async () => {
  const cases = [
    { name: "default", args: [], env: {}, expected: "safe" },
    { name: "env", args: [], env: { ASW_PERMISSION_PROFILE: "balanced" }, expected: "balanced" },
  ];
  for (const scenario of cases) {
    const home = await mkdtemp(join(tmpdir(), `asw-perm-${scenario.name}-`));
    const target = join(home, ".gemini", "config");
    const settingsTarget = join(home, ".gemini", "antigravity-cli", "settings.json");
    try {
      const result = runCli(["install", "--target", target, "--settings-target", settingsTarget, ...scenario.args], { env: scenario.env });
      assert.equal(result.status, 0, result.stderr);
      assert.match(result.stdout, new RegExp(`permission profile ${scenario.expected}`, "i"));
      const settings = JSON.parse(await readFile(settingsTarget, "utf8"));
      assert.equal(settings.permission.read, "allow");
    } finally {
      await rm(home, { recursive: true, force: true });
    }
  }
});

test("#installer permissions #preserves existing permission unless force is explicit", async () => {
  const home = await mkdtemp(join(tmpdir(), "asw-perm-preserve-"));
  const target = join(home, ".gemini", "config");
  const settingsTarget = join(home, ".gemini", "antigravity-cli", "settings.json");
  try {
    await mkdir(join(home, ".gemini", "antigravity-cli"), { recursive: true });
    await writeFile(settingsTarget, JSON.stringify({ permission: { bash: "deny" }, existing: true }, null, 2), "utf8");
    const preserve = runCli(["install", "--target", target, "--settings-target", settingsTarget, "--permission-profile", "balanced"]);
    assert.equal(preserve.status, 0, preserve.stderr);
    assert.match(preserve.stdout, /preserve existing permission/i);
    assert.deepEqual(JSON.parse(await readFile(settingsTarget, "utf8")).permission, { bash: "deny" });

    const overwrite = runCli(["install", "--target", target, "--settings-target", settingsTarget, "--permission-profile", "balanced", "--force-permission"]);
    assert.equal(overwrite.status, 0, overwrite.stderr);
    assert.match(overwrite.stdout, /permission profile balanced/i);
    assert.equal(JSON.parse(await readFile(settingsTarget, "utf8")).permission.read, "allow");
  } finally {
    await rm(home, { recursive: true, force: true });
  }
});

test("#installer permissions #invalid profile fails clearly", () => {
  const result = runCli(["install", "--permission-profile", "root"]);

  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /Invalid permission profile: root/);
  assert.match(result.stderr, /safe, balanced, full, none/);
});

test("#installer help #uses Antigravity CLI global config root", () => {
  const result = runCli(["--help"]);

  assert.equal(result.status, 0, result.stderr);
  assert.match(result.stdout, new RegExp(defaultAgyConfigRoot.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")));
  assert.doesNotMatch(result.stdout, /antigravity-cli\/plugins|antigravity-cli\/skills/);
  assert.match(result.stdout, /Default HUD settings/);
});

test("#installer install+verify #copies plugin skills hooks and manifest", async () => {
  const target = await mkdtemp(join(tmpdir(), "asw-install-"));
  try {
    const settingsTarget = join(target, "settings.json");
    const install = runCli(["install", "--target", target, "--settings-target", settingsTarget, "--permission-profile", "none"]);
    assert.equal(install.status, 0, install.stderr);
    assert.match(install.stdout, /ASW\s+v0\.2\.4/);
    assert.match(install.stdout, /ANTIGRAVITY SWARM/);
    assert.match(install.stdout, /Hooks · Skills · HUD · Agents/);
    assert.match(install.stdout, /Install target/);
    assert.match(install.stdout, /◆ Package/);
    assert.match(install.stdout, /◆ Install/);
    assert.match(install.stdout, /◇ plugin assets/);
    assert.match(install.stdout, /✓ plugin assets/);
    assert.match(install.stdout, /✓ global skill shims/);
    assert.match(install.stdout, /✓ hook paths/);
    assert.match(install.stdout, /Ready/);
    assert.match(install.stdout, /asw-plan/);
    assert.doesNotMatch(install.stdout, /│ ASW Antigravity Swarm\s+│/);

    const verify = runCli(["verify", "--target", target]);
    assert.equal(verify.status, 0, verify.stderr);
    assert.match(verify.stdout, /verification passed/i);

    const manifest = JSON.parse(
      await readFile(join(target, "plugins", "antigravity-swarm", "plugin.json"), "utf8"),
    );
    assert.equal(manifest.name, "antigravity-swarm");
    assert.equal(manifest.hooks, "./hooks/hooks.json");
    assert.equal(manifest.skills, "./skills");

    const hooks = JSON.parse(
      await readFile(join(target, "plugins", "antigravity-swarm", "hooks", "hooks.json"), "utf8"),
    );
    assert.match(
      hooks["antigravity-swarm"].PreInvocation[0].command,
      new RegExp(`${target.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}.+asw-hook\\.mjs`),
    );

    const skill = await readFile(join(target, "skills", "asw-plan", "SKILL.md"), "utf8");
    assert.match(skill, /Antigravity Swarm Plan/);

    const goalSkill = await readFile(join(target, "skills", "asw-goal", "SKILL.md"), "utf8");
    assert.match(goalSkill, /observable evidence/);

    const agent = await readFile(join(target, "plugins", "antigravity-swarm", "agents", "asw-reviewer.toml"), "utf8");
    assert.match(agent, /ASW APPROVED/);
  } finally {
    await rm(target, { recursive: true, force: true });
  }
});

test("#installer hud #merges statusLine without clobbering other settings", async () => {
  const home = await mkdtemp(join(tmpdir(), "asw-hud-"));
  const target = join(home, ".gemini", "config");
  const settingsTarget = join(home, ".gemini", "antigravity-cli", "settings.json");
  try {
    const install = runCli(["install", "--target", target, "--hud", "--settings-target", settingsTarget]);
    assert.equal(install.status, 0, install.stderr);
    assert.match(install.stdout, /✓ HUD statusline/);

    const settings = JSON.parse(await readFile(settingsTarget, "utf8"));
    assert.equal(settings.statusLine.type, "command");
    assert.match(settings.statusLine.command, /\.gemini\/antigravity-cli\/asw-statusline\.sh$/);
    await access(settings.statusLine.command, constants.X_OK);
    await stat(join(target, "plugins", "antigravity-swarm", "scripts", "asw-statusline.mjs"));

    const conflict = runCli(["install-hud", "--target", target, "--settings-target", settingsTarget]);
    assert.equal(conflict.status, 0, conflict.stderr);
  } finally {
    await rm(home, { recursive: true, force: true });
  }
});

test("#installer interactive #renders menu and installs HUD from a numeric choice", async () => {
  const home = await mkdtemp(join(tmpdir(), "asw-interactive-"));
  const target = join(home, ".gemini", "config");
  const settingsTarget = join(home, ".gemini", "antigravity-cli", "settings.json");
  try {
    const result = runCli(["--interactive", "--target", target, "--settings-target", settingsTarget], {
      input: "2\n6\n1\n",
      env: { ASW_TEST_TTY: "1" },
    });

    assert.equal(result.status, 0, result.stderr);
    assert.match(result.stdout, /\bASW\b/);
    assert.equal(result.stdout.includes("___      _____"), false);
    assert.match(result.stdout, /ANTIGRAVITY SWARM/);
    assert.match(result.stdout, /◆ Package/);
    assert.match(result.stdout, /╭/);
    assert.match(result.stdout, /02\s+Install with HUD/);
    assert.match(result.stdout, /install with HUD/i);
    assert.match(result.stdout, /HUD color/i);
    assert.match(result.stdout, /rose/i);
    assert.match(result.stdout, /Permission profile/);
    assert.match(result.stdout, /safe\s+least privilege/);
    assert.match(result.stdout, /◐ plugin assets/);
    assert.match(result.stdout, /✓ plugin assets/);
    assert.match(result.stdout, /Ready plugin, hooks, and skills/);

    const settings = JSON.parse(await readFile(settingsTarget, "utf8"));
    assert.match(settings.statusLine.command, /asw-statusline\.sh$/);
    assert.equal(settings.permission.read, "allow");
    assert.equal(settings.permission.edit, "ask");
    const wrapper = await readFile(settings.statusLine.command, "utf8");
    assert.match(wrapper, /ASW_HUD_COLOR='rose'/);
  } finally {
    await rm(home, { recursive: true, force: true });
  }
});

test("#installer interactive #renders ASW title logo and polished install cockpit", async () => {
  const home = await mkdtemp(join(tmpdir(), "asw-interactive-logo-"));
  const target = join(home, ".gemini", "config");
  const settingsTarget = join(home, ".gemini", "antigravity-cli", "settings.json");
  try {
    const result = runCli(["--interactive", "--target", target, "--settings-target", settingsTarget], {
      input: "1\n4\n",
      env: { ASW_TEST_TTY: "1" },
    });

    assert.equal(result.status, 0, result.stderr);
    assert.match(result.stdout, /█████╗ ███████╗██╗\s+██╗/);
    assert.match(result.stdout, /ANTIGRAVITY SWARM/);
    assert.match(result.stdout, /install cockpit/i);
    assert.match(result.stdout, /Target/);
    assert.match(result.stdout, /Target/);
    assert.match(result.stdout, /asw-interactive-logo-[^/]+\/\.gemini\/config/);
    assert.match(result.stdout, /01\s+Install plugin \+ skills/);
    assert.match(result.stdout, /04\s+Verify existing install/);
    assert.doesNotMatch(result.stdout, /│ ASW Antigravity Swarm\s+│/);
    for (const line of result.stdout.split(/\r?\n/).filter((value) => value.startsWith("│"))) {
      assert.ok(line.length <= 80, `installer panel line is too wide: ${line}`);
    }
  } finally {
    await rm(home, { recursive: true, force: true });
  }
});

test("#installer interactive #renders HUD color choices with visible ANSI swatches", async () => {
  const home = await mkdtemp(join(tmpdir(), "asw-color-menu-"));
  const target = join(home, ".gemini", "config");
  const settingsTarget = join(home, ".gemini", "antigravity-cli", "settings.json");
  try {
    const result = runCli(["--interactive", "--target", target, "--settings-target", settingsTarget], {
      input: "3\n\n",
      env: { ASW_TEST_TTY: "1", FORCE_COLOR: "1" },
    });

    assert.equal(result.status, 0, result.stderr);
    assert.match(result.stdout, /HUD color/);
    assert.match(result.stdout, /\x1b\[1;38;5;51m■\x1b\[0m\s+cyan/);
    assert.match(result.stdout, /\x1b\[1;38;5;213m■\x1b\[0m\s+rose/);
    assert.match(result.stdout, /\x1b\[1;38;5;245m■\x1b\[0m\s+gray/);
    assert.match(result.stdout, /current/);
  } finally {
    await rm(home, { recursive: true, force: true });
  }
});

test("#installer interactive #keeps HUD color menu readable without ANSI", async () => {
  const home = await mkdtemp(join(tmpdir(), "asw-color-menu-plain-"));
  const target = join(home, ".gemini", "config");
  const settingsTarget = join(home, ".gemini", "antigravity-cli", "settings.json");
  try {
    const result = runCli(["--interactive", "--target", target, "--settings-target", settingsTarget], {
      input: "3\n\n",
      env: { ASW_TEST_TTY: "1", FORCE_COLOR: "0" },
    });

    assert.equal(result.status, 0, result.stderr);
    assert.match(result.stdout, /■ cyan/);
    assert.match(result.stdout, /■ rose/);
    assert.match(result.stdout, /current/);
    assert.doesNotMatch(result.stdout, /\x1b\[/);
  } finally {
    await rm(home, { recursive: true, force: true });
  }
});
