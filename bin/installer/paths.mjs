import { homedir } from "node:os";
import { readFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

export const root = resolve(dirname(fileURLToPath(import.meta.url)), "..", "..");
export const packageVersion = JSON.parse(readFileSync(join(root, "package.json"), "utf8")).version;
export const pluginName = "antigravity-swarm";
export const pluginSource = join(root, "plugins", pluginName);
export const defaultTarget = join(homedir(), ".gemini", "config");
export const defaultSettingsPath = join(homedir(), ".gemini", "antigravity-cli", "settings.json");
