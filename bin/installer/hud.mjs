import { chmod, mkdir, readFile, stat, writeFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { copyTree, rewriteInstalledHooks } from "./files.mjs";
import { pluginName, pluginSource } from "./paths.mjs";
import { hudColors, paint } from "./ui.mjs";

export async function installHud(options) {
  const installedPlugin = join(options.target, "plugins", pluginName);
  const statusScript = join(installedPlugin, "scripts", "asw-statusline.mjs");
  const settingsPath = options.settingsTarget;
  const wrapperPath = join(dirname(settingsPath), "asw-statusline.sh");
  const statusLine = { type: "command", command: wrapperPath };

  if (options.dryRun) {
    console.log(`ensure ${statusScript}`);
    console.log(`write ${wrapperPath}`);
    console.log(`merge statusLine command into ${settingsPath}`);
    return;
  }

  await ensurePluginInstalled(statusScript, installedPlugin, options);
  await writeStatusWrapper(wrapperPath, statusScript, options.hudColor);
  const settings = await readSettings(settingsPath);
  assertCanWriteStatusLine(settings, statusLine, options);
  settings.statusLine = statusLine;
  await mkdir(dirname(settingsPath), { recursive: true });
  await writeFile(settingsPath, `${JSON.stringify(settings, null, 2)}\n`, "utf8");
  console.log(`${paint(options, "green", "✓")} HUD statusline ${paint(options, "dim", settingsPath)}`);
}

async function ensurePluginInstalled(statusScript, installedPlugin, options) {
  try {
    await stat(statusScript);
  } catch (error) {
    if (error.code !== "ENOENT") throw error;
    await copyTree(pluginSource, installedPlugin, options);
    await rewriteInstalledHooks(options);
  }
}

async function writeStatusWrapper(wrapperPath, statusScript, hudColor) {
  const color = hudColors.includes(hudColor) ? hudColor : "cyan";
  const body = [
    "#!/bin/sh",
    `ASW_HUD_COLOR='${color}'`,
    "export ASW_HUD_COLOR",
    `exec node "${statusScript}"`,
    "",
  ].join("\n");
  await mkdir(dirname(wrapperPath), { recursive: true });
  await writeFile(wrapperPath, body, "utf8");
  await chmod(wrapperPath, 0o755);
}

async function readSettings(settingsPath) {
  try {
    return JSON.parse(await readFile(settingsPath, "utf8"));
  } catch (error) {
    if (error.code === "ENOENT") return {};
    throw new Error(`Cannot read settings JSON at ${settingsPath}: ${error.message}`);
  }
}

function assertCanWriteStatusLine(settings, statusLine, options) {
  const current = settings.statusLine;
  if (current && JSON.stringify(current) !== JSON.stringify(statusLine) && !options.forceHud) {
    throw new Error(`settings.json already has a different statusLine. Re-run with --force-hud to replace it: ${options.settingsTarget}`);
  }
}
