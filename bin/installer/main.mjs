import { parseArgs } from "./options.mjs";
import { runCommand } from "./commands.mjs";

export async function main(argv) {
  const options = parseArgs(argv);
  await runCommand(options);
}
