# Database Schema — VidyaMitra v2.0

> **Date:** 2026-06-19 | **Version:** 2.0 | **Database:** PostgreSQL 16

---

## 1. New Tables (v2.0)

### 1.1 tutors
```sql
CREATE TABLE tutors (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subjects        JSONB NOT NULL DEFAULT '[]',        -- [{subject, grade_start, grade_end}]
    experience_yrs  INTEGER NOT NULL DEFAULT 0,
    bio             TEXT,
    verification_status VARCHAR(20) DEFAULT 'pending',  -- pending|verified|rejected
    verified_by     UUID REFERENCES users(id),
    verified_at     TIMESTAMPTZ,
    is_active       BOOLEAN DEFAULT FALSE,
    rating          REAL DEFAULT 0.0,
    total_students  INTEGER DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### 1.2 tutor_documents
```sql
CREATE TABLE tutor_documents (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tutor_id        UUID NOT NULL REFERENCES tutors(id) ON DELETE CASCADE,
    doc_type        VARCHAR(50) NOT NULL,               -- degree|certificate|id_proof|experience
    file_url        VARCHAR(500) NOT NULL,
    ocr_text        TEXT,
    ai_verified     BOOLEAN DEFAULT FALSE,
    ai_confidence   REAL DEFAULT 0.0,
    ai_notes        TEXT,
    uploaded_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### 1.3 principals
```sql
CREATE TABLE principals (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    institution     VARCHAR(255),
    jurisdiction    JSONB DEFAULT '{}',                  -- {grades, subjects, regions}
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### 1.4 curriculum_nodes
```sql
CREATE TABLE curriculum_nodes (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_id       UUID REFERENCES curriculum_nodes(id),
    node_type       VARCHAR(20) NOT NULL,               -- subject|chapter|topic
    name_en         VARCHAR(255) NOT NULL,
    name_hi         VARCHAR(255),
    name_bn         VARCHAR(255),
    name_ta         VARCHAR(255),
    grade_start     VARCHAR(5) NOT NULL,
    grade_end       VARCHAR(5),
    board           VARCHAR(50) DEFAULT 'ncert',
    sort_order      INTEGER DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### 1.5 content_lessons
```sql
CREATE TABLE content_lessons (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    curriculum_node_id UUID REFERENCES curriculum_nodes(id),
    title           VARCHAR(500) NOT NULL,
    content_text    TEXT,
    content_json    JSONB,                               -- Structured lesson data
    language        VARCHAR(5) NOT NULL DEFAULT 'en',
    region          VARCHAR(50),                         -- kolkata|chennai|delhi|rural
    culture_context VARCHAR(50),
    video_url       VARCHAR(500),
    audio_url       VARCHAR(500),
    source_pdf_id   UUID,                                -- Original PDF reference
    status          VARCHAR(20) DEFAULT 'draft',         -- draft|review|published|rejected
    created_by      VARCHAR(20) DEFAULT 'ai',            -- ai|tutor_id
    reviewed_by     UUID REFERENCES tutors(id),
    reviewed_at     TIMESTAMPTZ,
    published_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### 1.6 content_reviews
```sql
CREATE TABLE content_reviews (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lesson_id       UUID NOT NULL REFERENCES content_lessons(id) ON DELETE CASCADE,
    tutor_id        UUID NOT NULL REFERENCES tutors(id),
    action          VARCHAR(20) NOT NULL,                -- approved|rejected|modified
    feedback        TEXT,
    accuracy_score  REAL,                                -- 0-1
    completeness_score REAL,
    alignment_score REAL,
    reviewed_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### 1.7 approval_workflows
```sql
CREATE TABLE approval_workflows (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_type   VARCHAR(30) NOT NULL,                -- tutor_approval|content_approval|escalation
    target_id       UUID NOT NULL,                       -- tutor_id or lesson_id
    current_step    VARCHAR(30) NOT NULL,                -- ai_verification|principal_review|admin_approval
    status          VARCHAR(20) DEFAULT 'pending',       -- pending|approved|rejected
    steps_history   JSONB DEFAULT '[]',                  -- [{step, actor_id, action, timestamp}]
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at    TIMESTAMPTZ
);
```

### 1.8 notifications
```sql
CREATE TABLE notifications (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type            VARCHAR(30) NOT NULL,                -- tutor_request|content_alert|escalation|system
    title           VARCHAR(255) NOT NULL,
    message         TEXT,
    is_read         BOOLEAN DEFAULT FALSE,
    action_url      VARCHAR(500),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### 1.9 source_documents (PDF uploads)
```sql
CREATE TABLE source_documents (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title           VARCHAR(500) NOT NULL,
    file_url        VARCHAR(500) NOT NULL,
    file_type       VARCHAR(20) DEFAULT 'pdf',
    uploaded_by     UUID NOT NULL REFERENCES users(id),
    subject         VARCHAR(100),
    grade           VARCHAR(5),
    language        VARCHAR(5),
    extraction_status VARCHAR(20) DEFAULT 'pending',    -- pending|processing|completed|failed
    extracted_text  TEXT,
    chunk_count     INTEGER DEFAULT 0,
    embedding_model VARCHAR(50) DEFAULT 'text-embedding-3-small',
    uploaded_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

## 2. Modified Tables (v1.0 → v2.0)

### 2.1 users — Add role expansion
```sql
ALTER TABLE users ADD COLUMN phone VARCHAR(20);
ALTER TABLE users ADD COLUMN country VARCHAR(50);
ALTER TABLE users ADD COLUMN state VARCHAR(50);
ALTER TABLE users ADD COLUMN district VARCHAR(50);
ALTER TABLE users ADD COLUMN address TEXT;
-- Role: 'student' | 'tutor' | 'principal' | 'admin'
```

### 2.2 students — Add learning preferences
```sql
ALTER TABLE students ADD COLUMN gender VARCHAR(10);
ALTER TABLE students ADD COLUMN school VARCHAR(255);
ALTER TABLE students ADD COLUMN country VARCHAR(50);
ALTER TABLE students ADD COLUMN state VARCHAR(50);
ALTER TABLE students ADD COLUMN district VARCHAR(50);
ALTER TABLE students ADD COLUMN address TEXT;
ALTER TABLE students ADD COLUMN learning_style VARCHAR(30);    -- visual|auditory|reading|kinesthetic
ALTER TABLE students ADD COLUMN interests JSONB DEFAULT '[]'; -- ['sports','music','animals']
ALTER TABLE students ADD COLUMN matched_tutor_id UUID REFERENCES tutors(id);
```

### 2.3 assessments — Add subjective support
```sql
ALTER TABLE assessments ADD COLUMN assessment_type VARCHAR(20) DEFAULT 'objective'; -- objective|subjective|mixed
ALTER TABLE assessments ADD COLUMN image_url VARCHAR(500);      -- Uploaded handwritten answer
ALTER TABLE assessments ADD COLUMN ocr_text TEXT;               -- Extracted text from image
ALTER TABLE assessments ADD COLUMN diagram_analysis JSONB;      -- AI diagram evaluation
ALTER TABLE assessments ADD COLUMN tutor_feedback TEXT;         -- Tutor's additional feedback
ALTER TABLE assessments ADD COLUMN tutor_id UUID REFERENCES tutors(id);
ALTER TABLE assessments ADD COLUMN ai_feedback TEXT;            -- AI-generated feedback
```

---

## 3. Entity Relationships (v2.0)

```
users (1) ────< students
users (1) ────< tutors
users (1) ────< principals
tutors (1) ──< content_reviews
tutors (1) ──< content_lessons (reviewed_by)
curriculum_nodes (1) ──< content_lessons
source_documents (1) ──< content_lessons (source_pdf_id)
content_lessons (1) ──< content_reviews
approval_workflows → tutors | content_lessons (polymorphic)
students (1) ──< assessments
tutors (1) ──< assessments (tutor feedback)
```

---

## 4. Pydantic Schemas (Key v2.0 Additions)

```python
class TutorRegistrationRequest(BaseModel):
    user_id: UUID
    subjects: list[SubjectInfo]        # [{name, grade_start, grade_end}]
    experience_yrs: int
    bio: str | None
    documents: list[DocumentUpload]    # [{type, file}]

class ContentLessonResponse(BaseModel):
    id: UUID
    title: str
    content_text: str | None
    language: str
    region: str | None
    video_url: str | None
    audio_url: str | None
    status: str
    personalization: PersonalizationMeta | None

class AssessmentSubmission(BaseModel):
    assessment_id: UUID
    answers: list[Answer]              # [{question_id, answer_text, image_url}]

class ApprovalWorkflowResponse(BaseModel):
    id: UUID
    workflow_type: str
    current_step: str
    status: str
    steps_history: list[WorkflowStep]
```

---

## Next: Implementation Roadmap → [implementation-roadmap.md](./implementation-roadmap.md)
