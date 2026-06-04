#!/usr/bin/env node

import { readFileSync } from "node:fs";

try {
  readFileSync(0, "utf8");
} catch {
  // Antigravity treats an empty JSON object as a successful no-op hook result.
}

process.stdout.write("{}");

