import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

const repoRoot = new URL("..", import.meta.url).pathname;

test("#docs #README targets Antigravity CLI and documents ASW aliases", async () => {
  const readme = await readFile(`${repoRoot}/README.md`, "utf8");
  const plugin = JSON.parse(await readFile(`${repoRoot}/plugins/antigravity-swarm/plugin.json`, "utf8"));

  assert.match(readme, /Antigravity CLI/);
  assert.match(readme, /█████╗ ███████╗██╗\s+██╗/);
  assert.match(readme, /╚═╝  ╚═╝╚══════╝ ╚══╝╚══╝/);
  assert.match(readme, /img\.shields\.io/);
  assert.match(readme, /workflow layer/i);
  assert.match(readme, /Mission Control/);
  assert.match(readme, /Large Update/);
  assert.match(readme, /Type `asw`/);
  assert.match(readme, /Type `asw-plan`/);
  assert.match(readme, /Type `asw-review`/);
  assert.match(readme, /planner/i);
  assert.match(readme, /executor/i);
  assert.match(readme, /reviewer/i);
  assert.match(readme, /npx antigravity-swarm install/);
  assert.match(readme, /`asw`/);
  assert.match(readme, /`asw-plan`/);
  assert.match(readme, /`start-work`/);
  assert.match(readme, /`asw-start-work`/);
  assert.match(readme, /`asw-loop`/);
  assert.match(readme, /`asw-goal`/);
  assert.match(readme, /`asw-remove-ai-slops`/);
  assert.match(readme, /LSP diagnostics/);
  assert.match(readme, /status line/i);
  assert.match(readme, /GPT-OSS 120B \(Medium\)/);
  assert.match(readme, /ctx \[█▋\] 81%\/131k/);
  assert.match(readme, /mq G-f\(M\)/);
  assert.match(readme, /model quota/i);
  assert.match(readme, /Antigravity validates six subagent presets/);
  assert.match(readme, /`asw-planning-analysis`/);
  assert.match(readme, /`asw-plan-audit`/);
  assert.doesNotMatch(readme, /5h \[▏░\]|1w \[▊░\]|G-f \(Medium\) 3\.5 │ ctx \[▎░\] 9%\/1000k/);
  assert.match(readme, /~\/\.gemini\/config/);
  assert.doesNotMatch(readme, /py_compile|npm test|npm pack|agy plugin validate|Manual hook smoke|Manual HUD smoke|Legacy Python|hook payloads|returns `\\{\\}`|hooks\\.json/i);
  assert.doesNotMatch(readme, /Core runtime used by the agents/);
  assert.doesNotMatch(readme, /antigravity-cli\/plugins|antigravity-cli\/skills/);
  assert.doesNotMatch(readme, new RegExp(["REFERENCE_" + ["lazy", "codex"].join(""), "Lazy" + "Cod" + "ex", "O" + "MO"].join("|")));
  assert.doesNotMatch(readme, /Package Surface|pycache|files allowlist|tarball/i);
  assert.doesNotMatch(readme, /dependency-free spinner|evidence-driven|seamless|leverage|cutting-edge|robust|supercharge|next-level/i);
  assert.doesNotMatch(readme, /frictionless|game-changing|revolutionary|magic|10x|autonomous army|AI workforce/i);
  assert.doesNotMatch(readme, /stargazing project|sky map|constellation/i);
  assert.equal(plugin.version, "0.2.1");
  assert.equal(plugin.name, "antigravity-swarm");
});

test("#docs #Korean README and package metadata avoid deprecated Gemini-first install", async () => {
  const readme = await readFile(`${repoRoot}/README_KO.md`, "utf8");
  const pkg = JSON.parse(await readFile(`${repoRoot}/package.json`, "utf8"));

  assert.match(readme, /Antigravity CLI/);
  assert.match(readme, /█████╗ ███████╗██╗\s+██╗/);
  assert.match(readme, /╚═╝  ╚═╝╚══════╝ ╚══╝╚══╝/);
  assert.match(readme, /img\.shields\.io/);
  assert.match(readme, /워크플로 레이어/);
  assert.match(readme, /Mission Control/);
  assert.match(readme, /큰 업데이트/);
  assert.match(readme, /`asw`를 입력/);
  assert.match(readme, /planner|플래너/i);
  assert.match(readme, /executor|실행/i);
  assert.match(readme, /reviewer|리뷰/i);
  assert.match(readme, /npx antigravity-swarm install/);
  assert.match(readme, /HUD/);
  assert.match(readme, /`start-work`/);
  assert.match(readme, /`asw-start-work`/);
  assert.match(readme, /`asw-remove-ai-slops`/);
  assert.match(readme, /statusLine/);
  assert.match(readme, /GPT-OSS 120B \(Medium\)/);
  assert.match(readme, /ctx \[█▋\] 81%\/131k/);
  assert.match(readme, /mq G-f\(M\)/);
  assert.match(readme, /model quota/i);
  assert.match(readme, /Antigravity가 검증하는 subagent preset은 6개입니다/);
  assert.match(readme, /`asw-planning-analysis`/);
  assert.match(readme, /`asw-plan-audit`/);
  assert.doesNotMatch(readme, /5h \[▏░\]|1w \[▊░\]|G-f \(Medium\) 3\.5 │ ctx \[▎░\] 9%\/1000k/);
  assert.match(readme, /~\/\.gemini\/config/);
  assert.doesNotMatch(readme, /py_compile|npm test|npm pack|agy plugin validate|훅 스모크|HUD 스모크|기존 Python|hook payload|`\\{\\}`|hooks\\.json/i);
  assert.doesNotMatch(readme, /dependency-free spinner|설치기는 interactive terminal|evidence-driven|seamless|leverage|cutting-edge|robust|supercharge|next-level/i);
  assert.doesNotMatch(readme, /frictionless|game-changing|revolutionary|magic|10x|autonomous army|AI workforce/i);
  assert.doesNotMatch(readme, /별을 보는 프로젝트|별자리|성좌/);
  assert.doesNotMatch(readme, /패키지 표면|pycache|files allowlist|tarball/i);
  assert.doesNotMatch(readme, new RegExp(["REFERENCE_" + ["lazy", "codex"].join(""), "Lazy" + "Cod" + "ex", "O" + "MO"].join("|")));
  assert.doesNotMatch(readme, /antigravity-cli\/plugins|antigravity-cli\/skills/);
  assert.equal(pkg.bin["antigravity-swarm"], "bin/antigravity-swarm.js");
  assert.equal(pkg.type, "module");
  assert.equal(pkg.version, "0.2.1");
  assert.ok(pkg.files.includes("plugins/antigravity-swarm"));
});

test("#skill asw-plan #creates executable plan files before implementation", async () => {
  const skill = await readFile(`${repoRoot}/plugins/antigravity-swarm/skills/asw-plan/SKILL.md`, "utf8");

  assert.match(skill, /planner, not an implementer/i);
  assert.match(skill, /\.asw\/plans\/<slug>\.md/);
  assert.match(skill, /Socratic interview/i);
  assert.match(skill, /parallel repo exploration/i);
  assert.match(skill, /gap analysis/i);
  assert.match(skill, /Downstream Executor Contract/i);
  assert.match(skill, /Refuse implementation/i);
  assert.doesNotMatch(skill, new RegExp(["Lazy" + "Cod" + "ex", "O" + "MO", "Prome" + "theus", "Boul" + "der"].join("|")));
});
