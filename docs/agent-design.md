# AI Agent Design — AI Student Tutor Platform v2.1 (Revised)

> **Date:** 2026-06-20 | **Version:** 2.1 | **Framework:** LangGraph

---

## 1. Agent Architecture Overview (12 Agents)

```
┌──────────────────────────────────────────────────────────────┐
│              LANGGRAPH ORCHESTRATOR (StateGraph)              │
│                                                               │
│  STUDENT-FACING AGENTS          BACKEND/PIPELINE AGENTS      │
│  ┌─────────────────┐           ┌─────────────────┐          │
│  │ 1. Teacher      │           │ 5. Content Gen  │          │
│  │    Agent         │           │    Agent         │          │
│  ├─────────────────┤           ├─────────────────┤          │
│  │ 2. Assessment   │           │ 6. Personalize  │          │
│  │    Agent         │           │    Agent         │          │
│  ├─────────────────┤           ├─────────────────┤          │
│  │ 3. Curriculum   │           │ 7. Video Gen    │          │
│  │    Agent         │           │    Agent         │          │
│  ├─────────────────┤           ├─────────────────┤          │
│  │ 4. Motivation   │           │ 8. Verification │          │
│  │    Agent         │           │    Agent         │          │
│  ├─────────────────┤           ├─────────────────┤          │
│  │ 9. Voice Agent  │           │ 10. Matching    │          │
│  │                  │           │     Agent        │          │
│  ├─────────────────┤           ├─────────────────┤          │
│  │                  │           │ 11. Analytics   │          │
│  │                  │           │     Agent        │          │
│  ├─────────────────┤           ├─────────────────┤          │
│  │                  │           │ 12. Report      │          │
│  │                  │           │     Agent        │          │
│  └─────────────────┘           └─────────────────┘          │
└──────────────────────────────────────────────────────────────┘
```

---

## 2. Agent Details

### Agent 1: Teacher Agent
- **Purpose:** Conversational voice tutoring with personalized explanations
- **Input:** Student question, learning profile, language preference
- **Output:** Age-appropriate explanation, hint, or guided thinking
- **Methodology:** Hint → Guide → Solve (never answer first)
- **Model:** GPT-4o / DeepSeek V4 (reasoning)
- **Languages:** EN, HI, BN, TA (expandable)

### Agent 2: Assessment Agent
- **Purpose:** Evaluate all answer types and generate scores
- **Input Types:** MCQ selection, text answer, image upload (handwriting)
- **Verification:** SymPy (math), OCR + semantic (subjective), rule engine (MCQ)
- **Output:** Score, misconception detection, feedback, recommended review
- **Model:** GPT-4o + SymPy + Tesseract OCR

### Agent 3: Curriculum Agent
- **Purpose:** Manage subject→chapter→topic hierarchy and learning paths
- **Knowledge Graph:** Prerequisites, dependencies, grade-level mapping
- **Output:** Next topic recommendation, curriculum coverage %
- **RAG:** Qdrant vector search for curriculum-aligned content

### Agent 4: Motivation Agent
- **Purpose:** Keep students engaged with gamification and encouragement
- **Features:** Streaks, badges, points, leaderboards, celebrations
- **Personalization:** Age-appropriate tone, language-specific encouragement
- **Model:** GPT-4o-mini (fast, warm tone)

### Agent 5: Content Generation Agent
- **Purpose:** Transform uploaded PDFs/notes into structured lessons
- **Pipeline:** Extract → Chunk → Embed → Generate
- **Outputs:** Lesson plans, chapter summaries, topic explanations, examples, exercises
- **Model:** GPT-4o (long context)
- **Storage:** PostgreSQL (metadata) + Qdrant (embeddings)

### Agent 6: Content Personalization Agent
- **Purpose:** Adapt content for language, region, culture, grade
- **Parameters:** Language (EN/HI/BN/TA), Region (urban/rural/state), Grade (N-12), Interests
- **Examples:** Kolkata-based word problems, Chennai-localized examples
- **Model:** GPT-4o (multilingual native)

### Agent 7: Video Generation Agent
- **Purpose:** Auto-create animated concept explanation videos
- **Input:** Lesson text, topic, grade level
- **Output:** Short educational video with voice narration
- **Technology:** Remotion (programmatic video) / RunwayML (AI video)
- **Voice:** Regional language + accent via ElevenLabs/Azure TTS

### Agent 8: Verification Agent
- **Purpose:** Auto-verify tutor qualification documents
- **Input:** Degree certificates, experience documents, ID proofs
- **Process:** OCR → Extract info → Cross-reference → Flag inconsistencies
- **Output:** Verification report with confidence score
- **Model:** GPT-4o + Azure Vision OCR

### Agent 9: Voice Agent
- **Purpose:** Handle all voice interactions (STT + TTS)
- **STT:** Whisper (EN/HI/BN/TA)
- **TTS:** ElevenLabs (primary) / Azure (fallback) / OpenAI (tertiary)
- **Features:** Real-time streaming, language detection, accent support

### Agent 10: Matching Agent
- **Purpose:** Intelligently match tutors to students
- **Criteria:** Subject expertise, language, region, culture, availability
- **Output:** Best-match tutor with confidence score
- **Model:** Rule engine + GPT-4o-mini scoring

### Agent 11: Analytics Agent
- **Purpose:** Analyze platform-wide learning patterns
- **Metrics:** Learning velocity, engagement, knowledge retention, trends
- **Output:** Dashboards for student/tutor/principal/admin
- **Technology:** Python analytics + GPT-4o for insights

### Agent 12: Report Agent
- **Purpose:** Generate reports for all user roles
- **Student:** Progress, performance, recommendations
- **Tutor:** Student outcomes, engagement metrics
- **Principal:** Institution performance
- **Admin:** Organization-wide analytics
- **Model:** GPT-4o (structured output)

---

## 3. Multi-Model Routing

| Task | Primary Model | Fallback |
|------|--------------|----------|
| Conversational teaching | GPT-4o | DeepSeek V4 |
| Content generation | GPT-4o | Claude Sonnet |
| Video scripting | GPT-4o | — |
| Answer evaluation | DeepSeek V4 + SymPy | GPT-4o |
| Translation/Personalization | GPT-4o (multilingual) | DeepSeek |
| OCR + Verification | GPT-4o + Azure Vision | Tesseract |
| Embeddings | text-embedding-3-small | — |
| STT | Whisper | — |
| TTS | ElevenLabs | Azure → OpenAI |
| Fast chat (greetings) | GPT-4o-mini | DeepSeek Chat |
| Analytics insights | GPT-4o | GPT-4o-mini |

---

## 4. Guardrails & Safety (Expanded)

## 5. v2.1 New Agent Capabilities

### 5.1 Feedback Analytics Agent
- **Purpose:** Process student feedback on tutors, compute aggregate ratings
- **Input:** Student ratings + feedback text per tutor
- **Process:** Aggregate scores, detect sentiment, flag low-rated tutors
- **Output:** FeedbackSummary for Tutor/Principal dashboards
- **Trigger:** On new feedback submission, nightly rollup

### 5.2 Report Generation Agent (Enhanced)
- **Purpose:** Generate Tutor Reports to Students with AI-written summaries
- **Input:** Student performance data, learning patterns, knowledge retention
- **Process:** AI writes performance summary, identifies strengths/weak areas, generates recommended study plan
- **Output:** Structured TutorReport visible on Student Dashboard

### 5.3 Notification Dispatch Agent
- **Purpose:** Route notifications to correct role dashboard
- **Triggers:** Content pending (→Tutor), Tutor approval (→Principal), Final approval (→Admin), Feedback alert (→Principal), Report ready (→Student)
- **Output:** Notification with action_url linking to relevant screen

## 6. Guardrails & Safety (Expanded)

- **Content Accuracy:** All AI-generated lessons must pass tutor validation
- **Age-Appropriate:** No violent, scary, or inappropriate examples
- **Academic Integrity:** Detect potential cheating patterns
- **Data Privacy:** COPPA-compliant for under-13, GDPR basics
- **Bias Detection:** Monitor for cultural/regional bias in content
- **Human-in-the-Loop:** Critical decisions (grading, content approval) involve human review

---

## Next: Database Schema → [database-schema.md](./database-schema.md)
