<p align="center">
  <img src="./cover.png" alt="Antigravity Swarm cover" width="100%" />
</p>

<h1 align="center">Antigravity Swarm</h1>

<pre align="center"><code>
 █████╗ ███████╗██╗    ██╗
██╔══██╗██╔════╝██║    ██║
███████║███████╗██║ █╗ ██║
██╔══██║╚════██║██║███╗██║
██║  ██║███████║╚███╔███╔╝
╚═╝  ╚═╝╚══════╝ ╚══╝╚══╝
</code></pre>

<p align="center">
  <strong>Antigravity CLI workflow layer: type <code>asw</code> and turn a loose request into a planned agent run.</strong>
</p>

<p align="center">
  <img alt="Antigravity CLI" src="https://img.shields.io/badge/Antigravity-CLI-00D5FF?style=for-the-badge&labelColor=111827" />
  <img alt="ASW v0.2.1" src="https://img.shields.io/badge/ASW-v0.2.1-8B5CF6?style=for-the-badge&labelColor=111827" />
  <img alt="Hooks skills agents HUD" src="https://img.shields.io/badge/hooks%20%2B%20skills%20%2B%20agents-HUD-22C55E?style=for-the-badge&labelColor=111827" />
  <img alt="MIT license" src="https://img.shields.io/badge/license-MIT-F59E0B?style=for-the-badge&labelColor=111827" />
</p>

<p align="center">
  <a href="#quick-start">Quick Start</a> ·
  <a href="#large-update">Large Update</a> ·
  <a href="#mission-control">Mission Control</a> ·
  <a href="#aliases">Aliases</a> ·
  <a href="#status-line">HUD</a> ·
  <a href="./README_KO.md">한국어</a>
</p>

Antigravity Swarm installs an ASW workflow layer for Antigravity CLI and Antigravity IDE. It bundles short wake words, global skills, hook routes, subagent presets, diagnostics guidance, background continuation, and a compact status line.

The old repo was a Gemini-first swarm runner. v0.2.1 is the large Antigravity rebuild: npm install, Antigravity-native plugin layout, ASW aliases, hooks, subagents, LSP diagnostics, and a HUD that can surface context, git state, and model quota data when the CLI provides it.

> [!IMPORTANT]
> Type `asw` when the work is ready to move. Type `asw-plan` when the work needs shape first. Type `asw-review` before you call it done.

<a id="quick-start"></a>
## Quick Start

```bash
npx antigravity-swarm install --hud
```

Then open Antigravity CLI or IDE in a project and use the loop:

```text
asw-plan "Refactor auth without changing public behavior"
start-work
asw
asw-review
```

Prefer the installer menu:

```bash
npx antigravity-swarm --interactive
```

Choose a HUD color:

```bash
npx antigravity-swarm install --hud --hud-color rose
```

Available colors: `cyan`, `blue`, `teal`, `green`, `lavender`, `rose`, `gold`, `orange`, `slate`, `gray`.

Other useful commands:

```bash
npx antigravity-swarm --dry-run install
npx antigravity-swarm verify
npx antigravity-swarm install-hud
npx antigravity-swarm uninstall
```

ASW writes the plugin under `~/.gemini/config/`, installs global skill shims, and registers the HUD through `~/.gemini/antigravity-cli/settings.json`. Existing different `statusLine` settings are left alone unless `--force-hud` is passed.

<a id="large-update"></a>
## Large Update

v0.2.1 is not a rename pass. It moves the project from a script-oriented swarm into an Antigravity workflow package.

| Before | Now |
|---|---|
| Gemini-first runner scripts | Antigravity CLI and IDE plugin install |
| Manual setup steps | `npx antigravity-swarm install --hud` |
| Single command surface | Planner, executor, loop, reviewer, cleanup, goal, diagnostics |
| Static docs | Hooked aliases with visible workflow handoff |
| Minimal prompt routing | Skills, hooks, subagents, LSP diagnostics, HUD |

The center of gravity is the command loop:

- Type `asw-plan` to produce an executable plan before implementation.
- Type `start-work` or `asw-start-work` to run that plan with the executor contract.
- Type `asw` for test-first implementation and visible checks.
- Type `asw-review` for a final reviewer pass over changes, hooks, install behavior, and docs.

<a id="mission-control"></a>
## Mission Control

```text
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                     ASW Antigravity Mission Control                  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
┌──────────────┬────────────┬──────────────────────┬──────────────────┐
│ Command      │ Role       │ What it wakes         │ Best moment       │
├──────────────┼────────────┼──────────────────────┼──────────────────┤
│ asw-plan     │ planner    │ scope, risks, steps   │ before big work    │
│ start-work   │ executor   │ plan execution        │ after plan review  │
│ asw          │ loop       │ tests, code, QA       │ active build pass  │
│ asw-review   │ reviewer   │ diff and install QA   │ before shipping    │
└──────────────┴────────────┴──────────────────────┴──────────────────┘
```

This is the part inherited from the first Antigravity Swarm: visible coordination. The new version keeps that mission-control feeling, but moves the controls into Antigravity aliases, hooks, skills, agents, and a status line that stays with your session.

<a id="aliases"></a>
## Aliases

Type these in Antigravity CLI or IDE:

| Alias | Mode | Use |
|---|---|---|
| `asw-plan` | planning | Large changes, migrations, unclear work |
| `start-work` | execution | Run the plan produced by `asw-plan` |
| `asw-start-work` | execution | Same as `start-work`, ASW-explicit |
| `asw-goal` | goal | Long tasks with explicit completion criteria |
| `asw` | loop | Test-first implementation and visible checks |
| `asw-loop` | loop | Same as `asw`, more explicit |
| `asw-review` | review | Diff, package, hook, and QA review |
| `asw-remove-ai-slops` | cleanup | Remove generated-looking clutter while preserving behavior |
| `ulw` | compatibility | Old loop alias mapped into ASW |

The hook injects a short directive before the model call. It does not run shell commands from the prompt and ignores identifier-like text such as `asw_helper.mjs`.

<a id="contents"></a>
## Contents

### Skills

The package ships 15 skills:

```text
asw, asw-loop, asw-plan, asw-start-work, asw-review, asw-goal,
asw-debug, asw-programming, asw-lsp, asw-rules,
asw-comment-check, asw-refactor, asw-ui-ux, asw-cleanup,
asw-remove-ai-slops
```

### Agents

Antigravity validates four subagent presets:

- `asw-planner`
- `asw-explorer`
- `asw-librarian`
- `asw-reviewer`

### Hooks

ASW installs hook support for alias detection, diagnostics handoff, and background-work continuation.

### LSP diagnostics

ASW includes a diagnostics hook and skill guidance for running real language checks on changed files.

<a id="status-line"></a>
## Status Line

The HUD renders a compact line:

```text
[✨ASW v0.2.1] | G-f (Medium) 3.5 │ ctx [▎░] 9%/1000k │ 5h [▏░] 4% ↻2h15m │ 1w [▊░] 35% ↻3d6h │ git main +3 ✓
```

When Antigravity passes `/usage` model quota rows into the status line payload, ASW adds a compact model quota segment:

```text
mq G-f(M) [█░] 60% · G-f(H) 60% · G-f(L) 60% · G-p(L) 60% ↻6d22h
```

## Acknowledgements

ASW adapts community patterns for planning, hooks, skills, diagnostics, and careful review into Antigravity CLI terminology and contracts.
