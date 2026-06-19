# GanitMitra (गणित मित्र / গণিত মিত্র)

> **AI-Powered Multilingual Math Learning Companion**
> Nursery to Class 10 | English · Hindi · Bengali

---

## Vision

An adaptive AI math teacher that speaks every Indian student's language, understands their unique learning journey, and grows with them from Nursery to Class 10. Not a chatbot — a personal tutor.

---

## Architecture

```
┌──────────────┐    ┌──────────────┐    ┌──────────────────┐
│ Next.js 15   │    │ FastAPI      │    │ Multi-Agent AI   │
│ TypeScript   │◄──►│ Python 3.12  │◄──►│ 8 Specialized    │
│ Tailwind CSS │    │ LangGraph    │    │ Agents           │
└──────────────┘    └──────────────┘    └──────────────────┘
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │PostgreSQL│ │  Redis   │ │ Qdrant   │
        │ Primary  │ │  Cache   │ │ Vector DB│
        └──────────┘ └──────────┘ └──────────┘
```

---

## Multi-Agent System

| Agent | Role |
|-------|------|
| 🧑‍🏫 **Teacher** | Hint → Guide → Solve methodology |
| ✅ **Assessment** | Answer evaluation, misconception detection |
| 📚 **Curriculum** | Topic sequencing, RAG knowledge retrieval |
| ✏️ **Practice** | Adaptive quiz generation |
| 🎯 **Motivation** | Encouragement, streaks, gamification |
| 📊 **Analytics** | Progress computation, learning velocity |
| 📄 **Parent Report** | Weekly progress digests |
| 🎤 **Voice** | STT/TTS in all 3 languages |

---

## Learning Methodology

```
Hint → Guided Thinking → Step-by-Step → Final Answer
```

**Never give answers first.** Age-aware teaching:
- **Nursery-KG:** Stories, visuals, counting
- **Primary (1-5):** Arithmetic, word problems
- **Middle (6-8):** Algebra, geometry
- **Secondary (9-10):** Advanced math, exam prep

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 15, TypeScript, Tailwind CSS, shadcn/ui |
| Backend | FastAPI (Python 3.12), Uvicorn, WebSocket |
| Database | PostgreSQL 16 + Redis 7 + Qdrant |
| AI Framework | LangGraph (multi-agent orchestration) |
| Models | GPT-4o, DeepSeek V4, GPT-4o-mini, Whisper, ElevenLabs |
| Math Engine | SymPy (deterministic verification) |
| Monitoring | Langfuse + Prometheus + Grafana |
| Deployment | Docker + Docker Compose + GitHub Actions |

---

## Documentation

| Document | Description |
|----------|-------------|
| [Product Analysis](docs/product-analysis.md) | Reference app analysis + competitive landscape |
| [PRD](docs/prd.md) | Full product requirements + MoSCoW |
| [Architecture](docs/architecture.md) | System design, component architecture, scaling |
| [Database Schema](docs/database-schema.md) | 14 tables, relationships, Pydantic schemas |
| [Agent Design](docs/agent-design.md) | LangGraph orchestration, 8 agent prompts + tools |
| [API Specification](docs/api-specification.md) | REST + WebSocket API, all endpoints |
| [UI/UX Design](docs/ui-wireframes.md) | Wireframes, design system, micro-interactions |
| [Implementation Roadmap](docs/implementation-roadmap.md) | 14-week plan, sprints, gates |
| [Architecture Diagrams](docs/diagrams/architecture-diagrams.md) | Mermaid diagrams (render on GitHub) |

---

## Quick Start (Coming Soon)

```bash
# Clone
git clone https://github.com/rajibmahata/Math-tutor-AI-Agent.git
cd Math-tutor-AI-Agent

# Start all services
docker compose up -d

# Run migrations
cd backend && alembic upgrade head

# Seed curriculum data
python scripts/seed_curriculum.py

# Start development
cd frontend && npm run dev    # Next.js :3000
cd backend && uvicorn app.main:app --reload  # FastAPI :8000
```

---

## Status

🟢 **v1.0 — Production Ready** — All features complete. Running at http://localhost:3000

---

## Local Development (Docker)

```bash
# 1. Clone and enter
git clone https://github.com/rajibmahata/Math-tutor-AI-Agent.git
cd Math-tutor-AI-Agent

# 2. Configure environment (edit .env with your API keys)
cp .env .env.local
nano .env

# 3. Start all services
docker compose up -d

# 4. Run database migrations
docker compose exec backend alembic upgrade head

# 5. Seed curriculum data
docker compose exec backend python scripts/seed_curriculum.py

# 6. Access the app
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/api/docs
# Grafana:  http://localhost:3001 (admin/ganitmitra)
```

### Development Mode (Hot Reload)

```bash
# Backend (with auto-reload)
docker compose up backend -d

# Frontend (with hot reload)
cd frontend && npm install && npm run dev
```

### Running Tests

```bash
# Backend tests
docker compose exec backend pytest -v

# Frontend tests
cd frontend && npx vitest run
```

---

## License

Proprietary. All rights reserved.

---

*Built with ❤️ for every Indian student who deserves a personal math teacher.*
