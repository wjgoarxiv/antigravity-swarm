# Antigravity Sub-Agents Skill 🚀

**AI 에이전트 팀을 고용하여 코딩 작업을 맡겨보세요.**

이 스킬은 Antigravity IDE 환경 내에서 여러 명의 전문 AI 에이전트(Sub-Agents)를 생성하여 복잡한 작업을 병렬로 처리할 수 있게 해줍니다. 터미널을 사용하든 Antigravity IDE를 사용하든, Architect, Engineer, Validator로 구성된 팀이 여러분의 문제를 효율적으로 해결해 드립니다.

> [!IMPORTANT] > **왜 이 스킬이 필요한가요?**
> 2026년 1월 18일 기준, Gemini CLI나 Antigravity IDE에는 서브에이전트를 배포할 수 있는 **네이티브 기능이 존재하지 않습니다.**
> 이 스킬은 그 공백을 메워, 여러분의 개발 환경에서 진정한 병렬 에이전트 오케스트레이션을 가능하게 합니다.

---

## 왜 이 스킬을 사용해야 하나요?

- **병렬 처리 (Parallel Execution)**: 한 명의 에이전트가 끝날 때까지 기다릴 필요가 없습니다. 3명의 에이전트를 동시에 실행하세요 (예: 한 명은 문서 작성, 한 명은 테스트 작성, 한 명은 코드 작성).
- **전문성 (Specialization)**: 각 에이전트에게 서로 다른 "페르소나"(프롬프트)를 부여하여 전문적인 작업을 수행하게 합니다.
- **품질 보증 (Quality Assurance)**: **[NEW]** 모든 팀에는 **Validator Agent(검증가)**가 필수적으로 포함되어, 작업 완료 전 결과물을 검토하고 높은 품질을 보장합니다.

---

## 설치 방법 (Installation)

1.  **스킬 위치 확인**: 이 리포지토리가 skills 폴더 안에 있는지 확인하세요:
    ```bash
    ~/.gemini/skills/antigravity-subagents/
    ```
2.  **의존성 패키지 설치**:

    ```bash
    pip install -r requirements.txt
    ```

    _(Requires `rich`, `pyyaml`, etc.)_

3.  **Gemini CLI**: `gemini` 명령어가 설치되어 있고 PATH에 등록되어 있어야 합니다.

---

## 사용 가이드 (User Manual)

이 스킬을 활용하는 두 가지 주요 방법이 있습니다.

### 🅰️ 시나리오 A: Gemini CLI (터미널 사용자용)

터미널에서 직접 팀을 "고용"하여 작업을 맡기고 싶을 때 사용하세요.

**Step 1: 팀 고용 (Plan)**
미션 내용을 입력하여 플래너(Planner)를 실행합니다.

```bash
python3 scripts/planner.py "뱀 게임을 만들어줘. 배경은 초록색이고 점수 기록 기능이 있어야 해."
```

**Step 2: 계획 검토 (Review)**
Planner는 다음 작업을 수행합니다:

1.  요청 사항 분석.
2.  최적의 팀 제안 (예: `Game_Designer`, `Python_Dev`, `Quality_Validator`).
3.  `task_plan.md` 초안 작성.
4.  사용자 확인 요청: `[Plan Mode] Save this configuration? [y/N]` -> `y` 입력.

**Step 3: 실행 (Orchestrate)**
승인 후, 팀을 출동시킵니다:

```bash
python3 scripts/orchestrator.py
```

_터미널 대시보드(TUI)를 통해 모든 에이전트가 동시에 일하는 모습을 볼 수 있습니다._

---

### 🅱️ 시나리오 B: Antigravity IDE (에이전트 사용자용)

IDE에서 Gemini Agent와 대화하던 중, 복잡한 작업을 에이전트가 자율적으로 처리하길 원할 때 사용됩니다.

**활성화 조건 (How to Trigger):**
이 스킬이 `~/.gemini/GEMINI.md`에 통합되어 있다면, 메인 에이전트는 다음 상황에서 **자동으로** 이 스킬을 호출합니다:

1.  작업이 **3개 이상의 파일 수정**을 필요로 할 때.
2.  작업에 **뚜렷한 전문성 분리**가 필요할 때 (예: "백엔드와 프론트엔드 둘 다 필요해").
3.  작업이 **병렬 처리**가 가능할 때.

**작동 방식:**

1.  메인 에이전트가 작업의 복잡성을 인지합니다.
2.  내부적으로 `planner.py`를 호출하여 팀을 설계합니다.
3.  `orchestrator.py`를 호출하여 작업을 실행합니다.
4.  Validator가 검증한 최종 결과를 사용자에게 보고합니다.

---

## 프로토콜 및 아키텍처 (Protocol & Architecture)

### "Manus Protocol"

이 스킬은 엄격한 상태 관리 프로토콜을 따릅니다:

- **`task_plan.md`**: 작업의 마스터 체크리스트.
- **`findings.md`**: 에이전트 간 지식을 공유하는 스크래치패드.
- **`progress.md`**: 수행한 작업의 불변 로그 (Log).

### "Validator" 규칙

설계상, 생성된 모든 팀의 **마지막 에이전트**는 반드시 **Quality Validator(품질 검증가)**여야 합니다.

- **역할**: 리뷰어 / QA.
- **임무**: `task_plan.md` 완료 여부 확인, 테스트 실행, 사용자 요구사항 충족 여부 검증.
- **이점**: 스스로 오류를 수정하는 루프(Self-correction loop)를 형성합니다.

---

## 디렉토리 구조 (Directory Structure)

```text
antigravity-subagents/
├── scripts/
│   ├── planner.py       # "Hiring Manager" (subagents.yaml 생성)
│   ├── orchestrator.py  # "Project Manager" (에이전트 실행 및 관리)
│   └── dispatch_agent.py # "Worker" (Gemini CLI 연동 Shim Layer)
├── subagents.yaml       # 현재 구성된 에이전트 명단
├── task_plan.md         # 현재 미션의 진행 상황
└── README.md            # 영문 설명서
```
