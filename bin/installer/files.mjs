import { copyFile, mkdir, readdir, readFile, rm, writeFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { pluginName, pluginSource, root } from "./paths.mjs";

export async function listFiles(dir, base = dir) {
  const entries = await readdir(dir, { withFileTypes: true });
  const files = [];
  for (const entry of entries) {
    const path = join(dir, entry.name);
    if (entry.isDirectory()) {
      files.push(...await listFiles(path, base));
    } else if (entry.isFile()) {
      files.push(path.slice(base.length + 1));
    }
  }
  return files.sort();
}

export async function copyTree(src, dest, options) {
  const files = await listFiles(src);
  for (const file of files) {
    const from = join(src, file);
    const to = join(dest, file);
    if (options.dryRun) {
      console.log(`copy ${from.replace(root + "/", "")} -> ${to}`);
      continue;
    }
    await mkdir(dirname(to), { recursive: true });
    await copyFile(from, to);
  }
}

export async function writeSkillShims(options) {
  const sourceSkills = join(pluginSource, "skills");
  const names = await readdir(sourceSkills);
  for (const name of names) {
    const from = join(sourceSkills, name, "SKILL.md");
    const to = join(options.target, "skills", name, "SKILL.md");
    if (options.dryRun) {
      console.log(`copy plugins/${pluginName}/skills/${name}/SKILL.md -> ${to}`);
      continue;
    }
    await mkdir(dirname(to), { recursive: true });
    await copyFile(from, to);
  }
}

export async function rewriteInstalledHooks(options) {
  const installedPlugin = join(options.target, "plugins", pluginName);
  const hooksPath = join(installedPlugin, "hooks", "hooks.json");
  const manifest = JSON.parse(await readFile(hooksPath, "utf8"));
  const replacements = new Map([
    ["${PLUGIN_ROOT}/scripts/asw-hook.mjs", join(installedPlugin, "scripts", "asw-hook.mjs")],
    ["${PLUGIN_ROOT}/scripts/asw-lsp-check.mjs", join(installedPlugin, "scripts", "asw-lsp-check.mjs")],
    ["${PLUGIN_ROOT}/scripts/asw-stop-check.mjs", join(installedPlugin, "scripts", "asw-stop-check.mjs")],
  ]);
  for (const hookConfig of Object.values(manifest)) {
    rewriteHookConfig(hookConfig, replacements);
  }
  await writeFile(hooksPath, `${JSON.stringify(manifest, null, 2)}\n`, "utf8");
}

function rewriteHookConfig(hookConfig, replacements) {
  for (const [eventName, handlers] of Object.entries(hookConfig)) {
    if (eventName === "enabled" || !Array.isArray(handlers)) continue;
    for (const handler of handlers) {
      rewriteHandler(handler, replacements);
    }
  }
}

function rewriteHandler(handler, replacements) {
  if (typeof handler.command === "string") {
    handler.command = rewriteCommand(handler.command, replacements);
  }
  if (Array.isArray(handler.hooks)) {
    handler.hooks.forEach((nested) => rewriteHandler(nested, replacements));
  }
}

function rewriteCommand(value, replacements) {
  let command = value;
  for (const [needle, replacement] of replacements) {
    command = command.replace(needle, replacement);
  }
  return command;
}

export async function removeTree(path, options) {
  if (options.dryRun) {
    console.log(`remove ${path}`);
    return;
  }
  await rm(path, { recursive: true, force: true });
}
