# VidyaMitra (विद्या मित्र / বিদ্যা মিত্র)

> **AI-Powered Multi-Role Student Tutor Platform**
> Student · Tutor · Principal · Super Admin
> Nursery to Class 12 | English · Hindi · Bengali · Tamil

---

## Vision

An AI-powered personalized learning platform that transforms educational content into interactive, voice-enabled, adaptive learning experiences — with human oversight at every stage.

The platform combines **Artificial Intelligence**, **Human Tutors**, **Principals**, and **Administrators** to create a scalable and personalized educational ecosystem.

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                   4 ROLE-BASED PORTALS                    │
│  Student Portal  │  Tutor Portal  │  Principal  │  Admin │
├──────────────────────────────────────────────────────────┤
│              Next.js 15 + TypeScript + Tailwind          │
├──────────────────────────────────────────────────────────┤
│              FastAPI + LangGraph + WebSocket             │
├──────────────────────────────────────────────────────────┤
│                  12 AI AGENTS                             │
│  Teacher · Assessment · Curriculum · Motivation          │
│  Content Gen · Personalization · Video Gen               │
│  Verification · Voice · Matching · Analytics · Report    │
├──────────────────────────────────────────────────────────┤
│  PostgreSQL 16  │  Redis 7  │  Qdrant  │  MinIO  │  RMQ  │
└──────────────────────────────────────────────────────────┘
```

---

## Multi-Agent System (12 Agents)

| Agent | Role |
|-------|------|
| 🧑‍🏫 **Teacher** | Voice-first conversational tutoring, Hint → Guide → Solve |
| ✅ **Assessment** | MCQ + subjective + image OCR + AI evaluation |
| 📚 **Curriculum** | Subject → Chapter → Topic knowledge graph |
| 🎯 **Motivation** | Streaks, badges, points, gamification |
| 📝 **Content Gen** | PDF → structured lessons + summaries + exercises |
| 🎨 **Personalization** | Adapt by language, region, culture, grade, interests |
| 🎬 **Video Gen** | Auto-create animated concept explanations |
| 🔍 **Verification** | Auto-verify tutor qualifications + documents |
| 🎤 **Voice** | STT/TTS in 4+ languages with regional accents |
| 🔗 **Matching** | Intelligent tutor ↔ student pairing |
| 📊 **Analytics** | Learning patterns, trends, predictions |
| 📄 **Report** | Multi-role reports (Student/Tutor/Principal/Admin) |

---

## Key Features

### 👩‍🎓 For Students
- Voice-first AI tutoring in your language
- Personalized learning path based on age, grade, interests
- Automatic content adaptation (language, region, culture)
- MCQ + subjective assessments with AI + tutor feedback
- Gamification: points, badges, streaks, leaderboards
- Progress dashboard with weak area identification

### 👨‍🏫 For Tutors
- AI-generated content to review (approve/modify/reject)
- Student performance dashboard with analytics
- Personalized feedback and study plan recommendations
- Document verification workflow (AI → Principal → Admin)
- Intelligent student matching based on expertise + language

### 👨‍💼 For Principals
- Institution-wide dashboard (students, tutors, content)
- Tutor performance monitoring and quality assurance
- Content dispute resolution and escalation management
- Academic governance tools

### ⚡ For Super Admins
- Organization-wide analytics and user management
- Multi-step approval workflows (tutors, content)
- Platform health monitoring and compliance
- Notification center with AI recommendations

---

## Content Generation Pipeline

```
Admin Uploads PDF → AI Extracts Content → Creates Embeddings
→ Generates Lessons, Summaries, Explanations
→ Generates Videos with Voice Narration
→ Personalizes by Language, Region, Culture, Grade
→ Tutor Reviews → Approves → Published to Students
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 15, TypeScript, Tailwind CSS |
| Backend | FastAPI (Python 3.12), Uvicorn, WebSocket |
| AI Framework | LangGraph (12-agent orchestration) |
| Database | PostgreSQL 16 + Redis 7 + Qdrant (Vector DB) |
| File Storage | MinIO / S3 |
| Async Tasks | RabbitMQ / Celery |
| Models | GPT-4o, DeepSeek V4, GPT-4o-mini, Whisper, ElevenLabs |
| Math Engine | SymPy (deterministic verification) |
| OCR | Tesseract / Azure Vision |
| Monitoring | Langfuse + Prometheus + Grafana |
| Deployment | Docker + Docker Compose + GitHub Actions |

---

## Documentation

| Document | Description |
|----------|-------------|
| [Product Analysis](docs/product-analysis.md) | v2.0 competitive landscape (9 competitors, 14-capability matrix) |
| [PRD](docs/prd.md) | Full product requirements, 4 roles, 8-step learning journey |
| [Architecture](docs/architecture.md) | System design, content pipeline, tutor approval workflow |
| [Database Schema](docs/database-schema.md) | v2.0: 20+ tables including multi-role, content, approvals |
| [Agent Design](docs/agent-design.md) | 12 agents with detailed specs, model routing, guardrails |
| [API Specification](docs/api-specification.md) | 50+ endpoints across 15 sections, all 4 roles |
| [UI/UX Design](docs/ui-wireframes.md) | 10 screens across 4 portals, role-based design system |
| [Implementation Roadmap](docs/implementation-roadmap.md) | 6 sprints, 12 weeks, team allocation |
| [Architecture Diagrams](docs/diagrams/architecture-diagrams.md) | 9 Mermaid diagrams (system, pipeline, workflows, ER) |

---

## Quick Start (v1.0 — Local Dev)

```bash
# Clone
git clone https://github.com/rajibmahata/Math-tutor-AI-Agent.git
cd Math-tutor-AI-Agent

# Backend
cd backend && python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 -c "from app.core.database import init_db; import asyncio; asyncio.run(init_db())"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Frontend
cd frontend && npm install && npm run dev
# Open http://localhost:3000
```

---

## Status

🟢 **v1.0 Production Ready** — Math tutoring with 8 AI agents, voice, 3 languages  
🟡 **v2.0 Planned** — Multi-role platform, 12 agents, content pipeline, tutor ecosystem

---

## License

Proprietary. All rights reserved.

---

*Built with ❤️ for every Indian student who deserves a personal AI teacher — and every tutor who makes learning possible.*
