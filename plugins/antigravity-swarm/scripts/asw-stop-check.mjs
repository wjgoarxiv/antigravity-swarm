#!/usr/bin/env node

import { readFileSync } from "node:fs";

function readPayload() {
  try {
    const raw = readFileSync(0, "utf8");
    return raw.trim() ? JSON.parse(raw) : {};
  } catch {
    return {};
  }
}

const payload = readPayload();
if (payload.fullyIdle === false) {
  process.stdout.write(JSON.stringify({
    decision: "continue",
    reason: "Antigravity Swarm detected active background work. Continue until spawned work is idle, verified, and cleaned up.",
  }));
} else {
  process.stdout.write(JSON.stringify({ decision: "" }));
}

