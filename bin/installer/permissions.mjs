import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname } from "node:path";
import { paint } from "./ui.mjs";

export const permissionProfileNames = ["safe", "balanced", "full", "none"];

export function normalizePermissionProfile(value) {
  const profile = String(value ?? "").trim().toLowerCase();
  if (!profile) return "";
  if (permissionProfileNames.includes(profile)) return profile;
  if (profile === "custom") {
    throw new Error("Permission profile custom is future work; supported profiles: safe, balanced, full, none");
  }
  throw new Error(`Invalid permission profile: ${profile}. Supported profiles: safe, balanced, full, none`);
}

export async function installPermissionProfile(options) {
  const profile = options.permissionProfile || "safe";
  const settingsPath = options.settingsTarget;
  if (profile === "none") {
    console.log(`permission profile none: no permission settings will be written to ${settingsPath}`);
    return;
  }

  const settings = await readSettings(settingsPath);
  if (settings.permission !== undefined && !options.forcePermission) {
    console.log(`preserve existing permission in ${settingsPath}; selected permission profile ${profile} requires --force-permission to overwrite`);
    return;
  }

  const warning = profile === "full" ? " (broad tool access)" : "";
  if (options.dryRun) {
    console.log(`write permission profile ${profile}${warning} to ${settingsPath}`);
    return;
  }

  settings.$schema ??= "https://opencode.ai/config.json";
  settings.permission = permissionFor(profile);
  await mkdir(dirname(settingsPath), { recursive: true });
  await writeFile(settingsPath, `${JSON.stringify(settings, null, 2)}\n`, "utf8");
  console.log(`${paint(options, profile === "full" ? "yellow" : "green", "✓")} permission profile ${profile}${warning} ${paint(options, "dim", settingsPath)}`);
}

export function permissionFor(profile) {
  if (profile === "full") return "allow";
  const common = {
    read: "allow",
    list: "allow",
    glob: "allow",
    grep: "allow",
    skill: "allow",
    todowrite: "allow",
    question: "allow",
    edit: "ask",
    bash: "ask",
    task: "ask",
    external_directory: "ask",
    webfetch: "ask",
    websearch: "ask",
    lsp: profile === "balanced" ? "allow" : "ask",
  };
  return common;
}

async function readSettings(settingsPath) {
  try {
    return JSON.parse(await readFile(settingsPath, "utf8"));
  } catch (error) {
    if (error.code === "ENOENT") return {};
    throw new Error(`Cannot read settings JSON at ${settingsPath}: ${error.message}`);
  }
}
