import { existsSync } from "node:fs";
import { readdir, stat } from "node:fs/promises";
import { join } from "node:path";
import { copyTree, removeTree, rewriteInstalledHooks, writeSkillShims } from "./files.mjs";
import { installHud } from "./hud.mjs";
import { installPermissionProfile } from "./permissions.mjs";
import { defaultSettingsPath, defaultTarget, pluginName, pluginSource } from "./paths.mjs";
import {
  chooseHudColor,
  chooseInstallAction,
  choosePermissionProfile,
  paint,
  printMode,
  shouldPrompt,
  showHeader,
  showInstallSummary,
  withSpinner,
} from "./ui.mjs";

export async function runCommand(options) {
  if (!existsSync(pluginSource)) throw new Error(`Missing package plugin assets: ${pluginSource}`);
  if (options.command === "help") return help();
  if (options.command === "interactive") return interactive(options);
  if (options.command === "install") return install(options);
  if (options.command === "install-hud") return installHudWithHeader(options);
  if (options.command === "verify") return verify(options);
  if (options.command === "uninstall") return uninstall(options);
  throw new Error(`Unknown command: ${options.command}`);
}

async function interactive(options) {
  if (!shouldPrompt(options)) return install({ ...options, command: "install" });
  const action = await chooseInstallAction(options);
  if (action === "install-hud-full") {
    const hudColor = await chooseHudColor(options);
    const permissionProfile = options.permissionProfile || await choosePermissionProfile(options);
    return install({ ...options, command: "install", hud: true, hudColor, permissionProfile, forceTty: true });
  }
  if (action === "install-hud") {
    const hudColor = await chooseHudColor(options);
    return installHudWithHeader({ ...options, command: "install-hud", hudColor });
  }
  if (action === "verify") {
    console.log("Verify existing install selected. Run the verify command when the target already has ASW installed.");
    return;
  }
  const permissionProfile = options.permissionProfile || await choosePermissionProfile(options);
  return install({ ...options, command: "install", permissionProfile, forceTty: true });
}

export async function install(options) {
  showHeader(options);
  printMode(options);
  const destination = join(options.target, "plugins", pluginName);
  await withSpinner(options, "plugin assets", () => copyTree(pluginSource, destination, options));
  await withSpinner(options, "global skill shims", () => writeSkillShims(options));
  if (options.dryRun) {
    await installPermissionProfile(options);
    if (options.hud) await installHud(options);
    console.log(paint(options, "yellow", "DRY RUN complete: no files were written."));
    return;
  }
  await withSpinner(options, "hook paths", () => rewriteInstalledHooks(options));
  await installPermissionProfile(options);
  if (options.hud) await installHud(options);
  showInstallSummary(options, [
    `${paint(options, "green", "Ready")} plugin, hooks, and skills`,
    `${paint(options, "dim", "Try")} asw-plan → start-work → asw`,
  ]);
}

async function installHudWithHeader(options) {
  showHeader(options);
  printMode(options);
  return installHud(options);
}

export async function verify(options) {
  showHeader(options);
  printMode(options);
  const required = [
    join(options.target, "plugins", pluginName, "plugin.json"),
    join(options.target, "plugins", pluginName, "hooks", "hooks.json"),
    join(options.target, "plugins", pluginName, "scripts", "asw-hook.mjs"),
    join(options.target, "plugins", pluginName, "scripts", "asw-lsp-check.mjs"),
    join(options.target, "plugins", pluginName, "scripts", "asw-statusline.mjs"),
    join(options.target, "skills", "asw", "SKILL.md"),
    join(options.target, "skills", "asw-plan", "SKILL.md"),
    join(options.target, "skills", "asw-loop", "SKILL.md"),
    join(options.target, "skills", "asw-goal", "SKILL.md"),
  ];
  for (const path of required) await stat(path);
  console.log(paint(options, "green", "Verification passed."));
}

export async function uninstall(options) {
  showHeader(options);
  printMode(options);
  const names = await installedSkillNames(options);
  await removeTree(join(options.target, "plugins", pluginName), options);
  for (const name of names) await removeTree(join(options.target, "skills", name), options);
  console.log(paint(options, "green", options.dryRun ? "DRY RUN complete: no files were removed." : "Removed ASW files."));
}

async function installedSkillNames(options) {
  try {
    return await readdir(join(options.target, "plugins", pluginName, "skills"));
  } catch {
    return ["asw", "asw-plan", "asw-loop", "asw-goal", "asw-review"];
  }
}

function help() {
  console.log(`ASW

Usage:
  antigravity-swarm --interactive
  antigravity-swarm install [--target <dir>] [--dry-run] [--hud] [--hud-color <name>] [--settings-target <file>] [--permission-profile <safe|balanced|full|none>] [--force-permission] [--force-hud]
  antigravity-swarm install-hud [--target <dir>] [--hud-color <name>] [--settings-target <file>] [--force-hud]
  antigravity-swarm verify [--target <dir>]
  antigravity-swarm uninstall [--target <dir>] [--dry-run]

HUD colors:
  cyan, blue, teal, green, lavender, rose, gold, orange, slate, gray

Permission profiles:
  safe      least privilege / read-mostly (default for non-TTY installs)
  balanced  recommended ASW permissions with prompts for writes and shell
  full      broad tool access; use only when you trust the workspace
  none      install files but do not modify permission settings
  custom    future work; not implemented

Environment:
  ASW_PERMISSION_PROFILE=safe|balanced|full|none

Existing permission settings are preserved unless --force-permission is passed.

Default target:
  ${defaultTarget}

Default HUD settings:
  ${defaultSettingsPath}
`);
}
