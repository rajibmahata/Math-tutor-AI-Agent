# Product Requirements Document (PRD) — AI Student Tutor Platform

> **Date:** 2026-06-19 | **Version:** 2.0 | **Status:** Updated
> **Author:** WorkCore (RCore)

---

## 1. Product Vision

**An AI-powered personalized learning platform that transforms educational content into interactive, voice-enabled, adaptive learning experiences — with human oversight at every stage.**

The platform serves Students, Tutors, Principals, and Super Admins in a complete educational ecosystem where AI generates and personalizes content, and human experts validate quality.

---

## 2. Product Name

**GanitMitra → VidyaMitra**
(विद्या मित्र / বিদ্যা মিত্র — "Knowledge Friend")

---

## 3. Target Users

| Role | Description | Count |
|------|-------------|-------|
| **Student** | Learner consuming personalized content | Primary (unlimited) |
| **Tutor** | Subject expert validating AI content | Medium (per subject) |
| **Principal** | Academic supervisor, quality assurance | Few (per institution) |
| **Super Admin** | Platform governance, compliance | 1-2 per org |

---

## 4. Core Features (MoSCoW)

### 🔴 Must Have (MVP v2.0)

| ID | Feature | Role |
|----|---------|------|
| F1 | Multi-role auth (Student/Tutor/Principal/Admin) | All |
| F2 | Student registration with learning preferences | Student |
| F3 | AI Student Profile (Digital Twin v2) | Student |
| F4 | Subject → Chapter → Topic navigation | Student |
| F5 | Personalized content delivery (text + audio + video) | Student |
| F6 | Voice-based conversational learning | Student |
| F7 | AI Tutor with Hint→Guide→Solve methodology | Student |
| F8 | Assessment Engine (MCQ + Short Answer + Subjective) | Student |
| F9 | AI answer evaluation with SymPy + handwriting OCR | Student |
| F10 | Progress tracking dashboard with gamification | Student |
| F11 | Tutor registration + document verification workflow | Tutor |
| F12 | AI content generation (PDF → Lessons → Video) | Tutor/Admin |
| F13 | Content validation pipeline (Tutor review → Publish) | Tutor |
| F14 | Tutor dashboard (student performance, analytics) | Tutor |
| F15 | Principal dashboard (monitor tutors, quality) | Principal |
| F16 | Super Admin dashboard (org-wide analytics) | Admin |
| F17 | AI Analytics Engine (learning patterns, trends) | All |

### 🟡 Should Have (V2.1)

| ID | Feature |
|----|---------|
| F18 | AI Video Generation (animated concept explanations) |
| F19 | Intelligent Tutor Matching (subject + language + region) |
| F20 | Tutor reassignment workflow |
| F21 | Parent dashboard |
| F22 | Multi-language content personalization |
| F23 | Regional/cultural content adaptation |
| F24 | Learning marketplace |

### 🟢 Could Have (V2.2)

| ID | Feature |
|----|---------|
| F25 | Live AI Avatar Tutor |
| F26 | Real-time classroom |
| F27 | Multi-school support |
| F28 | Career guidance AI |
| F29 | Emotional learning analytics |
| F30 | Offline mobile learning (PWA) |

---

## 5. User Journeys

### 5.1 Student Learning Journey

```
1. Register → Profile (age, grade, language, interests)
2. AI creates learning profile (Digital Twin v2)
3. Select Subject → Chapter → Topic
4. AI delivers personalized content (text/audio/video)
5. Voice-based Q&A with AI Tutor
6. Complete exercises + practice
7. Take Mock Test (MCQ + Short Answer + Subjective)
8. AI identifies weak areas → personalized revision
9. Take Final Assessment
10. View progress dashboard (scores, badges, streaks)
```

### 5.2 Tutor Workflow

```
1. Register → Upload qualifications
2. AI Verification Agent checks documents
3. Principal reviews → Super Admin approves
4. Access Tutor Dashboard
5. Review AI-generated content → Approve/Modify/Reject
6. Monitor student progress
7. Provide personalized feedback
```

### 5.3 Content Creation Pipeline

```
Admin uploads PDF/notes
  → AI extracts content + creates embeddings
  → AI generates: lesson plans, summaries, explanations
  → AI generates: videos, voice narration, examples
  → Tutor validates (accuracy, completeness, alignment)
  → Content published to knowledge base
  → Students access personalized versions
```

---

## 6. Functional Requirements

### 6.1 Student Module

| Requirement | Detail |
|-------------|--------|
| Registration | Name, age, gender, class, school, location, language preference |
| AI Profile | Dynamic profile: learning speed, strengths, weaknesses, interests |
| Subject nav | Browse subjects → chapters → topics |
| Content types | Text lessons, audio, video, interactive exercises |
| Voice learning | Ask questions verbally, receive spoken responses |
| Assessments | MCQ, fill-in-blanks, match, short answer, subjective (image upload) |
| Progress | Dashboard with scores, streaks, badges, recommendations |

### 6.2 Tutor Module

| Requirement | Detail |
|-------------|--------|
| Registration | Personal + professional details, qualification documents |
| AI Verification | Auto-verify degrees, certificates, consistency |
| Approval | Principal review → Super Admin approval workflow |
| Content validation | Review AI-generated content, approve/modify/reject |
| Student monitoring | View progress, scores, weak areas per student |
| Feedback | Personalized feedback, study plans, recommendations |

### 6.3 Principal Module

| Requirement | Detail |
|-------------|--------|
| Dashboard | Student + tutor data, platform analytics |
| Tutor monitoring | Performance, activity, content reviews |
| Quality assurance | Approve escalations, ensure standards |
| Content governance | Review published content quality |

### 6.4 Super Admin Module

| Requirement | Detail |
|-------------|--------|
| Organization dashboard | Platform-wide visibility |
| User management | Manage principals, tutors, students |
| Approval workflows | Final approval for tutors, content |
| Analytics | Total users, engagement, outcomes |
| Notifications | New tutor requests, content alerts, escalations |

---

## 7. AI Agent Architecture (v2.0 — Expanded)

| # | Agent | Role |
|---|-------|------|
| 1 | **Teacher Agent** | Conversational voice tutoring, personalized explanations |
| 2 | **Assessment Agent** | Evaluate answers (MCQ + text + image), scoring |
| 3 | **Curriculum Agent** | Subject → Chapter → Topic sequencing, knowledge graph |
| 4 | **Content Generation Agent** | PDF → lessons, summaries, videos |
| 5 | **Content Personalization Agent** | Adapt by language, region, culture, grade |
| 6 | **Video Generation Agent** | Auto-create animated concept explanations |
| 7 | **Verification Agent** | Verify tutor qualifications, documents |
| 8 | **Matching Agent** | Intelligent tutor-student matching |
| 9 | **Analytics Agent** | Learning patterns, trends, predictions |
| 10 | **Motivation Agent** | Encouragement, streaks, gamification |
| 11 | **Voice Agent** | STT/TTS for all supported languages |
| 12 | **Report Agent** | Student, tutor, principal, admin reports |

### Multi-Model AI Strategy

| Task | Model | Provider |
|------|-------|----------|
| Conversational teaching | GPT-4o / DeepSeek V4 | OpenAI / DeepSeek |
| Content generation | GPT-4o | OpenAI |
| Video generation | Sora / RunwayML | OpenAI / Third-party |
| Translation & localization | GPT-4o (multilingual) | OpenAI |
| Voice STT | Whisper | OpenAI |
| Voice TTS | ElevenLabs / Azure / OpenAI | Multi-provider |
| Math verification | SymPy | Local |
| Document OCR | Tesseract / Azure Vision | Local / Azure |
| Embeddings | text-embedding-3-small | OpenAI |

---

## 8. Success Metrics

| Metric | Target (6 months) |
|--------|-------------------|
| Registered students | 10,000 |
| Active tutors | 200 |
| Content lessons published | 5,000 |
| Student engagement (DAU) | 2,000 |
| Tutor content approval rate | >85% |
| Student learning velocity | +20% |
| NPS (Student) | >50 |
| NPS (Tutor) | >40 |

---

## Next: Architecture → [architecture.md](./architecture.md)
