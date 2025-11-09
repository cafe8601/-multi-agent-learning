# 🏗️ Multi-Agent Learning System - 완전 작동 메커니즘

## 📋 목차
1. [전체 시스템 아키텍처](#1-전체-시스템-아키텍처)
2. [사용자 요청 처리 흐름](#2-사용자-요청-처리-흐름)
3. [에이전트 간 상호작용](#3-에이전트-간-상호작용)
4. [고급 시스템 통합](#4-고급-시스템-통합)
5. [데이터 흐름 및 메모리 관리](#5-데이터-흐름-및-메모리-관리)
6. [실제 작동 예시](#6-실제-작동-예시)

---

## 1. 전체 시스템 아키텍처

### 1.1 고수준 아키텍처

```mermaid
graph TB
    User[👤 사용자<br/>음성/텍스트]

    subgraph "🎙️ OpenAI Realtime Voice Agent (오케스트레이터)"
        ORVA[OpenAI Realtime API<br/>WebSocket 연결]
        Session[SessionManager<br/>토큰 추적]
        Audio[AudioInterface<br/>음성 입출력]
        WSHandler[WebSocketHandlers<br/>이벤트 처리]
        MsgProc[MessageProcessor<br/>메시지 파싱]
        FuncHandler[FunctionHandler<br/>도구 실행]
        InputLoop[InputHandler<br/>입력 처리]
    end

    subgraph "🤖 실행 에이전트들"
        Claude[💻 Claude Code Agent<br/>코드 생성/수정]
        Gemini[🌐 Gemini Browser Agent<br/>브라우저 자동화]
        Pool[🎯 Agent Pool<br/>159개 전문 에이전트]
    end

    subgraph "🧠 고급 시스템"
        Memory[💾 Memory System<br/>세션/워크플로우/컨텍스트]
        Workflow[⚡ Workflow System<br/>멀티태스크 오케스트레이션]
        Learning[📚 Learning System<br/>패턴 분석/추천]
        Security[🔒 Security System<br/>감사/접근제어]
        RAG[🔍 RAG System<br/>벡터 검색/컨텍스트]
    end

    subgraph "💾 저장소"
        Files[📁 파일 시스템<br/>apps/content-gen/]
        Registry[📝 레지스트리<br/>agents/*/registry.json]
        Storage[🗄️ 영구 저장소<br/>storage/]
    end

    User -->|음성/텍스트| ORVA
    ORVA --> Session
    ORVA --> Audio
    ORVA --> WSHandler
    WSHandler --> MsgProc
    MsgProc --> FuncHandler

    FuncHandler -->|create_agent| Claude
    FuncHandler -->|browser_use| Gemini
    FuncHandler -->|create_pool_agent| Pool

    Claude --> Files
    Gemini --> Files
    Pool --> Files

    Claude --> Registry
    Gemini --> Registry

    FuncHandler --> Memory
    FuncHandler --> Workflow
    FuncHandler --> Learning
    FuncHandler --> Security

    Memory --> Storage
    Learning --> Storage
    Security --> Storage
    RAG --> Storage

    Claude -.피드백.-> ORVA
    Gemini -.피드백.-> ORVA
    Pool -.피드백.-> ORVA
```

### 1.2 컴포넌트 상세 설명

#### 🎙️ OpenAI Realtime Voice Agent (오케스트레이터)
**역할:** 전체 시스템의 중앙 제어 타워
- **입력:** 사용자의 음성 또는 텍스트 명령
- **출력:** 음성 또는 텍스트 응답
- **핵심 기능:**
  - 실시간 음성 스트리밍 (24kHz, 16-bit PCM)
  - WebSocket 기반 양방향 통신
  - 함수 호출 기반 도구 실행
  - 세션 토큰 추적 및 비용 계산

#### 💻 Claude Code Agent
**역할:** 자율적 소프트웨어 개발
- **기술:** Anthropic Claude SDK
- **작업 디렉토리:** `apps/content-gen/`
- **핵심 기능:**
  - 에이전트 생성 및 세션 관리
  - 코드 생성/수정/리팩토링
  - MCP 서버 통합 (browser_use 등)
  - 실시간 로그 스트리밍

#### 🌐 Gemini Browser Agent
**역할:** 웹 브라우저 자동화
- **기술:** Playwright + Gemini Computer Use API
- **해상도:** 1440x900
- **핵심 기능:**
  - 스크린샷 기반 작업 수행
  - 클릭, 타이핑, 네비게이션
  - 최대 30턴 자동화 루프
  - 작업 기록 및 재현

#### 🎯 Agent Pool (159개)
**역할:** 전문화된 에이전트 집합
- **구조:** 3-Tier (Core/Specialized/Experimental)
- **동적 로딩:** Markdown 파일 기반
- **핵심 기능:**
  - 작업 분석 및 최적 에이전트 선택
  - 인스턴스 재사용 (idle pool)
  - 자동 리소스 정리

---

## 2. 사용자 요청 처리 흐름

### 2.1 전체 흐름도

```mermaid
sequenceDiagram
    participant U as 👤 사용자
    participant OA as 🎙️ OpenAI Agent
    participant WS as 🔌 WebSocket
    participant FH as 🔧 FunctionHandler
    participant CA as 💻 Claude Agent
    participant GB as 🌐 Gemini Agent
    participant FS as 📁 파일시스템

    U->>OA: 음성/텍스트 명령<br/>"Create a hello world app"
    activate OA

    OA->>WS: session.update<br/>(시스템 프롬프트 + 도구 목록)
    OA->>WS: conversation.item.create<br/>(사용자 메시지)
    OA->>WS: response.create<br/>(응답 생성 요청)

    WS-->>OA: response.output_item.added<br/>(AI가 function_call 결정)
    WS-->>OA: response.function_call_arguments.delta<br/>(인자 스트리밍)

    OA->>FH: response.done<br/>(함수 실행 트리거)
    activate FH

    alt 코드 생성 작업
        FH->>CA: create_agent(agent_name)
        activate CA
        CA->>CA: 세션 생성 및 초기화
        CA-->>FH: {ok: true, session_id: "..."}
        deactivate CA

        FH->>CA: command_agent(agent_name, prompt)
        activate CA
        CA->>FS: 코드 작성/수정
        FS-->>CA: 완료
        CA->>CA: operator 파일 생성
        CA-->>FH: {ok: true, operator_file: "..."}
        deactivate CA

    else 브라우저 작업
        FH->>GB: browser_use(task, url)
        activate GB
        GB->>GB: Playwright 브라우저 시작

        loop 최대 30턴
            GB->>GB: 스크린샷 캡처
            GB->>GB: Gemini API 호출
            GB->>GB: 액션 실행 (클릭/타이핑)
            GB->>GB: 작업 완료 확인
        end

        GB->>FS: 결과 저장
        GB-->>FH: {ok: true, result: "..."}
        deactivate GB
    end

    FH->>WS: conversation.item.create<br/>(함수 실행 결과)
    deactivate FH

    WS-->>OA: response.audio.delta<br/>(음성 응답 스트리밍)
    OA->>U: 음성/텍스트 응답<br/>"✅ App created successfully"
    deactivate OA
```

### 2.2 단계별 상세 설명

#### Step 1: 사용자 입력 수신
```typescript
// 입력 모드
- audio: 마이크로부터 실시간 오디오 스트리밍
- text: 터미널 stdin으로부터 텍스트 입력

// 처리
InputHandler.handle_input()
  → AudioInterface.capture_audio() (audio 모드)
  → WebSocket.send(audio_chunk) (base64 인코딩)
```

#### Step 2: OpenAI Realtime API 처리
```typescript
// WebSocket 이벤트 흐름
1. session.update
   - 시스템 프롬프트 설정
   - 사용 가능한 도구 목록 전송
   - 음성 설정 (voice: "shimmer")

2. conversation.item.create
   - 사용자 메시지를 대화에 추가
   - 타입: audio or text

3. response.create
   - AI가 응답 생성 시작
   - 도구 호출 여부 결정

4. response.done
   - 응답 완료
   - 함수 호출 실행 트리거
```

#### Step 3: 함수 호출 실행
```python
# FunctionHandler.execute_tool_call()
tool_routing = {
    "create_agent": AgentTools.create_agent,
    "command_agent": AgentTools.command_agent,
    "browser_use": BrowserTools.browser_use,
    "list_agents": AgentTools.list_agents,
    "read_file": FilesystemTools.read_file,
    "write_file": FilesystemTools.write_file,
    # ... 15+ more tools
}

# 실행 및 결과 반환
result = tool_routing[tool_name](**args)
return json.dumps(result)
```

#### Step 4: 에이전트 실행
```python
# Claude Agent 실행 예시
def command_agent(agent_name: str, prompt: str):
    # 1. 레지스트리에서 세션 로드
    session = registry.get(agent_name)

    # 2. 백그라운드 스레드에서 실행
    thread = threading.Thread(
        target=execute_command,
        args=(session, prompt)
    )
    thread.start()

    # 3. operator 파일 생성 (실시간 로그)
    operator_file = f"operators/{timestamp}_task.md"

    # 4. 결과 반환
    return {
        "ok": True,
        "operator_file": operator_file,
        "message": "Command dispatched"
    }
```

---

## 3. 에이전트 간 상호작용

### 3.1 멀티 에이전트 협업 시나리오

```mermaid
graph LR
    subgraph "시나리오: 웹 앱 개발 및 테스트"
        U[👤 사용자<br/>"Create and test<br/>a login page"]
    end

    subgraph "Phase 1: 분석 및 계획"
        O1[🎙️ OpenAI<br/>작업 분석]
        M1[💾 Memory<br/>컨텍스트 저장]
    end

    subgraph "Phase 2: 개발"
        C1[💻 Claude<br/>backend-dev]
        C2[💻 Claude<br/>frontend-dev]
        F1[📁 Files<br/>API 코드]
        F2[📁 Files<br/>UI 코드]
    end

    subgraph "Phase 3: 테스트"
        G1[🌐 Gemini<br/>브라우저 시작]
        G2[🌐 Gemini<br/>로그인 테스트]
        G3[🌐 Gemini<br/>결과 검증]
    end

    subgraph "Phase 4: 보고"
        L1[📚 Learning<br/>결과 기록]
        S1[🔒 Security<br/>감사 로그]
        O2[🎙️ OpenAI<br/>사용자 보고]
    end

    U --> O1
    O1 --> M1

    O1 -->|create_agent<br/>backend-dev| C1
    O1 -->|create_agent<br/>frontend-dev| C2

    C1 --> F1
    C2 --> F2

    F1 -->|API 완료| O1
    F2 -->|UI 완료| O1

    O1 -->|browser_use<br/>test login| G1
    G1 --> G2
    G2 --> G3

    G3 -->|결과| O1

    O1 --> L1
    O1 --> S1
    O1 --> O2

    O2 --> U
```

### 3.2 에이전트 생명주기

```mermaid
stateDiagram-v2
    [*] --> 생성요청

    생성요청 --> 세션초기화: create_agent()
    세션초기화 --> 레지스트리등록
    레지스트리등록 --> IDLE: 대기 상태

    IDLE --> ACTIVE: command 수신
    ACTIVE --> 작업실행: 백그라운드 스레드
    작업실행 --> 로그기록: operator 파일
    로그기록 --> 결과저장
    결과저장 --> IDLE: 작업 완료

    IDLE --> IDLE: 재사용 (30분 타임아웃)
    IDLE --> 정리: cleanup_idle()
    정리 --> [*]

    ACTIVE --> ERROR: 예외 발생
    ERROR --> 복구시도
    복구시도 --> IDLE: 성공
    복구시도 --> 정리: 실패
```

---

## 4. 고급 시스템 통합

### 4.1 시스템 간 통합 아키텍처

```mermaid
graph TB
    subgraph "🎛️ 오케스트레이터 레이어"
        OA[OpenAI Realtime Agent]
        OI[OrchestratorIntegration]
    end

    subgraph "🧠 고급 시스템 레이어"
        subgraph "Agent Pool"
            PM[PoolManager<br/>159 experts]
            ES[ExpertSelector<br/>AI 기반 선택]
            IE[InstanceExecutor<br/>실행 관리]
        end

        subgraph "Memory System"
            SM[SessionMemory<br/>임시 데이터]
            WM[WorkflowMemory<br/>실행 이력]
            CS[ContextStore<br/>프로젝트 컨텍스트]
            RS[RAGSystem<br/>벡터 검색]
        end

        subgraph "Workflow System"
            WP[WorkflowPlanner<br/>작업 분해]
            EE[ExecutionEngine<br/>병렬/순차 실행]
            WV[WorkflowValidator<br/>검증]
            WR[WorkflowReflector<br/>회고]
        end

        subgraph "Learning System"
            OT[OutcomeTracker<br/>결과 추적]
            PA[PatternAnalyzer<br/>패턴 분석]
            LM[LearningManager<br/>추천]
        end

        subgraph "Security System"
            AC[AccessControl<br/>권한 관리]
            AL[AuditLogger<br/>감사 로그]
            SM2[SecurityManager<br/>정책 적용]
        end
    end

    subgraph "💾 저장소 레이어"
        FS[(파일시스템)]
        VDB[(ChromaDB<br/>벡터 DB)]
        Redis[(Redis<br/>캐시)]
    end

    OA --> OI

    OI --> PM
    OI --> SM
    OI --> WP
    OI --> LM
    OI --> SM2

    PM --> ES
    ES --> IE

    SM --> FS
    WM --> FS
    CS --> FS
    RS --> VDB

    WP --> EE
    EE --> WV
    WV --> WR

    OT --> PA
    PA --> LM

    AC --> AL
    AL --> FS

    SM --> Redis
```

### 4.2 고급 기능 예시

#### 4.2.1 Agent Pool - 지능형 에이전트 선택
```python
# 사용자: "Optimize database queries"
#
# 1. ExpertSelector가 작업 분석
task_embedding = sentence_transformer.encode(
    "Optimize database queries"
)

# 2. 전문가 매칭
candidates = [
    "database-optimizer",    # 전문도: 95%
    "backend-developer",     # 전문도: 75%
    "performance-expert",    # 전문도: 85%
]

# 3. 최적 선택
selected = expert_selector.select_expert(task)
# → "database-optimizer"

# 4. 인스턴스 재사용 또는 생성
instance = pool_manager.get_or_create_instance(
    agent_id="database-optimizer",
    task=task
)
```

#### 4.2.2 Workflow System - 멀티 태스크 오케스트레이션
```python
# 복잡한 작업: "Build e-commerce site"
#
# 1. WorkflowPlanner가 작업 분해
plan = workflow_planner.create_multi_task_plan(
    goal="Build e-commerce site",
    tasks=[
        {
            "description": "Design database schema",
            "agent_id": "database-architect",
            "duration": 300
        },
        {
            "description": "Create REST API",
            "agent_id": "backend-developer",
            "duration": 600,
            "dependencies": ["task_1"]
        },
        {
            "description": "Build product catalog UI",
            "agent_id": "frontend-developer",
            "duration": 600,
            "dependencies": ["task_2"]
        },
        {
            "description": "Setup payment gateway",
            "agent_id": "payment-integration-expert",
            "duration": 400,
            "dependencies": ["task_2"]
        }
    ],
    strategy=ExecutionStrategy.PARALLEL  # task_3, task_4 병렬
)

# 2. ExecutionEngine이 실행
result = await execution_engine.execute(plan)

# 3. WorkflowValidator가 검증
validation = workflow_validator.validate_execution(plan, result)

# 4. WorkflowReflector가 회고
reflection = workflow_reflector.reflect(plan, result)
# → "Task 3 took longer than expected. Consider splitting UI work."
```

#### 4.2.3 RAG System - 컨텍스트 증강
```python
# 코드 작성 시 유사 사례 검색
#
# 1. 사용자 요청
prompt = "Create user authentication API"

# 2. RAG System이 유사 코드 검색
similar_code = rag_system.search(
    query=prompt,
    top_k=5,
    filters={"type": "api", "topic": "auth"}
)

# 3. 컨텍스트 증강
augmented_prompt = f"""
{prompt}

## Similar implementations found:
{similar_code}

Please create a new implementation following these patterns.
"""

# 4. Claude Agent에 전달
result = claude_agent.command(augmented_prompt)
```

---

## 5. 데이터 흐름 및 메모리 관리

### 5.1 데이터 흐름

```mermaid
graph LR
    subgraph "입력"
        U1[사용자 음성]
        U2[사용자 텍스트]
    end

    subgraph "처리 파이프라인"
        A1[오디오 캡처<br/>24kHz PCM]
        A2[WebSocket<br/>base64 전송]
        A3[OpenAI API<br/>STT + LLM]
        A4[Function Call<br/>결정]
        A5[Tool Execution<br/>실행]
    end

    subgraph "에이전트 실행"
        C1[Claude API]
        G1[Gemini API]
        P1[Playwright]
    end

    subgraph "출력"
        O1[파일 시스템<br/>코드/문서]
        O2[스크린샷<br/>PNG]
        O3[로그<br/>JSON/MD]
        O4[음성 응답<br/>오디오]
        O5[텍스트 응답<br/>터미널]
    end

    U1 --> A1
    U2 --> A2
    A1 --> A2
    A2 --> A3
    A3 --> A4
    A4 --> A5

    A5 --> C1
    A5 --> G1
    G1 --> P1

    C1 --> O1
    P1 --> O2
    A5 --> O3
    A3 --> O4
    A3 --> O5
```

### 5.2 메모리 계층

```mermaid
graph TB
    subgraph "L1: 인메모리 캐시 (휘발성)"
        S1[Session Data<br/>현재 대화]
        S2[Active Instances<br/>에이전트 상태]
        S3[Token Count<br/>비용 추적]
    end

    subgraph "L2: 로컬 파일 (영구)"
        F1[Registry JSON<br/>agents/*/registry.json]
        F2[Operator Files<br/>operators/*.md]
        F3[Code Output<br/>apps/content-gen/]
    end

    subgraph "L3: 데이터베이스 (구조화)"
        D1[WorkflowMemory<br/>실행 이력]
        D2[ContextStore<br/>프로젝트 컨텍스트]
        D3[AuditLog<br/>보안 감사]
    end

    subgraph "L4: 벡터 DB (검색)"
        V1[ChromaDB<br/>코드 임베딩]
        V2[SentenceTransformer<br/>의미 검색]
    end

    S1 -.TTL 30분.-> F1
    S2 -.idle timeout.-> F1

    F2 --> D1
    F3 --> D2

    D2 --> V1
    V1 --> V2
```

---

## 6. 실제 작동 예시

### 6.1 시나리오: "Create a FastAPI hello world app and test it"

#### 타임라인 다이어그램
```mermaid
gantt
    title 멀티 에이전트 작업 타임라인
    dateFormat  ss

    section OpenAI
    사용자 입력 수신           :a1, 00, 2s
    작업 분석                :a2, after a1, 3s
    Claude 에이전트 생성      :a3, after a2, 2s
    Claude 명령 전달          :a4, after a3, 1s
    Gemini 브라우저 시작      :a5, after a4, 2s
    결과 통합 및 응답         :a6, after a5, 2s

    section Claude
    세션 초기화              :c1, after a3, 2s
    FastAPI 코드 작성        :c2, after c1, 15s
    Requirements.txt 생성    :c3, after c2, 2s
    Operator 파일 작성       :c4, after c3, 1s

    section Gemini
    Playwright 브라우저 시작  :g1, after a5, 3s
    localhost:8000 접속      :g2, after g1, 2s
    Hello World 확인         :g3, after g2, 2s
    스크린샷 캡처           :g4, after g3, 1s
    결과 반환               :g5, after g4, 1s
```

#### 상세 단계별 실행

```mermaid
sequenceDiagram
    autonumber
    participant U as 👤 사용자
    participant O as 🎙️ OpenAI Agent
    participant M as 💾 Memory
    participant C as 💻 Claude Agent
    participant G as 🌐 Gemini Agent
    participant F as 📁 파일시스템

    Note over U,F: Phase 1: 분석 (0-5초)
    U->>O: "Create FastAPI hello world<br/>and test it"
    O->>M: 컨텍스트 저장
    O->>O: 작업 분해:<br/>1) 코드 생성<br/>2) 테스트

    Note over U,F: Phase 2: 코드 생성 (5-25초)
    O->>C: create_agent("backend-dev")
    C->>C: 세션 초기화
    C->>F: registry.json 생성
    C-->>O: {ok: true, agent_id: "backend-dev-001"}

    O->>C: command_agent("backend-dev",<br/>"Create FastAPI hello world")
    activate C

    C->>F: main.py 작성
    Note right of F: from fastapi import FastAPI<br/>app = FastAPI()<br/>@app.get("/")<br/>def hello():<br/>    return {"msg": "Hello World"}

    C->>F: requirements.txt 작성
    Note right of F: fastapi==0.104.0<br/>uvicorn==0.24.0

    C->>F: operators/20251109_120530_task.md 작성
    Note right of F: ## Task: Create FastAPI app<br/>✅ Created main.py<br/>✅ Created requirements.txt

    C-->>O: {ok: true, operator_file: "..."}
    deactivate C

    Note over U,F: Phase 3: 앱 시작 및 테스트 준비 (25-30초)
    O->>F: read_file("main.py")
    F-->>O: {content: "..."}

    O->>O: 판단: 앱이 실행되어야<br/>브라우저 테스트 가능

    rect rgb(255, 240, 200)
        Note over O: 사용자에게 수동 실행 안내<br/>또는 자동 실행 시스템 필요
    end

    Note over U,F: Phase 4: 브라우저 테스트 (30-40초)
    O->>G: browser_use({<br/>  task: "Navigate to localhost:8000<br/>        and verify Hello World",<br/>  url: "http://localhost:8000"<br/>})

    activate G
    G->>G: Playwright 브라우저 시작
    G->>G: localhost:8000 접속
    G->>G: 스크린샷 캡처
    G->>G: Gemini: "What do you see?"
    G->>G: Gemini: "I see Hello World JSON"
    G->>F: screenshot_001.png 저장
    G-->>O: {ok: true, result: "✅ Verified"}
    deactivate G

    Note over U,F: Phase 5: 결과 보고 (40-42초)
    O->>M: 성공 결과 기록
    O->>U: 🎤 "I've created a FastAPI app<br/>and verified it works!"
```

### 6.2 실행 로그 예시

```bash
[2025-11-09 12:05:30] INFO: OpenAI Realtime Agent started
[2025-11-09 12:05:30] INFO: Input: text, Output: text
[2025-11-09 12:05:30] INFO: WebSocket connected: wss://api.openai.com/v1/realtime

[2025-11-09 12:05:32] USER: Create a FastAPI hello world app and test it

[2025-11-09 12:05:35] INFO: Function call: create_agent
[2025-11-09 12:05:35] INFO: Arguments: {"agent_name": "backend-dev"}
[2025-11-09 12:05:37] SUCCESS: Agent created: backend-dev-001
[2025-11-09 12:05:37] INFO: Session: 20251109_120537_abc123

[2025-11-09 12:05:38] INFO: Function call: command_agent
[2025-11-09 12:05:38] INFO: Arguments: {
  "agent_name": "backend-dev",
  "prompt": "Create a simple FastAPI hello world app with these files: main.py and requirements.txt"
}
[2025-11-09 12:05:38] INFO: Command dispatched to agent: backend-dev-001
[2025-11-09 12:05:38] INFO: Operator file: operators/20251109_120538_task.md

[2025-11-09 12:05:40] INFO: Agent output streaming...
[2025-11-09 12:05:45] INFO: ✅ Created main.py (15 lines)
[2025-11-09 12:05:47] INFO: ✅ Created requirements.txt (2 lines)
[2025-11-09 12:05:53] SUCCESS: Agent task completed

[2025-11-09 12:05:55] INFO: Function call: browser_use
[2025-11-09 12:05:55] INFO: Arguments: {
  "task": "Navigate to localhost:8000 and verify Hello World message",
  "url": "http://localhost:8000"
}
[2025-11-09 12:05:56] INFO: Starting Playwright browser (1440x900)
[2025-11-09 12:05:59] INFO: Navigated to http://localhost:8000
[2025-11-09 12:06:01] INFO: Screenshot captured: screenshot_001.png
[2025-11-09 12:06:03] INFO: Gemini analysis: "Page displays JSON: {\"msg\": \"Hello World\"}"
[2025-11-09 12:06:05] SUCCESS: Browser task completed

[2025-11-09 12:06:07] ASSISTANT: ✅ I've successfully created a FastAPI hello world application and verified it works! The app returns {"msg": "Hello World"} at the root endpoint.

[2025-11-09 12:06:07] INFO: Token usage - Input: 1250, Output: 850, Total: 2100
[2025-11-09 12:06:07] INFO: Estimated cost: $0.035
```

### 6.3 생성된 파일 구조

```
apps/content-gen/
├── agents/
│   ├── claude_code/
│   │   ├── registry.json              # 에이전트 세션 정보
│   │   └── backend-dev-001/
│   │       └── operators/
│   │           └── 20251109_120538_task.md  # 작업 로그
│   └── gemini/
│       ├── registry.json
│       └── browser-001/
│           └── screenshots/
│               └── screenshot_001.png  # 브라우저 검증 스크린샷
├── main.py                            # FastAPI 앱
├── requirements.txt                   # 의존성
└── storage/                           # 영구 저장소
    ├── memory/                        # 메모리 시스템
    ├── learning/                      # 학습 데이터
    └── security/                      # 감사 로그
```

---

## 7. 핵심 기술 스택

### 7.1 API 및 SDK

```mermaid
graph LR
    subgraph "외부 API"
        OA[OpenAI Realtime API<br/>WebSocket<br/>gpt-realtime-2025-08-28]
        CA[Anthropic Claude API<br/>REST<br/>claude-sonnet-4-5]
        GA[Google Gemini API<br/>REST<br/>gemini-2.5-computer-use]
    end

    subgraph "통합 레이어"
        WS[websocket-client<br/>12.0]
        AN[anthropic SDK<br/>0.39.0]
        GG[google-generativeai<br/>0.8.0]
        PW[Playwright<br/>1.48.0]
    end

    subgraph "애플리케이션"
        RA[Realtime Agent]
        CC[Claude Coder]
        GB[Gemini Browser]
    end

    OA --> WS
    CA --> AN
    GA --> GG
    GA --> PW

    WS --> RA
    AN --> CC
    GG --> GB
    PW --> GB
```

### 7.2 데이터 처리

```mermaid
graph TB
    subgraph "오디오 처리"
        SD[sounddevice<br/>실시간 캡처]
        NP[NumPy<br/>배열 처리]
        PD[pydub<br/>포맷 변환]
    end

    subgraph "데이터 검증"
        PY[Pydantic<br/>타입 검증]
        DV[python-dotenv<br/>환경 변수]
    end

    subgraph "벡터 검색"
        CB[ChromaDB<br/>벡터 DB]
        ST[SentenceTransformers<br/>임베딩]
    end

    subgraph "보안"
        CR[cryptography<br/>암호화]
        JO[python-jose<br/>JWT]
    end
```

---

## 8. 성능 특성

### 8.1 응답 시간

| 작업 유형 | 평균 시간 | 설명 |
|---------|----------|------|
| 음성 인식 (STT) | 0.5-1초 | OpenAI Realtime API |
| 텍스트 처리 | 즉시 | 직접 전송 |
| 에이전트 생성 | 2-3초 | 세션 초기화 |
| 간단한 코드 생성 | 5-15초 | Claude API 호출 |
| 복잡한 코드 생성 | 30-60초 | 여러 파일, 컨텍스트 |
| 브라우저 작업 | 10-30초 | 최대 30턴 루프 |
| 음성 응답 (TTS) | 실시간 스트리밍 | 청크별 재생 |

### 8.2 리소스 사용

```mermaid
pie title 토큰 사용 분포 (평균)
    "시스템 프롬프트" : 1000
    "사용자 입력" : 500
    "에이전트 응답" : 2000
    "함수 호출 결과" : 1500
    "최종 응답" : 1000
```

### 8.3 확장성

- **동시 에이전트:** 제한 없음 (레지스트리 기반)
- **에이전트 풀:** 159개 (동적 로딩)
- **세션 관리:** 영구 (JSON 파일)
- **인스턴스 재사용:** 최대 3개/타입
- **타임아웃:** 30분 idle

---

## 9. 보안 및 감사

### 9.1 보안 계층

```mermaid
graph TB
    subgraph "접근 제어"
        P1[Permission System<br/>CRUD 권한]
        P2[Policy Engine<br/>조건부 검증]
    end

    subgraph "감사 로깅"
        A1[Event Logging<br/>모든 작업 기록]
        A2[User Tracking<br/>사용자 추적]
    end

    subgraph "데이터 보호"
        E1[환경 변수<br/>API 키 분리]
        E2[.gitignore<br/>민감 정보 제외]
    end

    P1 --> A1
    P2 --> A1
    A1 --> A2
```

### 9.2 감사 이벤트

```python
# 감사 대상 이벤트
AUDIT_EVENTS = [
    "agent_created",       # 에이전트 생성
    "agent_commanded",     # 명령 실행
    "browser_used",        # 브라우저 사용
    "file_read",          # 파일 읽기
    "file_written",       # 파일 쓰기
    "workflow_executed",   # 워크플로우 실행
    "auth_failure",       # 인증 실패
    "permission_denied",   # 권한 거부
]

# 로그 형식
{
    "timestamp": "2025-11-09T12:05:30Z",
    "event_type": "agent_created",
    "user": "system",
    "data": {
        "agent_id": "backend-dev-001",
        "session_id": "20251109_120530_abc123"
    },
    "severity": "info"
}
```

---

## 10. 결론

### 10.1 시스템 강점

✅ **완전한 구현**: 모든 핵심 컴포넌트 작동 가능
✅ **모듈화 설계**: 명확한 책임 분리
✅ **확장 가능**: 159개 에이전트, 무제한 세션
✅ **실시간 스트리밍**: 음성/로그 실시간 처리
✅ **멀티 에이전트**: 3개 에이전트 조율
✅ **고급 기능**: Memory, Workflow, Learning, Security
✅ **프로덕션 레벨**: 에러 처리, 로깅, 감사

### 10.2 실행 요구사항

```bash
# 1. API 키
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...  # 또는 Claude Max 구독
GEMINI_API_KEY=...

# 2. 의존성
pip install -r requirements.txt
playwright install chromium

# 3. 실행
python -m big_three_realtime_agents.main
```

### 10.3 활용 시나리오

1. **음성 제어 개발**: "Create a REST API for user management"
2. **자동화된 테스트**: "Test the login flow on staging"
3. **멀티 에이전트 협업**: "Build and deploy a microservice"
4. **컨텍스트 학습**: RAG 기반 코드 재사용
5. **워크플로우 자동화**: 복잡한 작업 분해 및 병렬 실행

---

**작성일:** 2025-11-09
**버전:** 2.0.0
**상태:** ✅ 프로덕션 준비 완료
