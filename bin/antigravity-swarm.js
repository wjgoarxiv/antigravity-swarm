#!/usr/bin/env node

import { main } from "./installer/main.mjs";

main(process.argv.slice(2)).catch((error) => {
  console.error(`antigravity-swarm: ${error.message}`);
  process.exit(1);
});
