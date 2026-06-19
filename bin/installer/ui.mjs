import { createInterface } from "node:readline/promises";
import { stdin as defaultIn, stdout as defaultOut } from "node:process";
import { readFileSync } from "node:fs";
import { packageVersion } from "./paths.mjs";

export const hudColors = ["cyan", "blue", "teal", "green", "lavender", "rose", "gold", "orange", "slate", "gray"];

const ansi = {
  bold: "\x1b[1m",
  cyan: "\x1b[36m",
  magenta: "\x1b[35m",
  blue: "\x1b[34m",
  green: "\x1b[32m",
  yellow: "\x1b[33m",
  dim: "\x1b[2m",
  reset: "\x1b[0m",
};

const spinnerFrames = ["◐", "◓", "◑", "◒"];
const panelWidth = 48;
const logoLines = [
  " █████╗ ███████╗██╗    ██╗",
  "██╔══██╗██╔════╝██║    ██║",
  "███████║███████╗██║ █╗ ██║",
  "██╔══██║╚════██║██║███╗██║",
  "██║  ██║███████║╚███╔███╔╝",
  "╚═╝  ╚═╝╚══════╝ ╚══╝╚══╝ ",
];

const hudPalette = {
  cyan: "38;5;51",
  blue: "38;5;75",
  teal: "38;5;43",
  green: "38;5;82",
  lavender: "38;5;183",
  rose: "38;5;213",
  gold: "38;5;220",
  orange: "38;5;208",
  slate: "38;5;109",
  gray: "38;5;245",
};

export function paint(options, color, value) {
  if (!options.color) return value;
  return `${ansi[color]}${value}${ansi.reset}`;
}

export function paintHud(options, value) {
  if (!options.color) return value;
  const code = hudPalette[options.hudColor] ?? hudPalette.cyan;
  return `\x1b[1;${code}m${value}\x1b[0m`;
}

export function showHeader(options) {
  console.log(paintHud(options, "╭────────────────────────────────────────────────╮"));
  for (const line of logoLines) console.log(panelLine(options, paintHud(options, line), panelWidth - 2));
  console.log(panelLine(options, `${paintHud(options, `ASW v${packageVersion}`)} ${paint(options, "bold", "ANTIGRAVITY SWARM")}`, panelWidth - 2));
  console.log(panelLine(options, paint(options, "dim", "Hooks · Skills · HUD · Agents"), panelWidth - 2));
  console.log(paintHud(options, "╰────────────────────────────────────────────────╯"));
}

export function printMode(options) {
  const mode = options.dryRun ? "DRY RUN" : options.command.toUpperCase();
  console.log(sectionTitle(options, mode === "INTERACTIVE" ? "Install cockpit" : "Package"));
  console.log(kvLine(options, "Mode", `ASW ${mode}`));
  console.log(kvLine(options, mode === "INTERACTIVE" ? "Target" : "Install target", options.target));
  console.log(sectionTitle(options, mode === "INTERACTIVE" ? "Choose path" : "Install"));
}

export function showInstallSummary(options, rows = []) {
  console.log(paintHud(options, "╭──────────────────── ready ────────────────────╮"));
  for (const row of rows) console.log(panelLine(options, row, panelWidth - 2));
  console.log(paintHud(options, "╰────────────────────────────────────────────────╯"));
}

export function shouldPrompt(options, input = defaultIn, output = defaultOut, env = process.env) {
  return options.interactive && (env.ASW_TEST_TTY === "1" || (input.isTTY && output.isTTY && !env.CI));
}

export async function chooseInstallAction(options, input = defaultIn, output = defaultOut) {
  showHeader(options);
  printMode(options);
  console.log(paintHud(options, "╭────────────────────────────────────────────────╮"));
  console.log(menuLine(options, "01", "Install plugin + skills", panelWidth - 2));
  console.log(menuLine(options, "02", "Install with HUD", panelWidth - 2));
  console.log(menuLine(options, "03", "Install HUD only", panelWidth - 2));
  console.log(menuLine(options, "04", "Verify existing install", panelWidth - 2));
  console.log(paintHud(options, "╰────────────────────────────────────────────────╯"));
  const answer = await promptLine("Select 1) 2) 3) 4): ", input, output);
  return {
    "1": "install",
    "01": "install",
    "2": "install-hud-full",
    "02": "install-hud-full",
    "3": "install-hud",
    "03": "install-hud",
    "4": "verify",
    "04": "verify",
  }[answer] ?? "install";
}

export async function chooseHudColor(options, input = defaultIn, output = defaultOut) {
  console.log(sectionTitle(options, "HUD color"));
  console.log(paintHud(options, "╭────────────────────────────────────────────────╮"));
  hudColors.forEach((name, index) => console.log(colorChoiceLine(options, String(index + 1), name)));
  console.log(paintHud(options, "╰────────────────────────────────────────────────╯"));
  const answer = (await promptLine("Color: ", input, output)).toLowerCase();
  const numeric = Number(answer);
  if (Number.isInteger(numeric) && hudColors[numeric - 1]) return hudColors[numeric - 1];
  return hudColors.includes(answer) ? answer : options.hudColor;
}

export async function choosePermissionProfile(options, input = defaultIn, output = defaultOut) {
  console.log(sectionTitle(options, "Permission profile"));
  console.log(paintHud(options, "╭────────────────────────────────────────────────╮"));
  console.log(menuLine(options, "01", "safe      least privilege / read-mostly", panelWidth - 2));
  console.log(menuLine(options, "02", "balanced  recommended prompts", panelWidth - 2));
  console.log(menuLine(options, "03", "full      broad access; trust only", panelWidth - 2));
  console.log(menuLine(options, "04", "none      do not modify permissions", panelWidth - 2));
  console.log(paintHud(options, "╰────────────────────────────────────────────────╯"));
  const answer = (await promptLine("Permission profile: ", input, output)).toLowerCase();
  return {
    "1": "safe",
    "01": "safe",
    safe: "safe",
    "2": "balanced",
    "02": "balanced",
    balanced: "balanced",
    "3": "full",
    "03": "full",
    full: "full",
    "4": "none",
    "04": "none",
    none: "none",
  }[answer] ?? "safe";
}

function menuLine(options, key, label, width = 31) {
  const visiblePrefix = key.length > 1 ? key : `${key})`;
  const body = `${paint(options, "yellow", visiblePrefix)} ${label}`;
  const visibleLength = `${visiblePrefix} ${label}`.length;
  return `${paintHud(options, "│")} ${body}${" ".repeat(Math.max(0, width - visibleLength))}${paintHud(options, "│")}`;
}

function colorChoiceLine(options, key, name) {
  const marker = name === options.hudColor ? " current" : "";
  const body = `${paint(options, "yellow", key.padStart(2, "0"))}  ${swatch(options, name)} ${name}${marker ? paint(options, "dim", marker) : ""}`;
  return `${paintHud(options, "│")} ${body}${pad(body, panelWidth - 2)}${paintHud(options, "│")}`;
}

function swatch(options, name) {
  if (!options.color) return "■";
  const code = hudPalette[name] ?? hudPalette.cyan;
  return `\x1b[1;${code}m■\x1b[0m`;
}

function sectionTitle(options, value) {
  return `${paintHud(options, "◆")} ${paint(options, "bold", value)}`;
}

function kvLine(options, key, value) {
  const label = paint(options, "dim", key);
  const body = `${paint(options, "dim", `${key.padEnd(14)} `)}${value}`;
  if (visibleLength(body) <= panelWidth - 2) return `${paintHud(options, "│")} ${body}`;
  const wrapped = wrapVisible(value, panelWidth - 4)
    .map((line) => `${paintHud(options, "│")} ${paint(options, "dim", "  ")}${line}`)
    .join("\n");
  return `${paintHud(options, "│")} ${label}\n${wrapped}`;
}

function panelLine(options, value, width = 38) {
  const body = compactVisible(value, width);
  return `${paintHud(options, "│")} ${body}${pad(body, width)}${paintHud(options, "│")}`;
}

function compactVisible(value, width) {
  if (visibleLength(value) <= width) return value;
  const plain = stripAnsi(value);
  return `${plain.slice(0, Math.max(0, width - 1))}…`;
}

function wrapVisible(value, width) {
  const plain = stripAnsi(value);
  if (plain.length <= width) return [plain];
  const lines = [];
  let rest = plain;
  while (rest.length > width) {
    const slash = rest.lastIndexOf("/", width);
    const end = slash > 0 ? slash + 1 : width;
    lines.push(rest.slice(0, end));
    rest = rest.slice(end);
  }
  if (rest) lines.push(rest);
  return lines;
}

function pad(value, width) {
  return " ".repeat(Math.max(0, width - visibleLength(value)));
}

function visibleLength(value) {
  return stripAnsi(value).length;
}

function stripAnsi(value) {
  return value.replace(/\x1b\[[0-9;]*m/g, "");
}

let bufferedAnswers;

async function promptLine(prompt, input, output) {
  if (process.env.ASW_TEST_TTY === "1" && !input.isTTY) {
    output.write(prompt);
    if (!bufferedAnswers) bufferedAnswers = readFileSync(0, "utf8").split(/\r?\n/);
    const answer = (bufferedAnswers.shift() ?? "").trim();
    output.write(`${answer}\n`);
    return answer;
  }
  const rl = createInterface({ input, output });
  try {
    return (await rl.question(prompt)).trim();
  } finally {
    rl.close();
  }
}

export async function withSpinner(options, label, action) {
  const tty = options.forceTty || process.stdout.isTTY;
  if (options.dryRun || !tty) {
    console.log(`${paintHud(options, "◇")} ${label}`);
    const result = await action();
    console.log(`${paint(options, "green", "✓")} ${label}`);
    return result;
  }
  let index = 0;
  process.stdout.write(`${paintHud(options, spinnerFrames[index])} ${label}`);
  const timer = setInterval(() => {
    index = (index + 1) % spinnerFrames.length;
    process.stdout.write(`\r${paintHud(options, spinnerFrames[index])} ${label}`);
  }, 70);
  try {
    const result = await action();
    clearInterval(timer);
    process.stdout.write(`\r${paint(options, "green", "✓")} ${label}\n`);
    return result;
  } catch (error) {
    clearInterval(timer);
    process.stdout.write(`\r${paint(options, "yellow", "×")} ${label}\n`);
    throw error;
  }
}
