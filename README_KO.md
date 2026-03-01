# Antigravity Sub-Agents Skill 🚀

**AI 에이전트 팀을 고용하여 코딩 작업을 맡겨보세요.**

이 스킬은 Antigravity IDE 환경 내에서 여러 명의 전문 AI 에이전트(Sub-Agents)를 생성하여 복잡한 작업을 병렬로 처리할 수 있게 해줍니다. 터미널을 사용하든 Antigravity IDE를 사용하든, Architect, Engineer, Validator로 구성된 팀이 여러분의 문제를 효율적으로 해결해 드립니다.

```text
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                   ✨ Antigravity Swarm Mission Control ✨                      ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
┌──────────────┬──────────┬──────────────┬───────┬─────────┬─────────────────────┐
│ Agent        │ Role     │ Status       │ Time  │ Msgs    │ Backend             │
├──────────────┼──────────┼──────────────┼───────┼─────────┼─────────────────────┤
│ ● Oracle     │ parallel │ ⠋ Running    │ 12.3s │ ↑2 ↓1   │ tmux %3             │
│ ● Junior     │ parallel │ ⠋ Running    │ 10.1s │ ↑0 ↓1   │ tmux %4             │
│ ● Librarian  │ serial   │ • Pending    │ -     │ -       │ -                   │
│ ● Validator  │ validator│ • Pending    │ -     │ -       │ -                   │
└──────────────┴──────────┴──────────────┴───────┴─────────┴─────────────────────┘
┌─── Live Activity ──────────────────────────────────────────────────────────────┐
│ Oracle: Analyzing auth.py module structure...                                  │
└────────────────────────────────────────────────────────────────────────────────┘
[Tab] View  [w,s] Select  [k] Kill  [s] Shutdown  [q] Quit
```

### 에이전트 원샷 프롬프트 (업데이트/업그레이드)

```text
재설치 없이 이 레포를 안전하게 업데이트하고 재검증하세요.

레포 경로: <your-install-path>/antigravity-swarm

작업 순서:
1) 현재 git status와 branch 확인
2) 최신 변경사항 안전하게 pull (파괴적 명령 금지)
3) requirements.txt가 바뀐 경우에만 Python 의존성 갱신
4) 검증 실행
   - gemini --version
   - python3 -m py_compile scripts/*.py scripts/core/*.py scripts/core/backends/*.py
   - python3 scripts/orchestrator.py --demo
5) nvim/neovim 설정 파일이 이 레포에 존재하고 변경된 경우 적용/업데이트, 아니면 "nvim 업데이트 불필요" 보고

안전 규칙:
- 파괴적 git 명령 금지 (reset --hard, clean -fd, force push, checkout --)
- merge/rebase 충돌 발생 시 즉시 중단하고 충돌 파일 목록 보고

최종 보고 형식:
- Pull: 성공/실패
- 의존성 갱신: 수행/미수행
- 검증: 통과/실패
- nvim 업데이트: 적용/스킵
- 다음 액션: 1줄
```

> [!IMPORTANT]
> **왜 이 스킬이 필요한가요?**
> 2026-03-02 기준, Gemini CLI나 Antigravity IDE에는 서브에이전트를 배포할 수 있는 **네이티브 기능이 존재하지 않습니다.**
> 이 스킬은 그 공백을 메워, 여러분의 개발 환경에서 진정한 병렬 에이전트 오케스트레이션을 가능하게 합니다.

> [!NOTE]
> **Windows 호환성 (Windows Compatibility)**
> 이 스킬은 Windows PowerShell 환경(CP949/한국어 로케일)을 완벽하게 지원합니다. 모든 입출력 작업에 UTF-8 인코딩을 강제하여 인코딩 오류를 방지했습니다.

> [!WARNING]
> **Orchestrator가 실행 중일 때 `.swarm/` 디렉토리의 파일을 수정하지 마십시오.**
> 시스템은 메일박스, 감사 추적(audit trail), 미션 상태 파일을 실시간으로 읽고 씁니다.
> 실행 중에 수동으로 파일을 편집하면 경합 조건(Race Condition)이나 에이전트의 오작동을 유발할 수 있습니다.

> [!NOTE]
> **상태 파일 관리 (State Files Management)**
> 대규모 미션을 시작하면 시스템은 프로젝트 루트에 `.swarm/` 디렉토리를 자동으로 생성합니다.
> 이 디렉토리는 에이전트 스웜(Swarm)의 "공유 메모리" 및 통신 계층 역할을 합니다. 미션이 진행되는 동안에는 이 디렉토리를 삭제하지 마십시오.

---

## 왜 이 스킬을 사용해야 하나요?

- **병렬 처리 (Parallel Execution)**: 한 명의 에이전트가 끝날 때까지 기다릴 필요가 없습니다. 여러 에이전트를 동시에 실행하세요 (예: 한 명은 문서 작성, 한 명은 테스트 작성, 한 명은 코드 작성).
- **전문성 (Specialization)**: 각 에이전트에게 서로 다른 "페르소나"(프롬프트)를 부여하여 전문적인 작업을 수행하게 합니다.
- **품질 보증 (Quality Assurance)**: 모든 팀에는 **Validator Agent(검증가)**가 필수적으로 포함되어, 작업 완료 전 결과물을 검토하고 높은 품질을 보장합니다.
- **실시간 통신 (Live Communication)**: **[NEW v2]** 에이전트들이 메시지를 주고받으며 실시간으로 협업합니다.
- **인터랙티브 TUI (Interactive TUI)**: **[NEW v2]** 3가지 뷰(Dashboard, Messages, Agent Detail)로 미션 진행 상황을 실시간 모니터링합니다.
- **미션 재개 (Mission Resume)**: **[NEW v2]** 중단된 미션을 이어서 진행할 수 있습니다.

---

## v2 신규 기능

### 🔄 에이전트 간 실시간 통신
에이전트들은 파일 기반 JSON 메일박스 시스템을 통해 메시지를 주고받으며 협업합니다:
- **다이렉트 메시지**: `<<SEND_MESSAGE to="Agent명">>내용<</SEND_MESSAGE>>`
- **브로드캐스트**: `<<BROADCAST>>모든 에이전트에게 알림<</BROADCAST>>`
- **자동 라우팅**: 메시지는 `.swarm/mailboxes/{agent}/inbox/` 디렉토리로 자동 전달됩니다.

### 🎭 향상된 에이전트 라이프사이클
```
PENDING → RUNNING → IDLE → (폴링) → RUNNING → COMPLETED/FAILED/SHUTDOWN
```
- **IDLE 상태**: 작업 완료 후 대기 중인 에이전트는 새 메시지나 작업을 받을 수 있습니다.
- **하트비트 모니터링**: 응답 없는 에이전트 자동 감지 및 처리

### 📊 인터랙티브 TUI v2
3가지 뷰를 Tab 키로 전환:
1. **Dashboard View**: 6개 열로 모든 에이전트의 상태를 한눈에 확인 (Agent, Role, Status, Time, Msgs, Backend)
2. **Messages View**: 에이전트 간 메시지 타임라인 (누가, 언제, 무엇을, 누구에게)
3. **Agent Detail View**: 선택한 에이전트의 전체 출력 및 컨텍스트 확인

**키보드 단축키**:
- `Tab`: 뷰 전환 (Dashboard ↔ Messages ↔ Agent Detail)
- `w/s`: 에이전트 선택
- `Enter`: 선택한 에이전트 상세보기
- `k`: 선택한 에이전트 종료 (kill)
- `s`: 선택한 에이전트에게 셧다운 요청 전송
- `q`: 전체 미션 종료
- `Esc`: 상세보기에서 대시보드로 돌아가기
- `?`: 도움말 표시

### 🔌 백엔드 추상화
시스템이 사용 가능한 환경에 따라 최적의 백엔드를 자동 선택합니다:
- **Thread Backend** (기본값): 모든 환경에서 작동
- **Tmux Backend**: tmux가 설치되어 있으면 자동으로 활성화 (각 에이전트가 별도의 tmux 패널에서 실행)

### 📝 감사 추적 (Audit Trail)
모든 에이전트 활동이 `.swarm/audit/mission-{id}.jsonl` 파일에 append-only 형식으로 기록됩니다:
- 에이전트 상태 변경
- 메시지 송수신
- 작업 시작/완료
- 에러 및 경고

### 💾 미션 영속화 및 재개
미션 상태가 `.swarm/missions/mission-{id}.json`에 저장되어 중단된 작업을 재개할 수 있습니다:
```bash
# 마지막 미션 재개
python3 scripts/orchestrator.py --resume

# Ultrawork Loop에서 재개
python3 scripts/ultrawork_loop.py --resume
```

### 🎯 팀 프리셋 (Team Presets)
`swarm-config.yaml` 파일에서 재사용 가능한 팀 구성을 정의할 수 있습니다:
```bash
python3 scripts/planner.py --preset fullstack "Todo 앱 만들어줘"
```

프리셋 예시:
- `fullstack`: Oracle + Junior + Frontend + Validator
- `backend`: Oracle + Junior + Validator
- `research`: Librarian + Explore + Doc_Writer + Validator

### 📊 미션 완료 후 리포트
미션 종료 시 자동으로 요약 리포트가 생성됩니다:
- 총 실행 시간
- 에이전트별 통계 (실행 시간, 메시지 수, 상태)
- 성공/실패 여부
- 주요 이벤트 타임라인

### ⚡ 스트리밍 사이드 이펙트 파싱
에이전트 출력이 스트리밍되는 동안 실시간으로 태그를 감지하고 실행합니다:
- `<<SEND_MESSAGE>>`, `<<BROADCAST>>` 태그 즉시 처리
- `<<UPDATE_STATUS>>`, `<<REQUEST_WORK>>` 태그 실시간 반영
- 에이전트 응답 대기 시간 최소화

---

## 설치 방법 (Installation)

> [!TIP]
> 아래 블록을 그대로 LLM 에이전트에게 전달하면 설치/검증을 한 번에 수행할 수 있습니다.

```text
이 레포를 설치부터 검증까지 end-to-end로 수행하세요.

리포지토리: https://github.com/wjgoarxiv/antigravity-swarm
설치 경로: <your-install-path>/antigravity-swarm

작업 순서:
1) 위 경로에 clone 수행 (이미 있으면 삭제/초기화하지 말고 현재 상태만 보고)
2) requirements.txt 의존성 설치
3) 아래 검증 명령 실행
   - gemini --version
   - python3 -m py_compile scripts/*.py scripts/core/*.py scripts/core/backends/*.py
   - python3 scripts/orchestrator.py --demo
4) 이 레포에 nvim/neovim 설정 파일이 있으면 적용하고, 없으면 "nvim config 없음"으로 보고 후 계속 진행

안전 규칙:
- 첫 실패 지점에서 즉시 중단하고 실패 명령/원인을 보고
- 파괴적 git 명령 금지 (reset --hard, force push, checkout --, 기존 디렉토리 삭제)

최종 보고 형식:
- Clone: 성공/실패
- 의존성 설치: 성공/실패
- 검증: 통과/실패
- nvim 설정: 적용/스킵
- 다음 액션: 1줄
```

1.  **스킬 위치 확인**: 이 리포지토리가 skills 폴더 안에 있는지 확인하세요:
    ```bash
    ~/.gemini/skills/antigravity-swarm/
    ```
2.  **의존성 패키지 설치**:

    ```bash
    pip install -r requirements.txt
    ```

    _(Requires `rich`, `pyyaml`, etc.)_

3.  **Gemini CLI**: `gemini` 명령어가 설치되어 있고 PATH에 등록되어 있어야 합니다.

4.  **설정 파일 (선택사항)**: 프로젝트 루트에 `swarm-config.yaml` 파일을 생성하여 기본 설정을 커스터마이즈할 수 있습니다:
    ```yaml
    backend: auto                  # auto | tmux | thread
    default_model: auto-gemini-3
    max_parallel: 5
    poll_interval_ms: 1000
    audit_enabled: true
    tui_refresh_rate: 10

    # 팀 프리셋 정의
    presets:
      fullstack:
        - Oracle
        - Junior
        - Frontend
        - Quality_Validator
    ```

---

## 사용 가이드 (User Manual)

아래 3가지 경로 중 하나만 선택하면 됩니다.

### 경로 A: Gemini CLI (권장)

```bash
python3 scripts/planner.py --preset quick "미션 내용"
python3 scripts/orchestrator.py --yes
```

재개:

```bash
python3 scripts/orchestrator.py --resume
```

데모 (Gemini 없이 테스트):

```bash
python3 scripts/orchestrator.py --demo
```

### 경로 B: 자율 루프

```bash
python3 scripts/ultrawork_loop.py "미션 내용"
```

재개:

```bash
python3 scripts/ultrawork_loop.py --resume
```

### 경로 C: Antigravity IDE

`~/.gemini/GEMINI.md`에 이 스킬을 연결하면, 복잡한 작업에서 메인 에이전트가 자동 호출할 수 있습니다.

---

## 가용 에이전트 역할 (Oh-My-Opencode 표준)

Planner는 다음 전문가 풀에서 미션에 가장 적합한 에이전트를 자동으로 선발합니다:

| 역할 (Role) | 전문 분야 (Expertise) | 모델 (Model) |
|---|---|---|
| **Oracle** | 아키텍처, 심층 디버깅, 근본 원인 분석 | gemini-3-pro |
| **Librarian** | 문서 탐색, 코드 구조 파악, 리서치 | gemini-3-flash |
| **Explore** | 빠른 파일 검색, 패턴 매칭, 정찰 | gemini-3-flash |
| **Frontend** | UI/UX, 스타일링, 접근성 | gemini-3-flash |
| **Multimodal** | 시각 분석, 목업 이미지 해석 | gemini-3-pro |
| **Doc_Writer** | README, API 문서, 주석 작성 | gemini-3-flash |
| **Prometheus** | 전략 기획, 요구사항 구체화 | gemini-3-pro |
| **Momus** | 비판적 검토, 리스크 식별 | gemini-3-pro |
| **Sisyphus** | 작업 조율, 태스크 위임 (PM) | gemini-3-flash |
| **Junior** | 구현, 코딩, 버그 수정 | gemini-3-flash |
| **Quality_Validator** | 최종 검증 및 테스트 (필수 포함) | gemini-3-flash |

---

## 프로토콜 및 아키텍처 (Protocol & Architecture)

### "Manus Protocol" (파일 기반 상태 관리)

이 스킬은 엄격한 상태 관리 프로토콜을 따릅니다:

- **`task_plan.md`**: 작업의 마스터 체크리스트.
- **`findings.md`**: 에이전트 간 지식을 공유하는 스크래치패드.
- **`progress.md`**: 수행한 작업의 불변 로그 (Log).

### 메일박스 시스템 (Mailbox System) **[NEW v2]**

에이전트 간 실시간 통신을 위한 파일 기반 JSON 메일박스:

**디렉토리 구조**:
```
.swarm/mailboxes/
├── oracle/
│   ├── inbox/          # 읽지 않은 메시지
│   └── processed/      # 읽은 메시지
└── junior/
    ├── inbox/
    └── processed/
```

**메시지 태그**:
- `<<SEND_MESSAGE to="Agent명">>내용<</SEND_MESSAGE>>`: 특정 에이전트에게 메시지 전송
- `<<BROADCAST>>내용<</BROADCAST>>`: 모든 에이전트에게 메시지 브로드캐스트

**메시지 처리 흐름**:
1. 에이전트가 출력에 메시지 태그를 포함
2. Orchestrator가 실시간으로 태그 감지 및 파싱
3. 수신자의 `inbox/` 디렉토리에 JSON 파일로 저장
4. 수신 에이전트가 다음 폴링 시 메시지 수신
5. 읽은 메시지는 `processed/` 디렉토리로 이동

### "Validator" 규칙

설계상, 생성된 모든 팀의 **마지막 에이전트**는 반드시 **Quality Validator(품질 검증가)**여야 합니다.

- **역할**: 리뷰어 / QA.
- **임무**: `task_plan.md` 완료 여부 확인, 테스트 실행, 사용자 요구사항 충족 여부 검증.
- **이점**: 스스로 오류를 수정하는 루프(Self-correction loop)를 형성합니다.

---

## 디렉토리 구조 (Directory Structure)

```text
antigravity-swarm/
├── scripts/
│   ├── core/                    # [NEW] 공유 코어 패키지
│   │   ├── __init__.py
│   │   ├── config.py            # 중앙화된 설정 + get_gemini_path()
│   │   ├── types.py             # AgentStatus, MessageType, AgentIdentity
│   │   ├── mailbox.py           # 파일 기반 JSON 메일박스 시스템
│   │   ├── audit.py             # Append-only JSONL 감사 추적
│   │   ├── mission.py           # 미션 상태 영속화
│   │   └── backends/
│   │       ├── __init__.py      # get_backend() 팩토리
│   │       ├── base.py          # SpawnBackend ABC
│   │       ├── thread_backend.py
│   │       └── tmux_backend.py
│   ├── planner.py               # 팀 구성 + 프리셋 + 팀 설정
│   ├── orchestrator.py          # 인터랙티브 TUI v2 + 백엔드 + 메일박스
│   ├── dispatch_agent.py        # 에이전트 라이프사이클 + 스트리밍 파싱 + 메시징
│   ├── ultrawork_loop.py        # 자율 루프 + 재개 지원
│   ├── compactor.py             # 컨텍스트 압축
│   └── reporter.py              # [NEW] 미션 완료 후 요약 리포트
├── swarm-config.yaml            # [NEW] 사용자 설정 + 프리셋
├── SKILL.md
├── README.md
└── README_KO.md
```

### 런타임 디렉토리 (.swarm/) **[NEW v2]**

미션 실행 시 프로젝트 루트에 자동 생성되는 디렉토리:

```text
.swarm/
├── config.json                  # 팀 명단 (자동 생성)
├── mailboxes/
│   ├── oracle/
│   │   ├── inbox/               # 읽지 않은 메시지
│   │   └── processed/           # 읽은 메시지
│   └── junior/
│       ├── inbox/
│       └── processed/
├── audit/
│   └── mission-xyz.jsonl        # Append-only 감사 추적
└── missions/
    └── mission-xyz.json         # 미션 상태 (재개용)
```

---

## TUI 조작법 (TUI Controls) **[NEW v2]**

인터랙티브 TUI는 3가지 뷰를 제공합니다:

### Dashboard View (기본 뷰)
6개 열로 모든 에이전트의 상태를 한눈에 확인:
- **Agent**: 에이전트 이름 및 상태 아이콘
- **Role**: 에이전트 역할 (parallel/serial/validator)
- **Status**: 현재 상태 (Pending/Running/Idle/Completed/Failed)
- **Time**: 실행 시간
- **Msgs**: 메시지 통계 (↑ 송신, ↓ 수신)
- **Backend**: 실행 백엔드 (tmux 패널 번호 또는 thread)

### Messages View
에이전트 간 메시지 타임라인:
- 시간순 정렬
- 송신자 → 수신자 표시
- 메시지 내용 미리보기
- 브로드캐스트 메시지 하이라이트

### Agent Detail View
선택한 에이전트의 상세 정보:
- 전체 출력 로그
- 현재 컨텍스트
- 메시지 히스토리
- 상태 변경 이력

### 키보드 단축키

| 키 | 기능 |
|---|---|
| `Tab` | 뷰 전환 (Dashboard ↔ Messages ↔ Agent Detail) |
| `w/s` | 에이전트 선택 |
| `Enter` | 선택한 에이전트 상세보기 |
| `k` | 선택한 에이전트 강제 종료 (kill) |
| `s` | 선택한 에이전트에게 셧다운 요청 전송 |
| `q` | 전체 미션 종료 |
| `Esc` | 상세보기에서 대시보드로 돌아가기 |
| `?` | 도움말 표시 |

---

## 설정 (Configuration) **[NEW v2]**

`swarm-config.yaml` 파일을 프로젝트 루트에 생성하여 시스템 동작을 커스터마이즈할 수 있습니다:

```yaml
# 백엔드 선택 (auto: 자동 감지, tmux: tmux 강제, thread: thread 강제)
backend: auto

# 기본 모델
default_model: auto-gemini-3

# 최대 병렬 에이전트 수
max_parallel: 5

# 폴링 간격 (밀리초)
poll_interval_ms: 1000

# 권한 모드 (auto: 자동 승인, ask: 매번 확인, deny: 거부)
permission_mode: auto

# 감사 추적 활성화
audit_enabled: true

# TUI 갱신 주기 (Hz)
tui_refresh_rate: 10

# 컨텍스트 압축 임계값
compaction_threshold: 50

# 팀 프리셋 정의
presets:
  fullstack:
    - Oracle
    - Junior
    - Frontend
    - Quality_Validator

  backend:
    - Oracle
    - Junior
    - Quality_Validator

  research:
    - Librarian
    - Explore
    - Doc_Writer
    - Quality_Validator
```

### 프리셋 사용

프리셋을 사용하여 미리 정의된 팀 구성으로 빠르게 시작:

```bash
python3 scripts/planner.py --preset fullstack "Todo 앱 만들어줘"
python3 scripts/planner.py --preset backend "API 엔드포인트 추가해줘"
python3 scripts/planner.py --preset research "React 최신 패턴 조사해줘"
```

---

## 고급 기능 (Advanced Features)

### 미션 재개 (Mission Resume)

중단된 미션을 재개할 수 있습니다:

```bash
# Orchestrator로 재개
python3 scripts/orchestrator.py --resume

# Ultrawork Loop로 재개
python3 scripts/ultrawork_loop.py --resume
```

시스템은 `.swarm/missions/` 디렉토리에서 가장 최근 미션을 자동으로 찾아 재개합니다.

### 감사 추적 (Audit Trail)

모든 에이전트 활동이 `.swarm/audit/mission-{id}.jsonl` 파일에 기록됩니다:

```jsonl
{"timestamp": "<ISO_TIMESTAMP>", "event": "agent_started", "agent": "oracle", "data": {...}}
{"timestamp": "<ISO_TIMESTAMP>", "event": "message_sent", "from": "oracle", "to": "junior", "content": "..."}
{"timestamp": "<ISO_TIMESTAMP>", "event": "status_changed", "agent": "oracle", "from": "running", "to": "idle"}
```

### 데모 모드 (Demo Mode)

Gemini CLI 없이도 TUI를 테스트할 수 있습니다:

```bash
python3 scripts/orchestrator.py --demo
```

모의(mock) 에이전트들이 실행되어 TUI와 메시징 시스템을 시연합니다.

---

## ⭐️ Credits & Inspiration

이 프로젝트는 **[Oh-My-Opencode](https://github.com/code-yeongyu/oh-my-opencode)**에서 깊은 영감을 받았습니다.

해당 프로젝트를 구축 시, 하기의 핵심 철학들을 차용했습니다:
- **멀티 에이전트 오케스트레이션 (Multi-Agent Orchestration)**: Oracle, Librarian, Sisyphus 등 특화된 역할을 활용합니다.
- **Manus 프로토콜 (The "Manus Protocol")**: `task_plan.md`, `findings.md`와 같은 영구 파일로 상태를 관리합니다. 이 패턴은 **[planning-with-files](https://github.com/OthmanAdi/planning-with-files)**에서 깊은 영감을 받았습니다.
- **Ultrawork Loop**: 자율적인 "계획 -> 실행 -> 검증" 사이클을 구현했습니다.

원작자 분들께 감사의 말씀을 전합니다.
