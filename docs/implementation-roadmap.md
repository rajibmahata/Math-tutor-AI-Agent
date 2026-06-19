# Implementation Roadmap — GanitMitra Math Tutor

> **Date:** 2026-06-19
> **Version:** 1.0
> **Author:** WorkCore (RCore)

---

## 1. Development Phases Overview

```
Phase 0: Foundation        Phase 1: Core MVP         Phase 2: Enhancement
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│ Week 1-2        │  ───▶ │ Week 3-6        │  ───▶ │ Week 7-10       │
│                 │       │                 │       │                 │
│ • Project Setup │       │ • Auth + Users  │       │ • Voice STT/TTS │
│ • DB + Migrations│      │ • Student Twin  │       │ • Practice Mode │
│ • Docker Env    │       │ • Teacher Agent │       │ • Parent Reports│
│ • CI/CD         │       │ • Assessment    │       │ • Gamification  │
│ • Design System │       │ • Chat UI       │       │ • RAG Pipeline  │
│ • Boilerplate   │       │ • Dashboard     │       │ • Analytics     │
└─────────────────┘       └─────────────────┘       └─────────────────┘

Phase 3: Polish           Phase 4: Launch
┌─────────────────┐       ┌─────────────────┐
│ Week 11-12      │  ───▶ │ Week 13-14      │
│                 │       │                 │
│ • Testing/QA    │       │ • Production Deploy│
│ • Performance   │       │ • Monitoring    │
│ • Security Audit│       │ • Documentation │
│ • Nursery-KG    │       │ • Launch 🚀     │
│ • PWA Offline   │       │                 │
└─────────────────┘       └─────────────────┘
```

---

## 2. Detailed Sprint Plan

### Phase 0: Foundation (Week 1-2)

#### Sprint 0.1 — Project Scaffolding (Days 1-3)

| Task | Owner | Est. | Dependencies |
|------|-------|------|-------------|
| Initialize monorepo structure | DevOps | 2h | — |
| Set up FastAPI project with Poetry | Backend | 3h | — |
| Set up Next.js project with TypeScript | Frontend | 3h | — |
| Configure Tailwind + shadcn/ui | Frontend | 2h | Next.js |
| Set up PostgreSQL with Docker | DevOps | 2h | — |
| Set up Redis with Docker | DevOps | 1h | — |
| Create Docker Compose (all services) | DevOps | 3h | — |
| Configure Alembic for migrations | Backend | 2h | FastAPI |
| Set up ESLint + Prettier | Frontend | 1h | Next.js |
| Set up Black + Ruff for Python | Backend | 1h | FastAPI |
| Initialize Git repo + .gitignore | DevOps | 0.5h | — |

**Deliverable:** Running Docker environment with all services starting.

#### Sprint 0.2 — Database & Models (Days 4-7)

| Task | Owner | Est. | Dependencies |
|------|-------|------|-------------|
| Create SQLAlchemy models (all 14 tables) | Backend | 6h | Sprint 0.1 |
| Generate initial Alembic migration | Backend | 1h | Models |
| Create Pydantic schemas | Backend | 4h | Models |
| Seed curriculum topics (NCERT Class 1-10) | Backend | 4h | Models |
| Seed topic prerequisites | Backend | 2h | Topics |
| Set up test database + fixtures | Backend | 3h | Migration |
| Verify DB schema with test data | Backend | 2h | All above |

**Deliverable:** Complete database schema with curriculum seed data.

#### Sprint 0.3 — CI/CD & Design System (Days 8-14)

| Task | Owner | Est. | Dependencies |
|------|-------|------|-------------|
| Set up GitHub Actions CI pipeline | DevOps | 3h | Repo |
| Configure pytest + coverage | Backend | 2h | FastAPI |
| Configure Jest + React Testing Library | Frontend | 2h | Next.js |
| Build design system components (Button, Card, Input, Badge, Progress, Dialog, Toast) | Frontend | 8h | Tailwind+shadcn |
| Create layout components (Shell, Sidebar, BottomNav) | Frontend | 4h | Design system |
| Build KaTeX math renderer component | Frontend | 3h | Design system |
| Create language provider (i18n context) | Frontend | 4h | Next.js |
| Set up Zustand stores (auth, student, session) | Frontend | 3h | Next.js |

**Deliverable:** CI/CD pipeline, design system, core UI components.

---

### Phase 1: Core MVP (Week 3-6)

#### Sprint 1.1 — Authentication (Days 15-18)

| Task | Owner | Est. | Dependencies |
|------|-------|------|-------------|
| Implement JWT auth (access + refresh) | Backend | 4h | Models |
| Implement Google OAuth flow | Backend | 4h | JWT auth |
| Build signup page (email/password) | Frontend | 4h | Design system |
| Build login page | Frontend | 3h | Design system |
| Build Google OAuth button integration | Frontend | 2h | Auth pages |
| Implement protected route middleware | Frontend | 2h | Auth |
| Build user session management (refresh rotation) | Backend | 3h | JWT |
| Rate limiting middleware | Backend | 2h | FastAPI |
| Auth integration tests | Backend | 3h | All auth |

**Deliverable:** Full auth flow — signup, login, OAuth, protected routes.

#### Sprint 1.2 — Student Profile & Digital Twin (Days 19-22)

| Task | Owner | Est. | Dependencies |
|------|-------|------|-------------|
| Student profile CRUD API | Backend | 4h | Models |
| Digital twin computation service | Backend | 6h | Student profile |
| Placement assessment (5 questions) | Backend | 4h | Topics seed |
| Build onboarding wizard (3 screens) | Frontend | 6h | Design system, Auth |
| Build student dashboard page | Frontend | 6h | Onboarding |
| Parent-student linking API | Backend | 2h | Student profile |
| Student profile page (display twin data) | Frontend | 4h | Dashboard |

**Deliverable:** Student onboarding, digital twin, dashboard.

#### Sprint 1.3 — Teacher Agent + Tutoring (Days 23-30)

| Task | Owner | Est. | Dependencies |
|------|-------|------|-------------|
| Build LangGraph orchestrator graph | AI Engineer | 6h | Phase 0 |
| Implement Teacher Agent (Hint→Guide→Solve) | AI Engineer | 8h | Orchestrator |
| Implement Assessment Agent (evaluation + misconception) | AI Engineer | 6h | Teacher Agent |
| Implement Model Router | AI Engineer | 4h | LangGraph |
| Integrate SymPy verification service | Backend | 4h | Model Router |
| Build tutoring session API (REST + WS) | Backend | 6h | Agents |
| Build chat interface component | Frontend | 8h | Design system |
| Build hint reveal UI + interaction | Frontend | 4h | Chat interface |
| Build solution steps display (KaTeX) | Frontend | 4h | Chat interface |
| WebSocket client integration | Frontend | 4h | Chat interface |
| Session persistence + resume | Backend | 4h | Session API |

**Deliverable:** Working tutoring chat with Hint→Guide→Solve flow.

#### Sprint 1.4 — Progress Dashboard + Motivation (Days 31-42)

| Task | Owner | Est. | Dependencies |
|------|-------|------|-------------|
| Implement Analytics Agent computations | Backend | 6h | Digital twin |
| Progress API endpoints | Backend | 4h | Analytics |
| Topic tree API | Backend | 3h | Topics seed |
| Build progress dashboard page | Frontend | 8h | Dashboard |
| Build topic mastery map component | Frontend | 6h | Progress page |
| Build weekly activity chart | Frontend | 4h | Progress page |
| Implement Motivation Agent | AI Engineer | 4h | Teacher Agent |
| Build achievement badges system | Backend | 4h | Digital twin |
| Achievement detection triggers | Backend | 3h | Achievements |
| Build celebration animations (confetti, badges) | Frontend | 4h | Achievements |

**Deliverable:** Full progress tracking, visualization, motivation system.

---

### Phase 2: Enhancement (Week 7-10)

#### Sprint 2.1 — Voice Interaction (Days 43-49)

| Task | Owner | Est. | Dependencies |
|------|-------|------|-------------|
| Implement Voice Agent (STT pipeline) | Backend | 6h | FastAPI |
| Implement Voice Agent (TTS pipeline) | Backend | 6h | STT |
| Math-to-speech text preprocessing | Backend | 4h | TTS |
| Voice recording UI component | Frontend | 6h | Chat UI |
| Voice playback component | Frontend | 3h | TTS |
| Voice mode toggle + UI | Frontend | 4h | Voice components |
| Voice WebSocket streaming | Backend | 4h | WS existing |

**Deliverable:** Full voice input/output for all 3 languages.

#### Sprint 2.2 — Practice Mode (Days 50-56)

| Task | Owner | Est. | Dependencies |
|------|-------|------|-------------|
| Implement Practice Agent (question generation) | AI Engineer | 6h | LangGraph |
| Practice set API (generate, submit, complete) | Backend | 6h | Practice Agent |
| Build practice quiz UI | Frontend | 8h | Design system |
| Build question card + timer | Frontend | 4h | Quiz UI |
| Build quiz results screen | Frontend | 4h | Quiz UI |
| Adaptive difficulty algorithm | Backend | 4h | Digital twin |

**Deliverable:** Working practice mode with adaptive quizzes.

#### Sprint 2.3 — Curriculum RAG (Days 57-63)

| Task | Owner | Est. | Dependencies |
|------|-------|------|-------------|
| Set up Qdrant + embedding pipeline | RAG Engineer | 6h | Phase 0 |
| Ingest NCERT textbooks (EN/HI) | RAG Engineer | 8h | Qdrant |
| Ingest ICSE + WB Board content | RAG Engineer | 6h | Qdrant |
| Build RAG retriever + reranker | RAG Engineer | 6h | Qdrant |
| Integrate RAG into Curriculum Agent | AI Engineer | 4h | RAG + LangGraph |
| Build search curriculum endpoint | Backend | 3h | RAG |

**Deliverable:** Curriculum knowledge base with semantic search.

#### Sprint 2.4 — Parent Reports + Gamification (Days 64-70)

| Task | Owner | Est. | Dependencies |
|------|-------|------|-------------|
| Implement Parent Report Agent | AI Engineer | 6h | Analytics |
| Report generation API | Backend | 4h | Report Agent |
| Scheduled report generation (cron) | Backend | 3h | Report API |
| Build parent dashboard page | Frontend | 8h | Reports |
| Build report detail view | Frontend | 4h | Parent dashboard |
| Gamification: streaks, points, leaderboard | Backend | 4h | Achievements |
| Gamification UI: badges, points display | Frontend | 4h | Gamification |

**Deliverable:** Parent reports, full gamification system.

---

### Phase 3: Polish (Week 11-12)

#### Sprint 3.1 — Testing & QA (Days 71-77)

| Task | Owner | Est. | Dependencies |
|------|-------|------|-------------|
| Backend unit tests (≥80% coverage) | Backend | 12h | All APIs |
| Agent unit tests (mock LLM responses) | AI Engineer | 8h | All agents |
| Frontend component tests | Frontend | 8h | All components |
| Integration tests (auth → tutoring → progress) | QA | 8h | All features |
| E2E tests (Playwright, key flows) | QA | 6h | Integration |
| Multilingual testing (EN/HI/BN) | QA | 6h | All features |
| Mobile responsiveness QA | QA | 4h | All pages |
| Accessibility audit (WCAG 2.1 AA) | QA | 4h | All pages |

**Deliverable:** Test suite with ≥80% coverage.

#### Sprint 3.2 — Performance & Security (Days 78-84)

| Task | Owner | Est. | Dependencies |
|------|-------|------|-------------|
| API response time optimization (<500ms p95) | Backend | 6h | All APIs |
| Redis caching strategy (sessions, frequent queries) | Backend | 4h | Performance |
| DB query optimization (indexes, N+1) | Backend | 4h | Performance |
| Frontend bundle optimization (code splitting) | Frontend | 4h | All pages |
| Image/asset optimization | Frontend | 2h | Bundle |
| Security audit (OWASP Top 10) | Security | 6h | All APIs |
| Prompt injection hardening | AI Engineer | 4h | All agents |
| Dependency vulnerability scan | DevOps | 2h | All |
| Rate limiting tuning | Backend | 2h | Security |

**Deliverable:** Performance-optimized, security-hardened application.

---

### Phase 4: Launch (Week 13-14)

#### Sprint 4.1 — Pre-Launch (Days 85-91)

| Task | Owner | Est. | Dependencies |
|------|-------|------|-------------|
| Nursery-KG mode (stories, visuals) | AI + Frontend | 8h | Teacher Agent |
| PWA offline support | Frontend | 6h | All pages |
| Production Docker build optimization | DevOps | 4h | All services |
| Environment config management | DevOps | 2h | Docker |
| Production database setup + backup | DevOps | 3h | All |
| DNS + SSL setup | DevOps | 2h | Production |
| Monitoring setup (Langfuse + Grafana) | DevOps | 6h | Production |

**Deliverable:** Production-ready deployment.

#### Sprint 4.2 — Launch (Days 92-98)

| Task | Owner | Est. | Dependencies |
|------|-------|------|-------------|
| Production deployment | DevOps | 4h | Pre-launch |
| Smoke tests (all critical paths) | QA | 4h | Deploy |
| Load testing (1K concurrent users) | QA | 4h | Deploy |
| API documentation (OpenAPI/Swagger) | Backend | 4h | All APIs |
| User guide (EN/HI/BN) | Docs | 6h | All features |
| Landing page optimization | Frontend | 4h | Deploy |
| SEO metadata | Frontend | 2h | Landing page |
| Analytics/tracking setup | DevOps | 2h | Deploy |

**Deliverable:** 🚀 LAUNCH — GanitMitra is live!

---

## 3. Workforce Allocation

### Team Composition (7 agents)

| Role | Agent | Primary Sprints |
|------|-------|----------------|
| **Product Owner** | rajiblabs-po | All phases (review, prioritize) |
| **Architect** | rajiblabs-architect | Phase 0-1 (design review) |
| **AI Engineer** | WorkCore (RCore) | Phase 0-2 (agents, RAG) |
| **Backend Engineer** | rajiblabs-dev-backend | Phase 0-3 (FastAPI, DB) |
| **Frontend Engineer** | rajiblabs-dev-frontend | Phase 0-3 (Next.js, UI) |
| **QA Engineer** | rajiblabs-qa-functional | Phase 3 (testing) |
| **DevOps Engineer** | rajiblabs-devops | Phase 0, 4 (infrastructure) |

### Parallel Work Strategy

```
Week 1-2:  Backend + Frontend + DevOps (parallel setup)
Week 3-4:  Backend (API) + Frontend (UI) + AI (Agents) — parallel
Week 5-6:  Backend (Analytics) + Frontend (Dashboard) — parallel
Week 7-8:  AI (Voice) + Frontend (Voice UI) — parallel
Week 9-10: AI (RAG) + Frontend (Reports) + Backend (Reports) — parallel
Week 11-12: QA + Security (parallel)
Week 13-14: DevOps + Docs + Launch (parallel)
```

---

## 4. Risk Register

| Risk | Impact | Probability | Mitigation |
|------|--------|------------|------------|
| LLM API costs exceed budget | High | Medium | Aggressive caching, model routing for cost optimization |
| Hindi/Bengali TTS quality poor | Medium | Medium | Use multiple providers, fallback to text |
| Whisper accuracy low for children's voices | Medium | Low | Fine-tune or use child-specific models |
| SymPy cannot parse all answer formats | Medium | Medium | Multiple parsing strategies, regex fallback |
| Curriculum seed data incomplete | Medium | Medium | Start with NCERT Class 1-5, expand gradually |
| Indian language text rendering issues | Low | Low | Use Noto fonts, test on real devices |
| Docker complexity slows development | Low | Low | Start with simple Compose, iterate |
| Student data privacy compliance (COPPA) | High | Low | Privacy-first design from Day 1 |

---

## 5. Success Gates

### Gate 1: Foundation Complete (End of Week 2)
- [ ] All Docker services start successfully
- [ ] Database migrations run clean
- [ ] CI pipeline passes on PR
- [ ] Design system components render
- [ ] Curriculum seed data loaded

### Gate 2: MVP Core Complete (End of Week 6)
- [ ] Full auth flow works
- [ ] Student can onboard and get placement
- [ ] Tutoring chat works with Hint→Guide→Solve
- [ ] Assessment correctly evaluates answers
- [ ] Progress dashboard shows real data
- [ ] All 3 languages functional

### Gate 3: Feature Complete (End of Week 10)
- [ ] Voice input/output works in all languages
- [ ] Practice mode generates adaptive quizzes
- [ ] Parent reports generate and display
- [ ] Gamification elements active
- [ ] RAG curriculum retrieval working

### Gate 4: Production Ready (End of Week 14)
- [ ] Test coverage ≥ 80%
- [ ] Performance benchmarks met
- [ ] Security audit passed
- [ ] Production deployment verified
- [ ] Documentation complete

---

## Next: Start Development (Phase 0)
