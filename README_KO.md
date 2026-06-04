<p align="center">
  <img src="./cover.png" alt="Antigravity Swarm cover" width="100%" />
</p>

<h1 align="center">Antigravity Swarm</h1>

<table align="center">
<tr>
<td>
<pre><code>
 █████╗ ███████╗██╗    ██╗
██╔══██╗██╔════╝██║    ██║
███████║███████╗██║ █╗ ██║
██╔══██║╚════██║██║███╗██║
██║  ██║███████║╚███╔███╔╝
╚═╝  ╚═╝╚══════╝ ╚══╝╚══╝
</code></pre>
</td>
</tr>
</table>

<p align="center">
  <strong>Antigravity CLI 워크플로 레이어: <code>asw</code>를 입력하고, 느슨한 요청을 계획된 에이전트 실행으로 바꾸세요.</strong>
</p>

<p align="center">
  <img alt="Antigravity CLI" src="https://img.shields.io/badge/Antigravity-CLI-00D5FF?style=for-the-badge&labelColor=111827" />
  <img alt="ASW v0.2.1" src="https://img.shields.io/badge/ASW-v0.2.1-8B5CF6?style=for-the-badge&labelColor=111827" />
  <img alt="Hooks skills agents HUD" src="https://img.shields.io/badge/hooks%20%2B%20skills%20%2B%20agents-HUD-22C55E?style=for-the-badge&labelColor=111827" />
  <img alt="MIT license" src="https://img.shields.io/badge/license-MIT-F59E0B?style=for-the-badge&labelColor=111827" />
</p>

<p align="center">
  <a href="#quick-start">Quick Start</a> ·
  <a href="#large-update">큰 업데이트</a> ·
  <a href="#mission-control">Mission Control</a> ·
  <a href="#aliases">Alias</a> ·
  <a href="#status-line">HUD</a> ·
  <a href="./README.md">English</a>
</p>

Antigravity Swarm은 Antigravity CLI와 Antigravity IDE 위에 ASW 워크플로 레이어를 설치합니다. 짧은 호출어, 전역 스킬, hook route, subagent preset, 진단 가이드, 백그라운드 continuation, compact status line을 함께 제공합니다.

예전 프로젝트가 Gemini-first swarm runner였다면, v0.2.1은 Antigravity용 큰 업데이트입니다. npm 설치, Antigravity plugin layout, ASW alias, hooks, subagents, LSP diagnostics, 그리고 CLI가 데이터를 넘길 때 context, git, model quota를 보여주는 HUD까지 포함합니다.

> [!IMPORTANT]
> 작업을 밀고 나갈 때는 `asw`를 입력하세요. 먼저 형태를 잡아야 할 때는 `asw-plan`, 마무리 전에는 `asw-review`가 좋습니다.

<a id="quick-start"></a>
## Quick Start

```bash
npx antigravity-swarm install --hud
```

그다음 Antigravity CLI나 IDE를 프로젝트에서 열고 이 흐름으로 사용합니다.

```text
asw-plan "Refactor auth without changing public behavior"
start-work
asw
asw-review
```

메뉴형 설치가 편하다면:

```bash
npx antigravity-swarm --interactive
```

HUD 색상 선택:

```bash
npx antigravity-swarm install --hud --hud-color rose
```

색상: `cyan`, `blue`, `teal`, `green`, `lavender`, `rose`, `gold`, `orange`, `slate`, `gray`.

기타 명령:

```bash
npx antigravity-swarm --dry-run install
npx antigravity-swarm verify
npx antigravity-swarm install-hud
npx antigravity-swarm uninstall
```

ASW는 plugin을 `~/.gemini/config/` 아래에 설치하고, global skill shim을 만들며, `~/.gemini/antigravity-cli/settings.json`을 통해 HUD를 등록합니다. 이미 다른 `statusLine` 설정이 있으면 `--force-hud` 없이는 바꾸지 않습니다.

<a id="large-update"></a>
## 큰 업데이트

v0.2.1은 이름만 바꾼 버전이 아닙니다. script 중심 swarm에서 Antigravity workflow package로 중심을 옮겼습니다.

| 이전 | 지금 |
|---|---|
| Gemini-first runner script | Antigravity CLI와 IDE plugin install |
| 수동 설정 단계 | `npx antigravity-swarm install --hud` |
| 단일 명령 중심 | planner, executor, loop, reviewer, cleanup, goal, diagnostics |
| 정적인 문서 | hook alias와 보이는 workflow handoff |
| 최소 prompt routing | skills, hooks, subagents, LSP diagnostics, HUD |

핵심은 명령 루프입니다.

- `asw-plan`을 입력해 구현 전에 실행 가능한 계획을 만듭니다.
- `start-work` 또는 `asw-start-work`로 그 계획을 executor contract에 맞춰 실행합니다.
- `asw`를 입력하면 테스트 먼저, 눈에 보이는 확인까지 이어갑니다.
- `asw-review`로 변경 사항, hooks, 설치 동작, docs를 마지막으로 검토합니다.

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

이 감성은 기존 Antigravity Swarm README에서 이어받았습니다. 보이는 coordination, mission-control 느낌은 남기고, 실제 조작부는 Antigravity alias, hook, skill, agent, status line으로 옮겼습니다.

<a id="aliases"></a>
## Alias

Antigravity CLI나 IDE에서 입력합니다.

| Alias | 모드 | 용도 |
|---|---|---|
| `asw-plan` | 계획 | 큰 변경, 마이그레이션, 애매한 작업 |
| `start-work` | 실행 | `asw-plan`으로 만든 계획 실행 |
| `asw-start-work` | 실행 | `start-work`와 같지만 ASW 명시 |
| `asw-goal` | 목표 | 완료 기준이 필요한 긴 작업 |
| `asw` | 루프 | 테스트 먼저, 눈에 보이는 확인까지 |
| `asw-loop` | 루프 | `asw`와 같지만 더 명시적 |
| `asw-review` | 리뷰 | diff, 패키지, 훅, QA 검토 |
| `asw-remove-ai-slops` | 정리 | 생성형 코드 냄새를 동작 보존 기준으로 제거 |
| `ulw` | 호환 | 기존 loop alias를 ASW로 연결 |

훅은 모델 호출 전에 짧은 지시문을 넣습니다. 프롬프트 속 셸 명령은 실행하지 않고, `asw_helper.mjs` 같은 식별자는 무시합니다.

<a id="contents"></a>
## 구성

### Skills

설치되는 스킬은 15개입니다.

```text
asw, asw-loop, asw-plan, asw-start-work, asw-review, asw-goal,
asw-debug, asw-programming, asw-lsp, asw-rules,
asw-comment-check, asw-refactor, asw-ui-ux, asw-cleanup,
asw-remove-ai-slops
```

### Agents

Antigravity가 검증하는 subagent preset은 4개입니다.

- `asw-planner`
- `asw-explorer`
- `asw-librarian`
- `asw-reviewer`

### Hooks

ASW는 alias 감지, 진단 연결, 백그라운드 작업 continuation을 위한 hook support를 설치합니다.

### LSP Diagnostics

ASW는 변경 파일의 실제 언어 검사를 유도하는 진단 hook과 스킬 지시를 포함합니다.

<a id="status-line"></a>
## Status Line

HUD 예시:

```text
[✨ASW v0.2.1] | G-f (Medium) 3.5 │ ctx [▎░] 9%/1000k │ 5h [▏░] 4% ↻2h15m │ 1w [▊░] 35% ↻3d6h │ git main +3 ✓
```

Antigravity가 `/usage` model quota row를 status line payload로 넘기면 ASW가 compact model quota segment를 추가합니다.

```text
mq G-f(M) [█░] 60% · G-f(H) 60% · G-f(L) 60% · G-p(L) 60% ↻6d22h
```

## Acknowledgements

ASW는 계획, 훅, 스킬, 진단, 리뷰 패턴을 Antigravity CLI 용어와 계약에 맞게 옮긴 프로젝트입니다.
