# Product Requirements Document (PRD) — Math Tutor AI Agent

> **Date:** 2026-06-19
> **Version:** 1.0
> **Status:** Draft
> **Author:** WorkCore (RCore)

---

## 1. Product Vision

**An adaptive AI math teacher that speaks every Indian student's language, understands their unique learning journey, and grows with them from Nursery to Class 10.**

We are not building a chatbot. We are building a personal math tutor that:
- Remembers every student by name
- Knows their strengths and weaknesses
- Adapts teaching style to age and language
- Never gives up on a concept
- Keeps parents informed and reassured

---

## 2. Product Name

**GanitMitra** (गणित मित्र / গণিত মিত্র)
— "Math Friend" in Hindi and Bengali

---

## 3. Target Users

### Primary Users
- **Students:** Age 3-16, Nursery to Class 10
- **Languages:** English, Hindi, Bengali
- **Geography:** India (primary), global Indian diaspora (secondary)

### Secondary Users
- **Parents:** Monitor progress, receive reports, set goals
- **Teachers/Tutors:** Manage multiple students, assign practice

---

## 4. Core Features (MoSCoW)

### 🔴 Must Have (MVP)

| ID | Feature | Description |
|----|---------|-------------|
| F1 | **Multilingual Chat Tutoring** | Text-based math tutoring in EN/HI/BN with age-appropriate responses |
| F2 | **Grade Selection** | Student selects or is placed in appropriate grade (N-10) |
| F3 | **Teacher Agent** | AI that teaches using Hint → Guide → Solve methodology |
| F4 | **Assessment Agent** | Evaluates student answers, identifies misconceptions |
| F5 | **Student Digital Twin** | Persistent profile: age, grade, strengths, weaknesses, progress |
| F6 | **Hint → Guide → Solve** | Never gives direct answers; progressive scaffolding |
| F7 | **SymPy Verification** | All math answers verified computationally |
| F8 | **Progress Dashboard** | Student view of topics mastered, in-progress, not started |
| F9 | **Authentication** | Secure login (email/password + Google OAuth) |
| F10 | **Session Persistence** | All sessions saved, resumable |

### 🟡 Should Have (V1.1)

| ID | Feature | Description |
|----|---------|-------------|
| F11 | **Voice Input (STT)** | Speech-to-text for questions in all 3 languages |
| F12 | **Voice Output (TTS)** | Text-to-speech for responses in all 3 languages |
| F13 | **Practice Quiz Generator** | Auto-generates topic-specific practice sets |
| F14 | **Parent Report Agent** | Weekly progress reports, weak area alerts |
| F15 | **Curriculum RAG** | NCERT/CBSE/State board curriculum knowledge base |
| F16 | **Multi-Model Routing** | Fast model for chat, reasoning model for math, translation model |
| F17 | **Gamification Basics** | Points, badges, streaks |

### 🟢 Could Have (V1.2)

| ID | Feature | Description |
|----|---------|-------------|
| F18 | **Nursery-KG Mode** | Visual stories, shapes, counting with animations |
| F19 | **Exam Prep Mode** | Board exam paper practice, mock tests |
| F20 | **Offline PWA** | Progressive web app with offline capability |
| F21 | **Teacher Dashboard** | Classroom management for tutors/teachers |
| F22 | **Advanced Analytics** | Learning velocity, confidence trends, prediction |

### 🔵 Won't Have (V1)

| ID | Feature | Reason |
|----|---------|--------|
| W1 | Video-based tutoring | Scope — text+voice sufficient for MVP |
| W2 | Live human tutor connection | Different product category |
| W3 | Subjects beyond Math | Stay focused on math specialization |
| W4 | Mobile native apps | PWA approach preferred |

---

## 5. User Journeys

### 5.1 New Student Onboarding

```
1. Student visits GanitMitra
2. Clicks "Start Learning" → Sign Up / Login
3. Enters: Name, Age, Grade, Preferred Language
4. Takes quick placement assessment (5 questions)
5. System creates Digital Twin profile
6. Lands on personalized dashboard
7. First tutoring session begins
```

### 5.2 Daily Learning Session

```
1. Student logs in → sees dashboard
2. System suggests "Today's Topic" based on curriculum + weak areas
3. Student asks question or accepts suggestion
4. Teacher Agent provides hint
5. Student attempts answer
6. Assessment Agent evaluates → Right? Move on | Wrong? Scaffold
7. Session saved to digital twin
8. Streak updated, points earned
9. Student sees session summary
```

### 5.3 Parent Check-In

```
1. Parent logs in → sees child's dashboard
2. Views: Topics mastered, current focus, weak areas
3. Reads: Weekly progress summary
4. Sees: Time spent, questions attempted, accuracy
5. Receives: Recommendation for support at home
6. Optional: Sets daily practice goal
```

### 5.4 Practice Mode

```
1. Student selects "Practice" from dashboard
2. Chooses: Topic, difficulty, question count
3. Practice Agent generates problems
4. Student solves one at a time
5. Immediate feedback after each
6. End-of-practice score + detailed breakdown
7. Weak areas flagged for future tutoring
```

---

## 6. Functional Requirements

### 6.1 Tutoring Engine

| Requirement | Detail |
|-------------|--------|
| Hint generation | Progressive hints (3 levels before solution) |
| Solution steps | Break every problem into logical steps |
| Answer evaluation | Compare to SymPy-verified answer, not just LLM output |
| Misconception detection | Pattern-matching common errors (e.g., order of operations) |
| Re-teaching | If wrong, teach prerequisite concept before retry |
| Difficulty adjustment | Auto-scale based on success rate (80% target) |
| Language switching | Mid-session language change support |

### 6.2 Student Digital Twin

| Field | Type | Update Trigger |
|-------|------|----------------|
| Age | Integer | Profile / birthday |
| Grade | Enum(N-10) | Profile / auto-promotion |
| Preferred Language | Enum(EN/HI/BN) | Profile |
| Learning Speed | Float (1-10) | Per session |
| Topic Strengths | JSON {topic: score} | Per question |
| Topic Weaknesses | JSON {topic: score} | Per question |
| Mistake Patterns | JSON [{pattern, count}] | Per error |
| Confidence Score | Float (0-1) | Per session |
| Session History | Relation | Per session |
| Questions Attempted | Integer (cumulative) | Per question |
| Accuracy Rate | Float (%) | Per question |

### 6.3 Multi-Agent System

See [Agent Design Document](./agent-design.md) for full detail.

| Agent | Responsibility |
|-------|---------------|
| Teacher Agent | Primary interaction, hint-based tutoring |
| Assessment Agent | Answer evaluation, misconception detection |
| Curriculum Agent | Topic sequencing, curriculum alignment |
| Practice Agent | Quiz/practice set generation |
| Motivation Agent | Encouragement, streaks, gamification |
| Analytics Agent | Progress computation, trend analysis |
| Parent Report Agent | Weekly digest generation |
| Voice Agent | STT/TTS orchestration |

### 6.4 Multi-Model Strategy

| Task | Model | Reason |
|------|-------|--------|
| Chat/Interaction | GPT-4o-mini / Claude Haiku | Fast, cost-effective |
| Math Reasoning | GPT-4o / Claude Sonnet / DeepSeek V4 | Strong reasoning needed |
| Translation | GPT-4o / Claude (native multilingual) | Built-in capability |
| Voice STT | Whisper (OpenAI) | Best accuracy for Indian languages |
| Voice TTS | ElevenLabs / Azure TTS | Natural voice output |
| Math Verification | SymPy (local) | Deterministic, zero hallucination |

### 6.5 Content & Curriculum

| Board | Coverage |
|-------|----------|
| NCERT/CBSE | Full K-10 mathematics |
| ICSE | K-10 mathematics |
| West Bengal Board | Bengali-medium mathematics |
| State Boards | Common core topics |

Topics organized by grade with prerequisite mappings in the RAG knowledge base.

---

## 7. Non-Functional Requirements

### 7.1 Performance

| Metric | Target |
|--------|--------|
| First response (chat) | < 2 seconds |
| Math reasoning response | < 5 seconds |
| Voice STT processing | < 3 seconds |
| Page load (LCP) | < 2.5 seconds |
| Concurrent users | 1,000 (MVP), 10,000 (scale) |
| API p95 latency | < 500ms |

### 7.2 Security

| Requirement | Detail |
|-------------|--------|
| Authentication | JWT + refresh tokens |
| Authorization | Role-based (student, parent, admin) |
| Data encryption | At rest (AES-256) + in transit (TLS 1.3) |
| Input sanitization | All user inputs sanitized |
| Rate limiting | Per-user, per-IP |
| Content filtering | No inappropriate content generation |
| Data privacy | COPPA-compliant for under-13 users |
| GDPR basics | Data export, account deletion |
| LLM prompt injection | Guardrails against jailbreak attempts |

### 7.3 Reliability

| Metric | Target |
|--------|--------|
| Uptime | 99.5% |
| Data backup | Daily, 30-day retention |
| Disaster recovery | < 4 hour RTO |
| Session persistence | Auto-save every interaction |

### 7.4 Accessibility

| Standard | Level |
|----------|-------|
| WCAG 2.1 | AA |
| Screen reader | Compatible |
| Keyboard navigation | Full |
| Color contrast | 4.5:1 minimum |
| Font scaling | Up to 200% |

---

## 8. Success Metrics

### 8.1 Product KPIs

| Metric | Target (3 months) | Target (12 months) |
|--------|-------------------|---------------------|
| Registered students | 5,000 | 50,000 |
| DAU (Daily Active Users) | 500 | 5,000 |
| Avg. session duration | 15 min | 20 min |
| Sessions per week per user | 3 | 5 |
| Topic mastery rate | 70% | 85% |
| Parent report opens | 60% | 80% |
| Free → Paid conversion | 5% | 8% |
| Churn rate | < 10%/month | < 5%/month |

### 8.2 Learning Outcomes

| Metric | Target |
|--------|--------|
| Accuracy improvement (30 days) | +15% |
| Weak area resolution (2 weeks) | 60% of flagged topics |
| Grade-level readiness | 80% of students at/above grade level |
| Student confidence score increase | +0.2 (on 0-1 scale) |

---

## 9. Constraints & Assumptions

### Constraints
- Must work on low-end smartphones (2GB RAM)
- Must handle intermittent connectivity
- Hindi/Bengali TTS quality limited by available models
- Indian K-10 curriculum varies by state/board

### Assumptions
- Students have basic digital literacy or parental assistance
- Internet connectivity available (not offline-first for MVP)
- Parents willing to pay for quality math tutoring
- LLM APIs remain accessible and affordable

---

## 10. Out of Scope (V1)

- Non-math subjects
- Live video tutoring
- School ERP integration
- Government scheme integration
- Physical workbook generation
- AR/VR experiences

---

## Next: System Architecture → [architecture.md](./architecture.md)
