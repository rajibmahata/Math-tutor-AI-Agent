# Implementation Roadmap — VidyaMitra v2.0

> **Date:** 2026-06-19 | **Version:** 2.0

---

## 1. Phase Summary

| Phase | Scope | Timeline |
|-------|-------|----------|
| **v1.0 (Complete)** | Math tutoring — Student + AI chat + Voice | ✅ Done |
| **v2.0 — Foundation** | Multi-role auth, Tutor/Principal/Admin portals | Weeks 1-4 |
| **v2.0 — Content Engine** | PDF upload → AI lessons → Tutor validation | Weeks 5-8 |
| **v2.0 — Assessment** | Subjective + image-based assessment | Weeks 9-10 |
| **v2.0 — Launch** | Production deploy, testing, docs | Weeks 11-12 |

---

## 2. v2.0 Sprint Plan

### Sprint 2.1: Multi-Role Auth + Profiles (Week 1-2)

| Task | Est. |
|------|------|
| Extend users table: phone, location, role expansion | 4h |
| Create tutors, principals tables + migrations | 4h |
| Tutor registration API + document upload | 6h |
| Principal profile + assignment API | 3h |
| Role-based auth middleware (4 roles) | 4h |
| Tutor dashboard page | 6h |
| Principal dashboard page | 4h |
| Super Admin dashboard page | 4h |
| Role-switching in frontend layout | 3h |

### Sprint 2.2: Curriculum + Content Generation (Week 3-4)

| Task | Est. |
|------|------|
| curriculum_nodes table + seed data (NCERT K-12) | 6h |
| source_documents table + PDF upload endpoint | 4h |
| PDF text extraction service (PyMuPDF) | 6h |
| Content Generation Agent (PDF → lessons) | 8h |
| Content Personalization Agent (language/region/culture) | 6h |
| content_lessons + content_reviews tables | 4h |
| Content review API (tutor approve/modify/reject) | 6h |

### Sprint 2.3: Video + Voice Generation (Week 5-6)

| Task | Est. |
|------|------|
| Video Generation Agent (Remotion integration) | 8h |
| Multi-language voice narration for videos | 4h |
| Voice Agent enhancement (streaming, accent) | 4h |
| Content delivery API (personalized feed) | 4h |
| Student content browsing UI | 6h |
| Video player component | 3h |

### Sprint 2.4: Assessment Engine v2 (Week 7-8)

| Task | Est. |
|------|------|
| Subjective assessment submission (image upload) | 4h |
| OCR integration (Tesseract / Azure Vision) | 6h |
| AI subjective evaluation agent | 6h |
| Diagram analysis pipeline | 6h |
| Tutor feedback on assessments | 4h |
| Assessment results UI with AI + tutor feedback | 6h |

### Sprint 2.5: Admin + Governance (Week 9-10)

| Task | Est. |
|------|------|
| approval_workflows table + API | 4h |
| Tutor approval workflow (AI → Principal → Admin) | 6h |
| Verification Agent (document checking) | 6h |
| notifications table + system | 4h |
| Super Admin dashboard: approve/reject | 4h |
| Matching Agent: tutor-student assignment | 4h |
| Organization analytics API | 4h |

### Sprint 2.6: Testing + Launch (Week 11-12)

| Task | Est. |
|------|------|
| Integration tests (all workflows) | 8h |
| E2E tests (Playwright) | 6h |
| Performance optimization | 6h |
| Security audit | 4h |
| Production deployment | 4h |
| Documentation | 4h |

---

## 3. Team Allocation (v2.0)

| Role | Agent | Focus |
|------|-------|-------|
| Architect | WorkCore | Architecture, agent design |
| Backend | rajiblabs-dev-backend | FastAPI, DB, services |
| Frontend | rajiblabs-dev-frontend | Next.js portals |
| AI Engineer | WorkCore | 12-agent system, content gen |
| QA | rajiblabs-qa | Testing all workflows |
| DevOps | rajiblabs-devops | Deployment, CI/CD |

---

## 4. Risk Register (v2.0)

| Risk | Impact | Mitigation |
|------|--------|------------|
| PDF extraction quality | High | Multi-engine: PyMuPDF + OCR fallback |
| AI video generation cost | Medium | Start with static videos, add AI later |
| Tutor verification accuracy | Medium | Human-in-the-loop for borderline cases |
| Multi-language TTS quality | Medium | Multi-provider chain: ElevenLabs → Azure → OpenAI |
| Subjective assessment accuracy | High | AI scores with tutor review overlay |
| Approval workflow bottlenecks | Low | Auto-escalation after timeout |

---

## Next: API Specification → [api-specification.md](./api-specification.md)
