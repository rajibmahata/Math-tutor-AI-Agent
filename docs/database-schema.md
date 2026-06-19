# Database Schema — GanitMitra Math Tutor

> **Date:** 2026-06-19
> **Version:** 1.0
> **Database:** PostgreSQL 16
> **ORM:** SQLAlchemy 2.0 + Alembic

---

## 1. Entity-Relationship Overview

```
┌──────────┐       ┌──────────┐       ┌──────────┐
│  users   │──1:N──│ students │──1:N──│ sessions │
└──────────┘       └──────────┘       └──────────┘
                         │                   │
                         │                   │ 1:N
                         │ 1:N               ▼
                         │           ┌──────────────┐
                         │           │  messages     │
                         │           └──────────────┘
                         │                   │
                         │ 1:N               │ 1:1 (optional)
                         ▼                   ▼
                  ┌──────────┐       ┌──────────────┐
                  │ progress │       │ assessments  │
                  └──────────┘       └──────────────┘
                         │
                         │ N:1
                         ▼
                  ┌──────────┐
                  │  topics  │
                  └──────────┘
                         │
                         │ 1:N
                         ▼
                  ┌──────────────┐
                  │ prerequisites│
                  └──────────────┘

┌──────────┐       ┌──────────┐
│  users   │──1:N──│ practice │
│(parents) │       │  sets    │
└──────────┘       └──────────┘
                         │
                         │ 1:N
                         ▼
                  ┌──────────────┐
                  │  questions   │
                  └──────────────┘

┌──────────┐
│  users   │──1:N──┌──────────────┐
│(parents) │       │  reports     │
└──────────┘       └──────────────┘
```

---

## 2. Complete Schema

### 2.1 users
Core authentication table for all user types.

```sql
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255) UNIQUE NOT NULL,
    password_hash   VARCHAR(255),                          -- NULL for OAuth-only users
    full_name       VARCHAR(255) NOT NULL,
    role            VARCHAR(20) NOT NULL DEFAULT 'student', -- 'student', 'parent', 'admin'
    avatar_url      VARCHAR(500),
    google_id       VARCHAR(255) UNIQUE,                    -- OAuth: Google ID
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    is_verified     BOOLEAN NOT NULL DEFAULT FALSE,
    last_login_at   TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_google_id ON users(google_id);
```

### 2.2 refresh_tokens

```sql
CREATE TABLE refresh_tokens (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash      VARCHAR(255) UNIQUE NOT NULL,
    device_info     VARCHAR(500),
    expires_at      TIMESTAMPTZ NOT NULL,
    revoked_at      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_refresh_tokens_user ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_expires ON refresh_tokens(expires_at);
```

### 2.3 students
Student-specific profile — the "Digital Twin."

```sql
CREATE TABLE students (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    parent_id           UUID REFERENCES users(id) ON DELETE SET NULL,

    -- Basic Profile
    age                 INTEGER NOT NULL CHECK (age >= 3 AND age <= 16),
    grade               VARCHAR(5) NOT NULL,                  -- 'N', 'KG', '1'..'10'
    preferred_language  VARCHAR(5) NOT NULL DEFAULT 'en',     -- 'en', 'hi', 'bn'
    board               VARCHAR(50) DEFAULT 'ncert',          -- 'ncert', 'icse', 'wb_board', etc.

    -- Learning Profile (Digital Twin Core)
    learning_speed      REAL NOT NULL DEFAULT 5.0,            -- 1.0 (slow) to 10.0 (fast)
    confidence_score    REAL NOT NULL DEFAULT 0.5,            -- 0.0 to 1.0
    total_questions     INTEGER NOT NULL DEFAULT 0,
    correct_answers     INTEGER NOT NULL DEFAULT 0,
    accuracy_rate       REAL NOT NULL DEFAULT 0.0,            -- Computed: correct/total
    current_streak      INTEGER NOT NULL DEFAULT 0,           -- Consecutive days active
    longest_streak      INTEGER NOT NULL DEFAULT 0,
    total_points        INTEGER NOT NULL DEFAULT 0,
    total_sessions      INTEGER NOT NULL DEFAULT 0,
    total_time_spent    INTEGER NOT NULL DEFAULT 0,           -- Seconds

    -- Current State
    current_topic_id    UUID REFERENCES topics(id),
    last_session_at     TIMESTAMPTZ,
    placement_complete  BOOLEAN NOT NULL DEFAULT FALSE,

    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_students_user ON students(user_id);
CREATE INDEX idx_students_parent ON students(parent_id);
CREATE INDEX idx_students_grade ON students(grade);
CREATE INDEX idx_students_language ON students(preferred_language);
```

### 2.4 sessions
Individual tutoring or practice sessions.

```sql
CREATE TABLE sessions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id      UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    session_type    VARCHAR(20) NOT NULL DEFAULT 'tutoring',  -- 'tutoring', 'practice', 'assessment', 'placement'
    language        VARCHAR(5) NOT NULL DEFAULT 'en',
    topic_id        UUID REFERENCES topics(id),

    -- Session Metrics
    questions_asked     INTEGER NOT NULL DEFAULT 0,
    questions_correct   INTEGER NOT NULL DEFAULT 0,
    hints_used          INTEGER NOT NULL DEFAULT 0,
    duration_seconds    INTEGER,                                -- Set on session end

    -- Session State
    status          VARCHAR(20) NOT NULL DEFAULT 'active',     -- 'active', 'completed', 'abandoned'
    started_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at        TIMESTAMPTZ,

    -- Mood/Engagement (optional)
    mood_score      REAL,                                       -- 0-1 sentiment analysis

    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_sessions_student ON sessions(student_id);
CREATE INDEX idx_sessions_status ON sessions(status);
CREATE INDEX idx_sessions_started ON sessions(started_at);
CREATE INDEX idx_sessions_type ON sessions(session_type);
```

### 2.5 messages
Individual messages within a tutoring session.

```sql
CREATE TABLE messages (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id      UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    role            VARCHAR(20) NOT NULL,                      -- 'student', 'teacher', 'system'
    content         TEXT NOT NULL,
    content_type    VARCHAR(20) NOT NULL DEFAULT 'text',       -- 'text', 'hint', 'solution', 'feedback', 'encouragement'
    language        VARCHAR(5) NOT NULL DEFAULT 'en',
    hint_level      INTEGER,                                    -- 1, 2, 3 (3 = final hint before solution)
    is_correct      BOOLEAN,                                    -- Only for student answers
    math_expression TEXT,                                       -- Extracted LaTeX if applicable
    tokens_used     INTEGER,                                    -- LLM token count
    model_used      VARCHAR(50),                                -- Which LLM model generated this
    latency_ms      INTEGER,                                    -- Response time

    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_messages_session ON messages(session_id);
CREATE INDEX idx_messages_role ON messages(role);
CREATE INDEX idx_messages_type ON messages(content_type);
```

### 2.6 assessments
Per-question evaluation records — the core feedback loop.

```sql
CREATE TABLE assessments (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id      UUID UNIQUE NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    student_id      UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    topic_id        UUID REFERENCES topics(id),

    -- The Question
    question_text   TEXT NOT NULL,
    question_latex  TEXT,                                       -- LaTeX source

    -- Student Answer
    student_answer  TEXT NOT NULL,
    student_answer_latex TEXT,

    -- Correct Answer
    correct_answer  TEXT NOT NULL,
    correct_answer_latex TEXT,

    -- Evaluation
    is_correct      BOOLEAN NOT NULL,
    confidence      REAL NOT NULL DEFAULT 1.0,                 -- Assessment agent confidence
    sympy_verified  BOOLEAN NOT NULL DEFAULT FALSE,

    -- Misconception Analysis
    error_type      VARCHAR(50),                               -- 'arithmetic', 'conceptual', 'careless', 'order_of_ops', etc.
    misconception   TEXT,                                       -- Description of detected misconception
    prerequisite_topic_id UUID REFERENCES topics(id),          -- Topic student needs to review

    -- Difficulty
    difficulty_level REAL NOT NULL DEFAULT 0.5,                -- 0.0 (easy) to 1.0 (hard)
    time_taken_seconds INTEGER,                                 -- How long student took

    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_assessments_student ON assessments(student_id);
CREATE INDEX idx_assessments_topic ON assessments(topic_id);
CREATE INDEX idx_assessments_correct ON assessments(is_correct);
CREATE INDEX idx_assessments_error_type ON assessments(error_type);
```

### 2.7 topics
Curriculum topics with hierarchical structure.

```sql
CREATE TABLE topics (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_id       UUID REFERENCES topics(id),                 -- NULL for root topics
    name_en         VARCHAR(255) NOT NULL,
    name_hi         VARCHAR(255),
    name_bn         VARCHAR(255),
    description_en  TEXT,
    description_hi  TEXT,
    description_bn  TEXT,
    grade_start     VARCHAR(5) NOT NULL,                        -- Grade where topic is introduced
    grade_end       VARCHAR(5),                                 -- Grade where mastery expected (NULL = ongoing)
    board           VARCHAR(50) DEFAULT 'ncert',
    topic_order     INTEGER NOT NULL DEFAULT 0,                 -- Sequence within grade
    difficulty_base REAL NOT NULL DEFAULT 0.3,                  -- Base difficulty level
    category        VARCHAR(50) NOT NULL,                       -- 'arithmetic', 'algebra', 'geometry', 'trigonometry', 'statistics', 'number_sense', 'measurement', 'data_handling'

    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_topics_parent ON topics(parent_id);
CREATE INDEX idx_topics_grade_start ON topics(grade_start);
CREATE INDEX idx_topics_category ON topics(category);
```

### 2.8 topic_prerequisites
Defines prerequisite relationships between topics.

```sql
CREATE TABLE topic_prerequisites (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    topic_id        UUID NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
    prerequisite_id UUID NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
    importance      VARCHAR(20) NOT NULL DEFAULT 'required',    -- 'required', 'recommended'
    UNIQUE(topic_id, prerequisite_id),
    CHECK(topic_id != prerequisite_id)
);

CREATE INDEX idx_prereq_topic ON topic_prerequisites(topic_id);
CREATE INDEX idx_prereq_prerequisite ON topic_prerequisites(prerequisite_id);
```

### 2.9 student_topic_progress
Per-student, per-topic mastery tracking.

```sql
CREATE TABLE student_topic_progress (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id          UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    topic_id            UUID NOT NULL REFERENCES topics(id) ON DELETE CASCADE,

    -- Mastery Metrics
    mastery_score       REAL NOT NULL DEFAULT 0.0,            -- 0.0 (not started) to 1.0 (mastered)
    questions_attempted INTEGER NOT NULL DEFAULT 0,
    questions_correct   INTEGER NOT NULL DEFAULT 0,
    accuracy_rate       REAL NOT NULL DEFAULT 0.0,            -- Computed
    last_attempted_at   TIMESTAMPTZ,
    mastered_at         TIMESTAMPTZ,                           -- Set when mastery >= 0.85
    times_reviewed      INTEGER NOT NULL DEFAULT 0,

    -- Weakness tracking
    is_weak             BOOLEAN NOT NULL DEFAULT FALSE,       -- Flagged if accuracy < 0.5 over last 5+ attempts
    common_error_type   VARCHAR(50),

    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(student_id, topic_id)
);

CREATE INDEX idx_stp_student ON student_topic_progress(student_id);
CREATE INDEX idx_stp_topic ON student_topic_progress(topic_id);
CREATE INDEX idx_stp_mastery ON student_topic_progress(mastery_score);
CREATE INDEX idx_stp_weak ON student_topic_progress(is_weak) WHERE is_weak = TRUE;
```

### 2.10 practice_sets
Generated practice quizzes.

```sql
CREATE TABLE practice_sets (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id      UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    title           VARCHAR(255) NOT NULL,
    topic_id        UUID REFERENCES topics(id),
    difficulty      VARCHAR(20) NOT NULL DEFAULT 'adaptive',   -- 'easy', 'medium', 'hard', 'adaptive'
    question_count  INTEGER NOT NULL DEFAULT 10,
    status          VARCHAR(20) NOT NULL DEFAULT 'pending',    -- 'pending', 'in_progress', 'completed'
    score           INTEGER,                                    -- Set on completion
    max_score       INTEGER,                                    -- Set on generation
    started_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_practice_sets_student ON practice_sets(student_id);
CREATE INDEX idx_practice_sets_status ON practice_sets(status);
```

### 2.11 practice_questions
Individual questions within a practice set.

```sql
CREATE TABLE practice_questions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    practice_set_id     UUID NOT NULL REFERENCES practice_sets(id) ON DELETE CASCADE,
    question_number     INTEGER NOT NULL,
    question_text       TEXT NOT NULL,
    question_latex      TEXT,
    correct_answer      TEXT NOT NULL,
    correct_answer_latex TEXT,
    solution_steps      JSONB,                                  -- Array of {step_number, explanation, latex}
    difficulty          REAL NOT NULL DEFAULT 0.5,
    hints               JSONB,                                  -- Array of hint strings (3 levels)
    topic_id            UUID REFERENCES topics(id),

    -- Student Response
    student_answer      TEXT,
    student_answer_latex TEXT,
    is_correct          BOOLEAN,
    time_taken_seconds  INTEGER,
    hints_used          INTEGER NOT NULL DEFAULT 0,
    answered_at         TIMESTAMPTZ,

    UNIQUE(practice_set_id, question_number)
);

CREATE INDEX idx_pq_set ON practice_questions(practice_set_id);
CREATE INDEX idx_pq_topic ON practice_questions(topic_id);
```

### 2.12 parent_reports
Auto-generated progress reports for parents.

```sql
CREATE TABLE parent_reports (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id      UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    parent_id       UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    report_type     VARCHAR(20) NOT NULL DEFAULT 'weekly',      -- 'weekly', 'monthly', 'milestone'
    period_start    DATE NOT NULL,
    period_end      DATE NOT NULL,
    report_data     JSONB NOT NULL,                             -- Structured report content
    summary_text    TEXT,                                       -- Natural language summary
    key_strengths   JSONB,                                     -- Top 3 strong topics
    key_weaknesses  JSONB,                                     -- Top 3 weak topics
    recommendations JSONB,                                     -- Suggested actions
    is_read         BOOLEAN NOT NULL DEFAULT FALSE,
    generated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    read_at         TIMESTAMPTZ
);

CREATE INDEX idx_reports_student ON parent_reports(student_id);
CREATE INDEX idx_reports_parent ON parent_reports(parent_id);
CREATE INDEX idx_reports_period ON parent_reports(period_start, period_end);
```

### 2.13 student_achievements
Gamification and milestone tracking.

```sql
CREATE TABLE student_achievements (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id      UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    achievement_type VARCHAR(50) NOT NULL,                      -- 'streak_3', 'streak_7', 'streak_30', 'topic_mastered', 'questions_100', 'accuracy_90', etc.
    title_en        VARCHAR(255) NOT NULL,
    title_hi        VARCHAR(255),
    title_bn        VARCHAR(255),
    description_en  TEXT,
    icon_url        VARCHAR(500),
    earned_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(student_id, achievement_type)
);

CREATE INDEX idx_achievements_student ON student_achievements(student_id);
```

### 2.14 knowledge_documents (for RAG in Qdrant — metadata only in PG)

```sql
CREATE TABLE knowledge_documents (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title           VARCHAR(500) NOT NULL,
    source          VARCHAR(255),                               -- 'ncert_class5', 'icse_class8', etc.
    topic_id        UUID REFERENCES topics(id),
    grade           VARCHAR(5),
    language        VARCHAR(5) NOT NULL,
    content_type    VARCHAR(50) NOT NULL,                       -- 'textbook', 'worksheet', 'example', 'solution'
    chunk_count     INTEGER NOT NULL DEFAULT 0,
    qdrant_collection VARCHAR(100) NOT NULL DEFAULT 'curriculum',
    ingested_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    file_hash       VARCHAR(64)                                 -- SHA-256 for deduplication
);

CREATE INDEX idx_kd_topic ON knowledge_documents(topic_id);
CREATE INDEX idx_kd_grade_lang ON knowledge_documents(grade, language);
```

---

## 3. Key Relationships

```
users (1) ─────< (1) students ─────< (N) sessions ─────< (N) messages ───── (1) assessments
  │                   │                    │
  │                   │<───(N) student_topic_progress ───>(N) topics
  │                   │                    │              │
  │                   │<───(N) practice_sets ──< (N) practice_questions
  │                   │
  │                   │<───(N) student_achievements
  │                   │
  │                   │<───(N) parent_reports
  │
  └──(1:N)── parent_reports (parent_id)
```

---

## 4. Pydantic Schemas (Key Examples)

### StudentDigitalTwin (API Response)
```python
class StudentDigitalTwin(BaseModel):
    id: UUID
    age: int
    grade: str
    preferred_language: str
    learning_speed: float
    confidence_score: float
    accuracy_rate: float
    current_streak: int
    total_points: int
    strengths: list[TopicSummary]
    weaknesses: list[TopicSummary]
    recent_mistakes: list[MistakePattern]
    progress_summary: ProgressSummary

class TopicSummary(BaseModel):
    topic_id: UUID
    name: str
    mastery_score: float
    questions_attempted: int
    accuracy_rate: float

class MistakePattern(BaseModel):
    error_type: str
    topic_name: str
    count: int
    last_occurred: datetime

class ProgressSummary(BaseModel):
    topics_mastered: int
    topics_in_progress: int
    topics_remaining: int
    grade_progress_pct: float
    weekly_activity: list[DailyActivity]
```

### SessionMessage (WebSocket)
```python
class SessionMessage(BaseModel):
    session_id: UUID
    role: Literal["student", "teacher", "system"]
    content: str
    content_type: Literal["text", "hint", "solution", "feedback"]
    hint_level: int | None
    is_correct: bool | None
    math_expression: str | None
```

---

## 5. Migration Strategy (Alembic)

```bash
# Initial migration
alembic revision --autogenerate -m "initial_schema"

# Apply
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## 6. Data Retention & Cleanup

| Data | Retention | Policy |
|------|-----------|--------|
| Active sessions | Indefinite | Core learning record |
| Abandoned sessions | 90 days | Auto-delete |
| Practice sets | Indefinite | Learning history |
| Refresh tokens | 30 days | Auto-revoke |
| Audit logs | 1 year | Compliance |
| Deleted accounts | 30 days grace | Full purge after |

---

## Next: AI Agent Design → [agent-design.md](./agent-design.md)
