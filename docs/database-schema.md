# Database Schema Additions — v2.1 (Revised)

> **Date:** 2026-06-20 | **Version:** 2.1

---

## 1. New Tables (v2.1)

### 1.1 tutor_reports
```sql
CREATE TABLE tutor_reports (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tutor_id        UUID NOT NULL REFERENCES tutors(id) ON DELETE CASCADE,
    student_id      UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    report_type     VARCHAR(20) DEFAULT 'periodic',     -- periodic|milestone|final
    period_start    DATE,
    period_end      DATE,
    performance_summary TEXT,
    strengths       JSONB DEFAULT '[]',
    weak_areas      JSONB DEFAULT '[]',
    study_plan      JSONB DEFAULT '[]',                 -- [{action, topic, frequency}]
    recommendations TEXT,
    is_read         BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_tutor_reports_student ON tutor_reports(student_id);
CREATE INDEX idx_tutor_reports_tutor ON tutor_reports(tutor_id);
```

### 1.2 student_feedback_on_tutors
```sql
CREATE TABLE student_feedback_on_tutors (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id      UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    tutor_id        UUID NOT NULL REFERENCES tutors(id) ON DELETE CASCADE,
    rating          INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    feedback_text   TEXT,
    categories      JSONB DEFAULT '[]',                 -- ['helpful','knowledgeable','patient']
    is_anonymous    BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(student_id, tutor_id, created_at)            -- One feedback per period
);

CREATE INDEX idx_student_feedback_tutor ON student_feedback_on_tutors(tutor_id);
```

### 1.3 notification_types (Seed Data)
```sql
CREATE TABLE notification_types (
    type            VARCHAR(30) PRIMARY KEY,
    category        VARCHAR(20) NOT NULL,               -- action_required|info|alert
    target_role     VARCHAR(20) NOT NULL,               -- tutor|principal|admin|student
    description     TEXT,
    action_url_template VARCHAR(500)
);
```

### 1.4 notifications (Enhanced)
```sql
-- Add to existing notifications table:
ALTER TABLE notifications ADD COLUMN notification_type VARCHAR(30) REFERENCES notification_types(type);
ALTER TABLE notifications ADD COLUMN action_data JSONB;      -- Context for action URL
ALTER TABLE notifications ADD COLUMN expires_at TIMESTAMPTZ;
ALTER TABLE notifications ADD COLUMN priority VARCHAR(10) DEFAULT 'normal';  -- low|normal|high|urgent
```

---

## 2. Modified Tables (v2.1)

### 2.1 tutors — Add audit fields
```sql
ALTER TABLE tutors ADD COLUMN content_approval_count INTEGER DEFAULT 0;
ALTER TABLE tutors ADD COLUMN content_rejection_count INTEGER DEFAULT 0;
ALTER TABLE tutors ADD COLUMN avg_feedback_rating REAL DEFAULT 0.0;
ALTER TABLE tutors ADD COLUMN last_report_generated_at TIMESTAMPTZ;
```

### 2.2 principals — Add oversight metrics
```sql
ALTER TABLE principals ADD COLUMN total_students_overseen INTEGER DEFAULT 0;
ALTER TABLE principals ADD COLUMN total_tutors_overseen INTEGER DEFAULT 0;
ALTER TABLE principals ADD COLUMN escalations_resolved INTEGER DEFAULT 0;
ALTER TABLE principals ADD COLUMN avg_response_time_hours REAL DEFAULT 0;
```

---

## 3. Pydantic Schemas (v2.1 Additions)

```python
class TutorReportRequest(BaseModel):
    student_id: UUID
    period_start: date | None
    period_end: date | None
    performance_summary: str
    strengths: list[str]
    weak_areas: list[str]
    study_plan: list[StudyPlanItem]
    recommendations: str | None

class StudentFeedbackRequest(BaseModel):
    tutor_id: UUID
    rating: int = Field(ge=1, le=5)
    feedback_text: str | None
    categories: list[str] = []
    is_anonymous: bool = False

class NotificationResponse(BaseModel):
    id: UUID
    type: str
    title: str
    message: str | None
    priority: str
    is_read: bool
    action_url: str | None
    created_at: datetime

class TutorDashboardResponse(BaseModel):
    assigned_students: list[StudentSummary]
    pending_actions: list[NotificationResponse]
    analytics: TutorAnalytics
    feedback_summary: FeedbackSummary
```

---

## Next: API Specification → [api-specification.md](./api-specification.md)
