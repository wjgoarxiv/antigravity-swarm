#!/usr/bin/env node

import { stdin, stdout } from "node:process";

const ASW_VERSION = "0.2.2";
const palette = {
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

function readStdin() {
  return new Promise((resolve) => {
    let data = "";
    stdin.setEncoding("utf8");
    stdin.on("data", (chunk) => {
      data += chunk;
    });
    stdin.on("end", () => resolve(data));
  });
}

function color(value) {
  if (process.env.FORCE_COLOR === "0" || (process.env.NO_COLOR && process.env.FORCE_COLOR !== "1")) return value;
  const code = palette[process.env.ASW_HUD_COLOR] ?? palette.cyan;
  return `\x1b[1;${code}m${value}\x1b[0m`;
}

function percent(value) {
  const number = Number(value);
  if (!Number.isFinite(number)) return "?";
  return `${Math.round(number)}%`;
}

function gauge(value) {
  const number = Number(value);
  if (!Number.isFinite(number)) return "░░";
  const marks = ["▏", "▎", "▍", "▌", "▋", "▊", "▉", "█"];
  const clamped = Math.max(0, Math.min(100, number));
  if (clamped <= 0) return "░░";
  if (clamped >= 100) return "██";
  const index = Math.max(0, Math.min(7, Math.floor((clamped % 50) / 7)));
  if (clamped >= 50) return `█${marks[index]}`;
  return `${marks[index]}░`;
}

function modelName(model) {
  const raw = model?.display_name ?? model?.id ?? "model";
  const text = String(raw).replace(/\s+/g, " ").trim();
  const gemini = text.match(/^Gemini\s+([\d.]+)\s+Flash(?:\s+\(([^)]+)\))?/i);
  if (gemini) return gemini[2] ? `G-f (${gemini[2]}) ${gemini[1]}` : `G-f ${gemini[1]}`;
  const pro = text.match(/^Gemini\s+([\d.]+)\s+Pro(?:\s+\(([^)]+)\))?/i);
  if (pro) return pro[2] ? `G-p (${pro[2]}) ${pro[1]}` : `G-p ${pro[1]}`;
  return text.replace(/^Gemini/i, "G").trim();
}

function contextLine(payload) {
  const context = payload.context_window ?? payload.context ?? {};
  const used = context.used_percentage ?? context.percentage;
  const size = Number(context.context_window_size ?? context.total_tokens ?? 0);
  const suffix = Number.isFinite(size) && size > 0 ? `/${Math.round(size / 1000)}k` : "";
  return `ctx [${gauge(used)}] ${percent(used)}${suffix}`;
}

function quotaLine(label, quota) {
  const used = quota?.used_percentage ?? quota?.percentage;
  if (!Number.isFinite(Number(used))) return "";
  const reset = resetText(quota?.reset_in_seconds ?? quota?.resetSeconds);
  return `${label} [${gauge(used)}] ${percent(used)}${reset ? ` ↻${reset}` : ""}`;
}

function modelQuotaLine(payload) {
  const rows = modelQuotaRows(payload).slice(0, 4);
  if (rows.length === 0) return "";
  const parts = rows.map((row, index) => {
    const remaining = remainingPercent(row);
    if (!Number.isFinite(remaining)) return "";
    const name = compactQuotaModelName(row.model ?? row.display_name ?? row.displayName ?? row.name ?? row.id);
    if (!name) return "";
    if (index === 0) return `${name} [${remainingGauge(remaining)}] ${Math.round(remaining)}%`;
    return `${name} ${Math.round(remaining)}%`;
  }).filter(Boolean);
  if (parts.length === 0) return "";
  const reset = resetText(firstResetSeconds(rows));
  return `mq ${parts.join(" · ")}${reset ? ` ↻${reset}` : ""}`;
}

function modelQuotaRows(payload) {
  const usage = payload.usage ?? payload.model_usage ?? payload.modelUsage ?? {};
  for (const value of [
    payload.model_quota,
    payload.modelQuota,
    payload.model_quotas,
    payload.modelQuotas,
    usage.model_quota,
    usage.modelQuota,
    usage.model_quotas,
    usage.modelQuotas,
    usage.models,
  ]) {
    if (Array.isArray(value)) return value;
  }
  return [];
}

function remainingPercent(row) {
  const explicit = Number(row?.remaining_percentage ?? row?.remainingPercentage ?? row?.remaining_percent ?? row?.remainingPercent);
  if (Number.isFinite(explicit)) return explicit;
  const used = Number(row?.used_percentage ?? row?.usedPercentage ?? row?.percentage);
  if (Number.isFinite(used)) return Math.max(0, Math.min(100, 100 - used));
  return Number.NaN;
}

function firstResetSeconds(rows) {
  for (const row of rows) {
    const seconds = Number(row?.refreshes_in_seconds ?? row?.refreshesInSeconds ?? row?.reset_in_seconds ?? row?.resetSeconds);
    if (Number.isFinite(seconds) && seconds > 0) return seconds;
  }
  return Number.NaN;
}

function remainingGauge(value) {
  const clamped = Math.max(0, Math.min(100, Number(value)));
  if (!Number.isFinite(clamped)) return "░░";
  if (clamped >= 75) return "██";
  if (clamped >= 50) return "█░";
  if (clamped > 0) return "▌░";
  return "░░";
}

function compactQuotaModelName(value) {
  const text = modelName({ display_name: value });
  const tier = text.match(/^(G-[fp]) \(([^)]+)\) [\d.]+$/);
  if (tier) return `${tier[1]}(${tier[2][0].toUpperCase()})`;
  const plain = text.match(/^(G-[fp]) [\d.]+$/);
  if (plain) return plain[1];
  return text.split(/\s+/).slice(0, 2).join("-");
}

function resetText(seconds) {
  const raw = Number(seconds);
  if (!Number.isFinite(raw) || raw <= 0) return "";
  const days = Math.floor(raw / 86400);
  const hours = Math.floor((raw % 86400) / 3600);
  const minutes = Math.floor((raw % 3600) / 60);
  if (days > 0) return `${days}d${hours}h`;
  if (hours > 0) return `${hours}h${minutes}m`;
  return `${minutes}m`;
}

function gitLine(vcs) {
  if (!vcs?.branch) return "";
  const count = Number(vcs.added ?? vcs.changed ?? vcs.changes ?? 0);
  const delta = Number.isFinite(count) && count > 0 ? ` +${count}` : "";
  const clean = vcs.dirty ? "!" : "✓";
  return `git ${vcs.branch}${delta} ${clean}`;
}

function render(payload) {
  const quota = payload.quota ?? payload.quotas ?? {};
  return [
    color(`[✨ASW v${ASW_VERSION}]`),
    color(modelName(payload.model)),
    color(contextLine(payload)),
    tone(modelQuotaLine(payload)),
    tone(quotaLine("5h", quota.five_hour ?? quota.fiveHour ?? quota["5h"])),
    tone(quotaLine("1w", quota.weekly ?? quota.one_week ?? quota["1w"])),
    tone(gitLine(payload.vcs)),
  ].filter(Boolean).join(" │ ");
}

function tone(value) {
  return value ? color(value) : "";
}

const raw = await readStdin();
try {
  stdout.write(`${render(raw.trim() ? JSON.parse(raw) : {})}\n`);
} catch {
  stdout.write(`${color(`[✨ASW v${ASW_VERSION}]`)} │ status unavailable\n`);
}
