# System Architecture — VidyaMitra AI Student Tutor Platform v2.0

> **Date:** 2026-06-19 | **Version:** 2.0 | **Author:** WorkCore (Architect)

---

## 1. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐  │
│  │ Student   │ │ Tutor    │ │ Principal│ │ Super Admin      │  │
│  │ Portal    │ │ Portal   │ │ Portal   │ │ Portal           │  │
│  │ Next.js   │ │ Next.js  │ │ Next.js  │ │ Next.js          │  │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────────┬─────────┘  │
└───────┼────────────┼────────────┼─────────────────┼────────────┘
        │            │            │                 │
        ▼            ▼            ▼                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                        API GATEWAY                               │
│  Nginx (TLS 1.3) → FastAPI (Uvicorn Workers) → WebSocket       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐      │
│  │ Auth     │ │ Rate     │ │ Content  │ │ Notification │      │
│  │ (JWT+R)  │ │ Limiter  │ │ CDN      │ │ Hub          │      │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────┘      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      SERVICE LAYER                               │
│                                                                  │
│  Student       Tutor        Principal     Admin                │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐         │
│  │ Learning │ │ Content  │ │ Monitor  │ │Governance│         │
│  │ Profile  │ │ Review   │ │ Service  │ │ Service  │         │
│  │ Service  │ │ Service  │ │          │ │          │         │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘         │
│                                                                  │
│  Shared Services                                                │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐         │
│  │ Content  │ │Assessment│ │ Analytics│ │ Voice    │         │
│  │ Generator│ │ Engine   │ │ Engine   │ │ Service  │         │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       AI AGENT LAYER (12 Agents)                 │
│                                                                  │
│  LangGraph Orchestrator ← Model Router                          │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐       │
│  │Teacher│ │Assess│ │Curric│ │Content│ │Person│ │Video │       │
│  │Agent  │ │Agent │ │Agent │ │Gen    │ │alize │ │Gen   │       │
│  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘       │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐       │
│  │Verify│ │Match │ │Analy │ │Motiv │ │Voice │ │Report│       │
│  │Agent │ │Agent │ │tics  │ │Agent │ │Agent │ │Agent │       │
│  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       DATA LAYER                                 │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│  │ PostgreSQL   │ │ Redis        │ │ Qdrant       │            │
│  │ (Primary)    │ │ (Cache/Sess) │ │ (Vector DB)  │            │
│  └──────────────┘ └──────────────┘ └──────────────┘            │
│  ┌──────────────┐ ┌──────────────┐                              │
│  │ MinIO/S3     │ │ RabbitMQ     │                              │
│  │ (File Store) │ │ (Async Tasks)│                              │
│  └──────────────┘ └──────────────┘                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Role-Based Portal Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    FRONTEND (Next.js)                      │
│                                                            │
│  /student/*     /tutor/*      /principal/*   /admin/*     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │Dashboard │  │Dashboard │  │Dashboard │  │Dashboard │ │
│  │Learning  │  │Content   │  │Tutors    │  │Users     │ │
│  │Chat      │  │Review    │  │Students  │  │Principals│ │
│  │Practice  │  │Students  │  │Reports   │  │Analytics │ │
│  │Progress  │  │Feedback  │  │Escalate  │  │Approve   │ │
│  │Profile   │  │Profile   │  │Profile   │  │Settings  │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │
└──────────────────────────────────────────────────────────┘
```

---

## 3. Content Generation Pipeline

```
┌─────────────────────────────────────────────────────────┐
│               CONTENT GENERATION PIPELINE                 │
│                                                          │
│  Admin Upload (PDF/Notes)                               │
│       │                                                  │
│       ▼                                                  │
│  ┌──────────────┐                                       │
│  │ Step 1:      │  Extract text, images, structure      │
│  │ Content      │  from PDF using OCR + parsing         │
│  │ Extraction   │                                       │
│  └──────┬───────┘                                       │
│         │                                                │
│         ▼                                                │
│  ┌──────────────┐                                       │
│  │ Step 2:      │  Generate embeddings                  │
│  │ Embeddings   │  Store in Qdrant vector DB            │
│  └──────┬───────┘                                       │
│         │                                                │
│         ▼                                                │
│  ┌──────────────┐                                       │
│  │ Step 3:      │  AI generates:                        │
│  │ Lesson       │  • Lesson plans                       │
│  │ Generation   │  • Chapter summaries                  │
│  │              │  • Topic explanations                 │
│  │              │  • Examples & exercises               │
│  └──────┬───────┘                                       │
│         │                                                │
│         ▼                                                │
│  ┌──────────────┐                                       │
│  │ Step 4:      │  AI generates:                        │
│  │ Video &      │  • Animated concept videos            │
│  │ Voice Gen    │  • Regional language narration        │
│  │              │  • Visual demonstrations              │
│  └──────┬───────┘                                       │
│         │                                                │
│         ▼                                                │
│  ┌──────────────┐                                       │
│  │ Step 5:      │  Adapt for: language, region,         │
│  │ Personalize  │  culture, grade level, interests      │
│  └──────┬───────┘                                       │
│         │                                                │
│         ▼                                                │
│  ┌──────────────┐                                       │
│  │ Step 6:      │  Tutor reviews → Approve/Modify/     │
│  │ Tutor        │  Reject → Published to knowledge      │
│  │ Validation   │  base                                 │
│  └──────────────┘                                       │
└─────────────────────────────────────────────────────────┘
```

---

## 4. Assessment Engine Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  ASSESSMENT ENGINE                        │
│                                                          │
│  Objective Questions          Subjective Questions       │
│  ┌──────────────────┐       ┌──────────────────────┐   │
│  │ • MCQ            │       │ • Student writes on   │   │
│  │ • Fill in blanks │       │   paper              │   │
│  │ • Match columns  │       │ • Draws diagrams     │   │
│  │ • True/False     │       │ • Uploads image      │   │
│  │                  │       │                      │   │
│  │ Auto-graded by   │       │ AI processes:        │   │
│  │ SymPy + rule     │       │ • OCR handwriting    │   │
│  │ engine           │       │ • Diagram analysis   │   │
│  └──────────────────┘       │ • Content evaluation │   │
│                              │ • Auto-scoring       │   │
│                              └──────────────────────┘   │
│                                                          │
│  Teacher Review: Tutor feedback alongside AI feedback    │
└─────────────────────────────────────────────────────────┘
```

---

## 5. Tutor Approval Workflow

```
Tutor Registration
 │  Submit: personal info, subjects, experience, degrees, certs
 ▼
AI Verification Agent
 │  Auto-verify: documents, qualifications, consistency
 │  Generate: verification report
 ▼
Principal Review
 │  Review: AI report, documents, suitability
 ▼
Super Admin Approval
 │  Final approval
 ▼
Tutor Activated
 │  Access: dashboard, students, content validation
```

---

## 6. Technology Stack (v2.0)

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Next.js 15, TypeScript, Tailwind CSS | Role-based portals |
| **Backend** | FastAPI (Python 3.12), Uvicorn | REST + WebSocket API |
| **AI Framework** | LangGraph | 12-agent orchestration |
| **Primary DB** | PostgreSQL 16 | Relational data |
| **Cache** | Redis 7 | Sessions, rate limiting |
| **Vector DB** | Qdrant | Content embeddings, RAG |
| **File Storage** | MinIO / S3 | PDFs, images, videos |
| **Async Tasks** | RabbitMQ / Celery | Content generation, video rendering |
| **Container** | Docker + Compose | Local dev, CI/CD |
| **Monitoring** | Langfuse + Prometheus + Grafana | LLM tracing + metrics |
| **STT** | OpenAI Whisper | Voice input |
| **TTS** | ElevenLabs / Azure / OpenAI | Voice output |
| **OCR** | Tesseract / Azure Vision | Handwriting recognition |
| **Video** | Remotion / RunwayML | AI video generation |
| **Auth** | JWT (Access + Refresh) + Google OAuth | Multi-role auth |

---

## 7. Database Schema (New Tables)

| Table | Purpose |
|-------|---------|
| `tutors` | Tutor profiles, subjects, experience |
| `tutor_documents` | Qualification documents, verification status |
| `principals` | Principal profiles, institution |
| `content_lessons` | AI-generated lessons |
| `content_videos` | AI-generated videos |
| `content_reviews` | Tutor content validation records |
| `assessments` | Extended: MCQ, subjective, image-based |
| `assessment_results` | Per-question results with AI + tutor feedback |
| `curriculum_nodes` | Subject → Chapter → Topic hierarchy |
| `notifications` | System-wide notification center |
| `approval_workflows` | Multi-step approval tracking |

---

## 8. API Endpoints (v2.0 — New)

| Endpoint | Role | Purpose |
|----------|------|---------|
| `POST /auth/register` | All | Multi-role registration |
| `POST /tutor/register` | Tutor | Submit profile + documents |
| `POST /tutor/verify` | AI | AI verification of documents |
| `GET /tutor/dashboard` | Tutor | Student analytics view |
| `POST /content/upload` | Admin | Upload PDF/notes |
| `POST /content/generate` | AI | Generate lessons from PDF |
| `POST /content/review` | Tutor | Approve/modify/reject content |
| `GET /content/lessons` | Student | Personalized lesson feed |
| `POST /assessment/subjective` | Student | Upload handwritten answer |
| `POST /assessment/evaluate` | AI | OCR + evaluate answer |
| `GET /principal/dashboard` | Principal | Institution-wide view |
| `GET /admin/dashboard` | Admin | Organization-wide analytics |
| `POST /admin/approve` | Admin | Approve tutor/content |
| `POST /tutor/feedback` | Tutor | Submit student feedback |

---

## Next: Database Schema → [database-schema.md](./database-schema.md)
