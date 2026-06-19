import { resolve } from "node:path";
import { defaultSettingsPath, defaultTarget } from "./paths.mjs";
import { normalizePermissionProfile } from "./permissions.mjs";

export function parseArgs(argv, env = process.env) {
  const options = {
    command: "install",
    target: defaultTarget,
    settingsTarget: defaultSettingsPath,
    dryRun: false,
    hud: false,
    forceHud: false,
    forcePermission: false,
    interactive: false,
    hudColor: "cyan",
    permissionProfile: normalizePermissionProfile(env.ASW_PERMISSION_PROFILE),
    color: env.FORCE_COLOR === "1" || (!env.NO_COLOR && env.FORCE_COLOR !== "0"),
  };

  const rest = [...argv];
  if (rest[0] === "--dry-run") {
    options.dryRun = true;
    rest.shift();
  }
  if (rest[0] && !rest[0].startsWith("-")) {
    options.command = rest.shift();
  }

  for (let i = 0; i < rest.length; i += 1) {
    const arg = rest[i];
    if (arg === "--target") {
      options.target = resolve(rest[++i] ?? "");
    } else if (arg === "--settings-target") {
      options.settingsTarget = resolve(rest[++i] ?? "");
    } else if (arg === "--dry-run") {
      options.dryRun = true;
    } else if (arg === "--hud") {
      options.hud = true;
    } else if (arg === "--force-hud") {
      options.forceHud = true;
    } else if (arg === "--force-permission") {
      options.forcePermission = true;
    } else if (arg === "--permission-profile") {
      const value = rest[++i];
      if (!value || value.startsWith("-")) throw new Error("Missing value for --permission-profile. Supported profiles: safe, balanced, full, none");
      options.permissionProfile = normalizePermissionProfile(value);
    } else if (arg === "--hud-color") {
      options.hudColor = (rest[++i] ?? "cyan").toLowerCase();
    } else if (arg === "--interactive") {
      options.interactive = true;
      options.command = options.command === "install" ? "interactive" : options.command;
    } else if (arg === "--no-color") {
      options.color = false;
    } else if (arg === "--help" || arg === "-h") {
      options.command = "help";
    } else {
      throw new Error(`Unknown argument: ${arg}`);
    }
  }

  return options;
}
