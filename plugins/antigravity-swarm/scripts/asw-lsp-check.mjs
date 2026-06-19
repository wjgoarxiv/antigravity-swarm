#!/usr/bin/env node

import { readFileSync } from "node:fs";
import { safeMode } from "./asw-redact.mjs";

let payload = {};
try {
  const raw = readFileSync(0, "utf8");
  payload = raw.trim() ? JSON.parse(raw) : {};
} catch {
  // Antigravity treats an empty JSON object as a successful no-op hook result.
}

if (safeMode(payload)) {
  process.stdout.write("{}");
  process.exit(0);
}

process.stdout.write("{}");
