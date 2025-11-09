# Multi-Agent Learning System

> 🤖 음성으로 제어하는 통합 AI 에이전트 오케스트레이션 시스템 + 159개의 전문화된 AI 에이전트 풀

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

---

## 📋 목차

- [프로젝트 개요](#-프로젝트-개요)
- [주요 기능](#-주요-기능)
- [시스템 아키텍처](#-시스템-아키텍처)
- [디렉토리 구조](#-디렉토리-구조)
- [빠른 시작](#-빠른-시작)
- [컴포넌트 상세](#-컴포넌트-상세)
- [에이전트 풀](#-에이전트-풀)
- [문서](#-문서)

---

## 🎯 프로젝트 개요

Multi-Agent Learning System은 두 가지 핵심 시스템으로 구성됩니다:

### 1. Big Three Realtime Agents
음성이나 텍스트로 명령을 내리면 자동으로 **코딩**과 **브라우저 자동화** 작업을 수행하는 통합 AI 에이전트 오케스트레이션 시스템입니다.

**핵심 에이전트:**
- 🎙️ **OpenAI Realtime Voice Agent** - 음성 대화 및 오케스트레이션 담당
- 💻 **Claude Code Agentic Coder** - 소프트웨어 개발 및 코딩 담당
- 🌐 **Gemini Browser Agent** - 웹 브라우저 자동화 담당

### 2. Agent Pool System v2.0
프로덕션 환경에서 사용 가능한 **159개의 전문화된 AI 에이전트** 모음입니다.

**티어 구조:**
- ✅ **Tier 1**: 20개의 검증된 프로덕션 코어 에이전트
- 📦 **Tier 2**: ~100개의 전문화된 에이전트 (11개 카테고리)
- 🧪 **Tier 3**: ~40개의 실험적 에이전트 (4개 카테고리)

---

## ✨ 주요 기능

### Big Three Realtime Agents
- ✅ **음성 제어**: 자연어로 복잡한 개발 작업 지시
- ✅ **실시간 스트리밍**: 에이전트 작업 진행상황 실시간 확인
- ✅ **세션 연속성**: 각 에이전트는 독립적인 세션 유지
- ✅ **브라우저 자동화**: Playwright + Gemini Computer Use API
- ✅ **자동 코드 생성**: Claude Code SDK 기반 소프트웨어 개발
- ✅ **레지스트리 관리**: 모든 에이전트 세션 추적 및 재사용

### Agent Pool System
- ✅ **100% 독립 실행**: Context Manager 의존성 없음
- ✅ **실용적 메트릭**: 상황별 목표 설정 (critical/standard/legacy)
- ✅ **우아한 실패처리**: MCP 서버 없이도 작동
- ✅ **실행 가능한 로직**: 구체적인 bash 명령어 및 조건문
- ✅ **자동 검증**: 8단계 품질 검사

---

## 🏗️ 시스템 아키텍처

### Big Three 작업 흐름

```
사용자 (음성/텍스트)
    ↓
OpenAI Realtime Voice Agent (오케스트레이터)
    ↓
    ├─→ Claude Code Agent (소프트웨어 개발)
    │       ↓
    │   작업 디렉토리 (apps/content-gen/)
    │       ↓
    │   코드 생성/수정
    │
    └─→ Gemini Browser Agent (브라우저 자동화)
            ↓
        Playwright 브라우저
            ↓
        웹 검증/자동화
```

### Agent Pool 구조

```
Tier 1 (Core) - 20개
    └─→ 프로덕션 검증 완료, 즉시 사용 가능

Tier 2 (Specialized) - ~100개
    ├─→ Languages: rust, go, java, kotlin, etc.
    ├─→ Frameworks: nextjs, django, rails, etc.
    ├─→ Infrastructure: terraform, k8s, sre, etc.
    ├─→ Quality: testing, performance, accessibility
    ├─→ Security: penetration, compliance, audit
    ├─→ Data/AI: mlops, data-science, analytics
    └─→ 5+ more categories...

Tier 3 (Experimental) - ~40개
    ├─→ Blockchain/Fintech
    ├─→ Gaming (Unity, Minecraft)
    ├─→ Emerging Tech (Quantum, Web3)
    └─→ Niche (WordPress, SEO)
```

---

## 📂 디렉토리 구조

```
multi-agent-learning/
│
├── apps/
│   ├── content-gen/              # 에이전트 작업 디렉토리
│   │   ├── agents/              # 에이전트 세션 레지스트리
│   │   │   ├── claude_code/    # Claude 에이전트 세션
│   │   │   └── gemini/         # Gemini 에이전트 세션
│   │   ├── backend/            # 백엔드 코드 (에이전트 작업물)
│   │   ├── frontend/           # 프론트엔드 코드 (에이전트 작업물)
│   │   └── specs/              # 프로젝트 사양
│   │
│   └── realtime-poc/           # Big Three 메인 시스템
│       ├── big_three_realtime_agents/  # 리팩토링된 모듈화 구조
│       │   ├── workflow/       # 워크플로우 관리
│       │   ├── memory/         # 메모리 시스템
│       │   ├── learning/       # 학습 시스템
│       │   ├── security/       # 보안 시스템
│       │   └── utils/          # 유틸리티
│       └── prompts/            # 시스템 프롬프트
│
├── agentpool/                  # Agent Pool System v2.0
│   ├── tier1-core/            # 20개 검증된 코어 에이전트
│   ├── tier2-specialized/     # ~100개 전문화 에이전트
│   │   ├── languages/
│   │   ├── frameworks/
│   │   ├── infrastructure/
│   │   ├── quality/
│   │   ├── security/
│   │   ├── data-ai/
│   │   ├── devtools/
│   │   ├── specialized/
│   │   ├── business/
│   │   ├── orchestration/
│   │   └── research/
│   ├── tier3-experimental/    # ~40개 실험적 에이전트
│   ├── _templates/            # 에이전트 생성 템플릿
│   └── [Documentation]/       # 가이드 문서
│
├── claudedocs/                 # 프로젝트 문서
│   ├── quality_enhancement_final_report.md
│   ├── COMPLETE_SYSTEMS_SUMMARY.md
│   └── ...
│
├── .env.sample                 # 환경 변수 템플릿
├── .gitignore
└── refactoring.md             # 시스템 상세 분석 문서
```

---

## 🚀 빠른 시작

### 사전 요구사항

```bash
# Python 3.11 이상
python --version

# Node.js 18 이상 (Claude Code용)
node --version

# 필수 API 키
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GEMINI_API_KEY=your_gemini_key
```

### 설치

1. **저장소 클론**
```bash
git clone https://github.com/cafe8601/-multi-agent-learning.git
cd multi-agent-learning
```

2. **환경 변수 설정**
```bash
cp .env.sample .env
# .env 파일을 열어 API 키 입력
```

3. **의존성 설치**
```bash
# Python 의존성
pip install -r requirements.txt

# Playwright 브라우저 설치
playwright install chromium
```

### Big Three 실행

```bash
cd apps/realtime-poc
python -m big_three_realtime_agents.main
```

음성 또는 텍스트로 명령을 내리면:
- "Create a simple web app" → Claude Code가 자동으로 코드 생성
- "Test the login form" → Gemini Browser가 자동으로 브라우저 테스트 실행

### Agent Pool 사용

에이전트 파일을 Claude 설정 디렉토리에 복사:

```bash
# Tier 1 코어 에이전트 설치
cp -r agentpool/tier1-core/* ~/.claude/agents/

# 특정 Tier 2 에이전트 설치 (예: Python Pro)
cp agentpool/tier2-specialized/languages/python-pro.md ~/.claude/agents/

# Claude Code에서 사용
# 예: "Use the python-pro agent to refactor this code"
```

---

## 🔍 컴포넌트 상세

### 1. OpenAI Realtime Voice Agent

**역할**: 음성 인터페이스 및 에이전트 조정자

**주요 기능**:
- 실시간 음성 대화 (OpenAI Realtime API)
- 작업 분석 및 적절한 에이전트에 라우팅
- 다중 에이전트 조율 및 결과 통합

**기술 스택**:
- OpenAI Realtime API (WebSocket)
- 음성 스트리밍 및 처리
- 함수 호출 기반 에이전트 제어

### 2. Claude Code Agentic Coder

**역할**: 자율적 소프트웨어 개발 에이전트

**주요 기능**:
- 코드 생성 및 수정
- 독립적인 세션 관리
- MCP 서버 통합 (browser_use 등)
- 실시간 작업 로그 스트리밍

**작업 디렉토리**: `apps/content-gen/`

**레지스트리**: `apps/content-gen/agents/claude_code/registry.json`

**핵심 메서드**:
```python
create_agent(agent_name: str)
    # 새 에이전트 생성 및 세션 초기화

command_agent(agent_name: str, prompt: str)
    # 에이전트에 작업 지시

check_agent_result(agent_name: str, operator_file: str)
    # 실행 결과 조회
```

### 3. Gemini Browser Agent

**역할**: 브라우저 자동화 및 웹 검증

**주요 기능**:
- Playwright 브라우저 제어
- Gemini Computer Use API 통합
- 스크린샷 기반 작업 수행
- 세션별 작업 기록 관리

**기술 스택**:
- Playwright (Chromium 1440x900)
- Gemini 2.0 Flash Experimental
- 스크린샷 기반 비전 처리

**레지스트리**: `apps/content-gen/agents/gemini/registry.json`

**핵심 메서드**:
```python
setup_browser()
    # Playwright 브라우저 초기화

execute_task(task: str, url: Optional[str])
    # 브라우저 작업 실행

_run_browser_automation_loop(task: str, max_turns: int = 30)
    # Computer Use 루프 (최대 30턴)
```

---

## 🤖 에이전트 풀

### Tier 1: Core Agents (20개)

프로덕션 검증 완료, 즉시 사용 가능:

| 에이전트 | 설명 | 크기 |
|---------|------|------|
| `backend-developer` | 백엔드 개발 전문가 | 19KB |
| `frontend-developer` | 프론트엔드 개발 전문가 | 25KB |
| `python-pro` | Python 전문가 | 8.5KB |
| `devops-engineer` | DevOps 및 인프라 | 13KB |
| `qa-expert` | 품질 보증 및 테스팅 | 15KB |
| `security-auditor` | 보안 감사 | 15KB |
| `typescript-pro` | TypeScript 전문가 | - |
| `kubernetes-architect` | K8s 아키텍트 | - |
| `multi-agent-coordinator` | 멀티 에이전트 조율 | - |
| ... | (총 20개) | 168KB |

### Tier 2: Specialized Agents (~100개)

**11개 카테고리**:

1. **Languages** (15+): Rust, Go, Java, Kotlin, Scala, C++, C#, PHP, Ruby, etc.
2. **Frameworks** (11): Next.js, Django, Rails, Laravel, Flutter, Angular, etc.
3. **Infrastructure** (11): Terraform, Ansible, SRE, Platform Engineering, etc.
4. **Quality** (11): Performance, Accessibility, Testing, Debugging, etc.
5. **Security** (6): Penetration Testing, Compliance, Security Engineering
6. **Data/AI** (8): MLOps, Data Science, NLP, LLM Architecture, etc.
7. **DevTools** (10): CLI, Documentation, Git Workflow, Tooling, etc.
8. **Specialized** (13): Mobile, IoT, GraphQL, WebSocket, MCP, etc.
9. **Business** (13): UX Research, Product Management, Sales, etc.
10. **Orchestration** (7): Workflow, Task Distribution, Knowledge Synthesis
11. **Research** (1): Research Analyst

### Tier 3: Experimental (~40개)

**4개 카테고리**:
- **Blockchain**: Blockchain Dev, FinTech, Quant Analysis
- **Gaming**: Game Dev, Unity, Minecraft Bukkit
- **Emerging Tech**: Quantum, Edge Computing, Web3
- **Niche**: WordPress, SEO variants

### 에이전트 생성 도구

```bash
# 템플릿 사용
cp agentpool/_templates/tier1-template.md my-new-agent.md

# 자동 검증
bash agentpool/_templates/validate-agent.sh my-new-agent.md
```

**8단계 검증**:
1. ✅ 독립 실행 가능 (no context manager)
2. ✅ 실행 가능한 bash 명령어
3. ✅ 실용적 메트릭 목표
4. ✅ MCP 서버 우아한 실패처리
5. ✅ 구체적 예시 코드
6. ✅ 조건부 로직 구현
7. ✅ 명확한 책임과 경계
8. ✅ 완전한 문서화

---

## 📚 문서

### Big Three Realtime Agents

- **[refactoring.md](./refactoring.md)** - 시스템 전체 분석 (299KB, 11,000+ 줄)
  - 아키텍처 상세 설명
  - 컴포넌트별 코드 분석
  - 워크플로우 및 데이터 흐름
  - 리팩토링된 모듈 구조

- **[apps/realtime-poc/big_three_realtime_agents/README.md](./apps/realtime-poc/big_three_realtime_agents/README.md)**
  - 리팩토링 후 모듈 구조
  - 사용 가이드
  - API 레퍼런스

### Agent Pool System

- **[agentpool/README.md](./agentpool/README.md)** - Agent Pool 개요
- **[agentpool/MIGRATION_GUIDE.md](./agentpool/MIGRATION_GUIDE.md)** - v1→v2 마이그레이션
- **[agentpool/AGENT_CLASSIFICATION_GUIDE.md](./agentpool/AGENT_CLASSIFICATION_GUIDE.md)** - 카테고리 분류 가이드
- **[agentpool/COMPLETION_REPORT.md](./agentpool/COMPLETION_REPORT.md)** - 상세 완성 보고서

### 프로젝트 문서

- **[claudedocs/COMPLETE_SYSTEMS_SUMMARY.md](./claudedocs/COMPLETE_SYSTEMS_SUMMARY.md)** - 전체 시스템 요약
- **[claudedocs/quality_enhancement_final_report.md](./claudedocs/quality_enhancement_final_report.md)** - 품질 향상 보고서

---

## 🛠️ 기술 스택

### Big Three System
- **Python 3.11+**
- **OpenAI Realtime API** - 음성 처리
- **Claude Code SDK** - 코드 생성
- **Gemini 2.0 Flash** - Computer Use
- **Playwright** - 브라우저 자동화
- **MCP (Model Context Protocol)** - 에이전트 도구 통합

### Agent Pool
- **Markdown** - 에이전트 정의
- **Bash** - 자동화 스크립트
- **YAML** - 메타데이터

---

## 🤝 기여 방법

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### 에이전트 기여 가이드라인

1. `agentpool/_templates/tier2-template.md` 사용
2. `validate-agent.sh`로 검증
3. 적절한 tier/category에 배치
4. README 업데이트

---

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

---

## 🙏 감사의 말

이 프로젝트는 다음 기술과 프로젝트를 기반으로 합니다:

- [OpenAI Realtime API](https://platform.openai.com/docs/guides/realtime)
- [Claude Code SDK](https://github.com/anthropics/anthropic-sdk-python)
- [Google Gemini API](https://ai.google.dev/)
- [Playwright](https://playwright.dev/)
- Original Big-3-Super-Agent by [disler](https://github.com/disler/big-3-super-agent)

---

## 📞 연락처

문제가 있거나 질문이 있으시면 [Issues](https://github.com/cafe8601/-multi-agent-learning/issues)에 등록해주세요.

---

**Made with ❤️ by the Multi-Agent Learning Community**
