# Product Analysis — Math Tutor AI Agent

> **Date:** 2026-06-19
> **Author:** WorkCore (RCore)
> **Status:** Complete

---

## 1. Reference Application: Manju Tutor

**URL:** https://hinglish-math-mentor--aks321.replit.app/

### 1.1 Overview

Manju Tutor is a single-page React application (Vite + React) that offers AI-powered Hinglish math tutoring for school students in North India. It's a minimal viable product — essentially a chatbot interface with math tutoring capabilities.

### 1.2 Technical Architecture

| Aspect | Detail |
|--------|--------|
| **Frontend** | React SPA (Vite build), Inter font family |
| **Backend** | Not visible (SPA-only frontend exposed) |
| **State Management** | React built-in (no Redux/Zustand visible) |
| **AI Integration** | Single-model chat interface (likely GPT-based) |
| **Languages** | Hinglish (Hindi + English hybrid) only |
| **Target Audience** | School students in North India |
| **Deployment** | Replit hosting |

### 1.3 Features Detected

| Feature | Present | Quality |
|---------|---------|---------|
| Chat interface | ✅ | Basic |
| Math tutoring | ✅ | Single-prompt style |
| Hinglish support | ✅ | Mixed Hindi-English |
| Multi-language support | ❌ | Hindi/English mix only |
| Grade-level adaptation | ❌ | No grade selection |
| Progress tracking | ❌ | No persistence visible |
| Voice input | ❌ | Text only |
| Voice output | ❌ | Text only |
| Quiz generation | ❌ | Not present |
| Parent reports | ❌ | Not present |
| Student profiles | ❌ | No login/profiles |
| Adaptive difficulty | ❌ | No learning path |
| Curriculum alignment | ❌ | Not structured |
| Mobile responsive | ⚠️ | Basic viewport meta only |
| Offline support | ❌ | Not present |

### 1.4 Critical Gaps in Reference App

1. **No Personalization** — Every student gets the same experience regardless of age/grade
2. **No Progress Tracking** — Session data is lost on refresh
3. **No Assessment** — Cannot measure learning outcomes
4. **No Voice** — Text-only interaction misses younger students and accessibility
5. **Single Language** — Excludes Bengali-speaking students and non-Hinglish speakers
6. **No Parent Involvement** — Parents have zero visibility into learning
7. **No Curriculum Structure** — Random tutoring without systematic coverage
8. **No Answer Verification** — Relies purely on LLM which can hallucinate math
9. **No Offline Capability** — Requires constant internet
10. **No Security** — No authentication, no data protection

---

## 2. Competitive Landscape

### 2.1 Direct Competitors

#### Saraswat AI (saraswatai.org)
- **Strengths:** Bengali + Hindi multilingual, mobile-first, Indian curriculum alignment, social mission (1 paid = 10 free)
- **Weaknesses:** Early stage, limited math depth, no adaptive learning demonstrated
- **Target:** K-12 students, Indian curriculum
- **Model:** Freemium with social impact angle

#### AI Math Tutor (aimathtutor.in)
- **Strengths:** NCERT/CBSE aligned, voice tutoring, structured practice, teacher dashboards
- **Weaknesses:** Limited to grades 1-10, English-primary, less AI sophistication
- **Target:** Indian school students, parents, tutoring centers
- **Model:** Practice-based with voice interface

#### MeraTutor.AI
- **Strengths:** Multi-subject (Math, Science, Hindi), parent/teacher dashboards
- **Weaknesses:** Broad focus dilutes math specialization
- **Target:** K-12 Indian students
- **Model:** Subject-wise AI tutoring

#### Vidya AI (Google Play)
- **Strengths:** Voice-enabled, image-based doubt solving, adaptive quizzes, streaks/gamification
- **Weaknesses:** Mobile-only, broader subject focus
- **Target:** Modern learners
- **Model:** App-based gamified learning

### 2.2 Global Competitors

| Product | Key Feature | Gap for Indian Market |
|---------|------------|----------------------|
| Khan Academy (Khanmigo) | AI tutor + structured curriculum | US-centric, no Indian languages |
| Duolingo Math | Gamified math | No Indian curriculum alignment |
| Photomath | Camera-based solving | No teaching, just solving |
| MathMentor | Free AI tutoring | English only, no Indian curriculum |
| ChatGPT | General AI | No educational structure, no guardrails |

### 2.3 Competitive Gap Analysis

| Capability | Manju Tutor | Saraswat | AIMathTutor | **Our Target** |
|------------|-------------|----------|-------------|----------------|
| Multilingual (EN/HI/BN) | ⚠️ HI only | ✅ | ❌ | ✅ |
| Grade adaptation (N-10) | ❌ | ⚠️ | ✅ 1-10 | ✅ N-10 |
| Voice input/output | ❌ | ❌ | ⚠️ Voice | ✅ Full |
| Adaptive learning path | ❌ | ❌ | ⚠️ | ✅ AI-driven |
| Multi-agent AI | ❌ | ❌ | ❌ | ✅ 8 agents |
| Student digital twin | ❌ | ❌ | ❌ | ✅ |
| Parent reports | ❌ | ✅ | ✅ | ✅ |
| Answer verification | ❌ | ❌ | ❌ | ✅ SymPy |
| Offline support | ❌ | ⚠️ Packs | ❌ | ✅ PWA |
| Curriculum knowledge base | ❌ | ❌ | ✅ | ✅ RAG |
| Gamification | ❌ | ❌ | ⚠️ | ✅ |
| Progress analytics | ❌ | ❌ | ⚠️ | ✅ Advanced |

---

## 3. Target Market Analysis

### 3.1 Indian K-10 Education Market

| Metric | Data |
|--------|------|
| K-10 students in India | ~250 million |
| Hindi-speaking students | ~140 million |
| Bengali-speaking students | ~30 million |
| Smartphone penetration | ~75% in urban, ~45% rural |
| EdTech market size (2025) | ~$10 billion |
| After-school tutoring market | ~$15 billion |
| Willingness to pay for education | High (cultural priority) |

### 3.2 User Personas

#### Persona 1: Priya (Age 8, Class 3, Hindi-medium)
- Struggles with multiplication tables
- Parents speak Hindi at home
- Has access to mother's smartphone
- Needs: Visual learning, Hindi explanations, encouragement

#### Persona 2: Arjun (Age 14, Class 9, English-medium)
- Preparing for board exams
- Weak in algebra and geometry
- Has own phone + laptop
- Needs: Exam prep, step-by-step solutions, practice papers

#### Persona 3: Riya (Age 5, Nursery, Bengali-medium)
- Learning numbers and shapes
- Parents want early math exposure
- Limited screen time
- Needs: Stories, visuals, Bengali voice interaction

#### Persona 4: Mrs. Sharma (Parent of Class 6 student)
- Concerned about child's math performance
- Wants visibility into progress
- Limited time to help with homework
- Needs: Progress reports, weak area identification, recommendations

### 3.3 Monetization Opportunities

| Tier | Price Point (INR) | Features |
|------|-------------------|----------|
| Free | ₹0 | 5 questions/day, 1 language, basic tutoring |
| Basic | ₹199/month | Unlimited questions, 3 languages, progress tracking |
| Premium | ₹499/month | Voice, quizzes, parent reports, offline access |
| Family | ₹799/month | Up to 3 students, detailed analytics, priority support |

---

## 4. Product Opportunity Assessment

### 4.1 Why This Will Win

1. **Multilingual First** — No competitor does English + Hindi + Bengali with full voice support for Nursery to Class 10
2. **Multi-Agent AI** — 8 specialized agents vs. competitors' single-chatbot approach
3. **Student Digital Twin** — Persistent adaptive profile that improves with every session
4. **Math-Verified Answers** — SymPy verification eliminates LLM hallucination risk
5. **Full Age Spectrum** — Nursery to Class 10 with age-appropriate teaching styles
6. **Parent Trust** — Transparent progress reports build long-term retention
7. **Open Architecture** — Multi-model routing, provider-agnostic design

### 4.2 MVP Scope (Phase 1)

| Feature | Priority |
|---------|----------|
| Text-based tutoring (EN/HI/BN) | P0 |
| Grade selection (1-10) | P0 |
| Teacher Agent + Assessment Agent | P0 |
| Student profiles + progress tracking | P0 |
| Hint → Guide → Solve methodology | P0 |
| SymPy answer verification | P0 |
| Voice input (STT) | P1 |
| Voice output (TTS) | P1 |
| Quiz/practice generation | P1 |
| Parent reports | P1 |
| Curriculum RAG knowledge base | P1 |
| Nursery-KG support | P2 |
| Offline PWA | P2 |
| Gamification | P2 |
| Admin dashboard | P2 |

---

## 5. Key Product Decisions

### 5.1 Learning Methodology

**Never give answers first.** The system follows:
```
Hint → Guided Thinking → Step-by-Step → Final Answer
```

### 5.2 Age-Aware Teaching

| Age Group | Grade | Approach |
|-----------|-------|----------|
| 3-5 | Nursery-KG | Stories, visuals, counting, shapes, songs |
| 6-8 | 1-2 | Games, manipulatives, basic arithmetic |
| 8-10 | 3-5 | Word problems, multiplication, fractions |
| 11-13 | 6-8 | Algebra intro, geometry, data handling |
| 14-16 | 9-10 | Advanced algebra, trigonometry, statistics, exam prep |

### 5.3 Error Handling Philosophy

When a student makes a mistake:
1. **Don't say "wrong"** — say "Let's think about this differently"
2. **Identify the misconception** — what specific concept is missing?
3. **Address the root cause** — teach the prerequisite concept
4. **Practice the corrected approach** — reinforce with similar problems
5. **Update the digital twin** — record the mistake pattern

---

## Next: PRD Creation
