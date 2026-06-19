# API Specification — VidyaMitra AI Student Tutor Platform v2.0

> **Date:** 2026-06-19 | **Version:** 2.0  
> **Base URL:** `/api/v1` | **Protocol:** REST + WebSocket | **Format:** JSON

---

## 1. API Design Principles

| Principle | Implementation |
|-----------|---------------|
| **Resource-Oriented** | RESTful endpoints for CRUD resources |
| **WebSocket for Real-Time** | Tutoring sessions use WS for streaming |
| **Versioned** | `/api/v1/` prefix |
| **Consistent Errors** | RFC 7807 Problem Details |
| **Pagination** | Cursor-based for lists |
| **Rate Limiting** | Headers: `X-RateLimit-*` |
| **Authentication** | Bearer JWT in `Authorization` header (4 roles) |
| **Language Header** | `Accept-Language: en/hi/bn/ta` |
| **File Upload** | `multipart/form-data` for PDFs, images, audio |

---

## 2. Authentication (Multi-Role)

### 2.1 Register (Any Role)

```
POST /api/v1/auth/register
Content-Type: application/json

Request:
{
  "email": "user@example.com",
  "password": "***",
  "full_name": "Riya Sharma",
  "role": "student",              // student | tutor | principal
  "phone": "+91-9876543210",
  "country": "IN",
  "state": "West Bengal",
  "district": "Kolkata"
}

Response (201):
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "Riya Sharma",
  "role": "student",
  "is_verified": false,
  "created_at": "2026-06-19T10:00:00Z"
}
```

### 2.2 Login

```
POST /api/v1/auth/login

Request: { "email": "user@example.com", "password": "***" }

Response (200):
{
  "access_token": "***",
  "refresh_token": "***",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "Riya Sharma",
    "role": "student"
  }
}
```

### 2.3 Multi-Role Endpoints

| Endpoint | Roles Allowed |
|----------|--------------|
| `/auth/register` | Public |
| `/auth/login` | Public |
| `/auth/refresh` | Authenticated |
| `/auth/logout` | Authenticated |
| `/auth/me` | Authenticated |
| `/students/*` | Student (own data), Parent, Principal, Admin |
| `/tutors/*` | Tutor (own data), Principal, Admin |
| `/principals/*` | Principal (own data), Admin |
| `/admin/*` | Admin only |
| `/content/*` | Student (read), Tutor (review), Admin (upload) |
| `/assessments/*` | Student (submit/view), Tutor (review), Principal |
| `/analytics/*` | Principal, Admin |

---

## 3. Student Endpoints

### 3.1 Create Student Profile

```
POST /api/v1/students
Authorization: Bearer <token>

Request:
{
  "age": 8,
  "grade": "3",
  "preferred_language": "hi",
  "board": "ncert",
  "gender": "female",
  "school": "DAV Public School",
  "country": "IN",
  "state": "West Bengal",
  "district": "Kolkata",
  "learning_style": "visual",
  "interests": ["sports", "drawing"]
}

Response (201): { ... student digital twin v2 ... }
```

### 3.2 Get Student Digital Twin v2

```
GET /api/v1/students/{student_id}
Authorization: Bearer <token>

Response (200):
{
  "id": "uuid",
  "user_id": "uuid",
  "age": 8,
  "grade": "3",
  "preferred_language": "hi",
  "learning_style": "visual",
  "interests": ["sports", "drawing"],
  "matched_tutor": {
    "id": "uuid",
    "name": "Mrs. Gupta",
    "subjects": ["Mathematics"]
  },
  "learning_speed": 5.5,
  "confidence_score": 0.72,
  "accuracy_rate": 0.78,
  "current_streak": 5,
  "total_points": 1250,
  "strengths": [...],
  "weaknesses": [...],
  "progress_summary": {
    "subjects": {
      "mathematics": { "mastered": 12, "in_progress": 5, "grade_pct": 0.35 },
      "science": { "mastered": 3, "in_progress": 2, "grade_pct": 0.15 }
    }
  }
}
```

### 3.3 Student Dashboard

```
GET /api/v1/students/{student_id}/dashboard
Authorization: Bearer <token>

Response (200):
{
  "learning_metrics": {
    "progress_pct": 35,
    "streak": 5,
    "daily_activity": [...]
  },
  "assessment_metrics": {
    "mock_test_avg": 78,
    "final_test_avg": null,
    "subject_performance": {
      "mathematics": 78,
      "science": 65
    }
  },
  "gamification": {
    "points": 1250,
    "badges": ["streak_7", "questions_100"],
    "rank": 15
  },
  "current_lesson": {
    "subject": "Mathematics",
    "chapter": "Multiplication",
    "topic": "Tables 6-9",
    "progress": 0.65
  }
}
```

---

## 4. Tutor Endpoints

### 4.1 Tutor Registration

```
POST /api/v1/tutors/register
Authorization: Bearer <token>
Content-Type: multipart/form-data

Form Data:
  subjects: [{"subject":"Mathematics","grade_start":"1","grade_end":"8"}]
  experience_yrs: 5
  bio: "Experienced math teacher with 5 years..."
  degree_cert: <file>
  experience_letter: <file>
  id_proof: <file>

Response (201):
{
  "id": "uuid",
  "user_id": "uuid",
  "subjects": [{"subject":"Mathematics","grade_start":"1","grade_end":"8"}],
  "experience_yrs": 5,
  "verification_status": "pending",
  "workflow": {
    "id": "uuid",
    "current_step": "ai_verification",
    "status": "pending"
  }
}
```

### 4.2 Tutor Verification (AI → Principal → Admin)

```
GET /api/v1/tutors/{tutor_id}/verification
Authorization: Bearer <principal_token>

Response (200):
{
  "tutor_id": "uuid",
  "verification_status": "ai_reviewed",
  "ai_report": {
    "document_authenticity": 0.92,
    "consistency_score": 0.88,
    "flags": [],
    "notes": "All documents appear genuine"
  },
  "documents": [
    { "type": "degree", "verified": true, "confidence": 0.95 },
    { "type": "experience", "verified": true, "confidence": 0.90 },
    { "type": "id_proof", "verified": true, "confidence": 0.92 }
  ],
  "workflow": {
    "current_step": "principal_review",
    "next_action": "principal_approval_required"
  }
}

POST /api/v1/tutors/{tutor_id}/approve
Authorization: Bearer <principal_or_admin_token>

Request: { "action": "approve", "notes": "Qualified. Approved." }
Response (200): { "status": "approved", "tutor_activated": true }
```

### 4.3 Tutor Dashboard

```
GET /api/v1/tutors/{tutor_id}/dashboard
Authorization: Bearer <tutor_token>

Response (200):
{
  "assigned_students": 24,
  "active_students": 18,
  "content_reviews_pending": 5,
  "assessments_to_review": 12,
  "student_performance": [
    {
      "student_id": "uuid",
      "name": "Riya",
      "grade": "3",
      "accuracy": 0.78,
      "weak_areas": ["Division"],
      "last_active": "2026-06-19"
    }
  ],
  "analytics": {
    "avg_student_accuracy": 0.72,
    "student_engagement": 0.85,
    "content_approval_rate": 0.92
  }
}
```

### 4.4 Tutor Feedback

```
POST /api/v1/tutors/{tutor_id}/feedback
Authorization: Bearer <tutor_token>

Request:
{
  "student_id": "uuid",
  "assessment_id": "uuid",
  "feedback": "Great improvement in multiplication. Focus on division next.",
  "recommendations": [
    "Practice division tables daily for 15 minutes",
    "Use real-life sharing examples"
  ]
}

Response (201): { "status": "submitted" }
```

### 4.5 Tutor Reassignment

```
POST /api/v1/tutors/{tutor_id}/reassign
Authorization: Bearer <tutor_token>

Request:
{
  "student_id": "uuid",
  "reason": "Student requires Hindi-medium instruction, I teach English only"
}

Response (200): {
  "status": "pending_principal_approval",
  "workflow_id": "uuid"
}
```

---

## 5. Principal Endpoints

### 5.1 Principal Dashboard

```
GET /api/v1/principals/{principal_id}/dashboard
Authorization: Bearer <principal_token>

Response (200):
{
  "institution": "DAV Group of Schools",
  "jurisdiction": { "grades": ["1","2","3","4","5"], "subjects": ["Mathematics"] },
  "student_data": {
    "total": 450,
    "active": 380,
    "avg_progress": 0.42
  },
  "tutor_data": {
    "total": 12,
    "active": 10,
    "pending_approvals": 2
  },
  "platform_analytics": {
    "sessions_this_week": 1240,
    "assessments_completed": 890,
    "avg_engagement_score": 0.76
  },
  "escalations": [
    { "type": "content_dispute", "status": "pending", "created": "2026-06-18" }
  ]
}
```

### 5.2 Monitor Tutors

```
GET /api/v1/principals/{principal_id}/tutors
Authorization: Bearer <principal_token>

Response (200):
{
  "tutors": [
    {
      "id": "uuid",
      "name": "Mrs. Gupta",
      "subjects": ["Mathematics"],
      "students_count": 24,
      "content_approval_rate": 0.92,
      "avg_rating": 4.7,
      "last_active": "2026-06-19",
      "status": "active"
    }
  ]
}
```

### 5.3 Quality Assurance

```
POST /api/v1/principals/{principal_id}/escalations/{escalation_id}/resolve
Authorization: Bearer <principal_token>

Request:
{
  "action": "resolved",
  "resolution": "Content re-assigned to Mrs. Sharma for review",
  "notes": "Original tutor was overloaded"
}

Response (200): { "status": "resolved" }
```

---

## 6. Super Admin Endpoints

### 6.1 Admin Dashboard

```
GET /api/v1/admin/dashboard
Authorization: Bearer <admin_token>

Response (200):
{
  "organization_overview": {
    "total_users": 1500,
    "total_students": 1200,
    "total_tutors": 50,
    "total_principals": 8,
    "new_registrations_today": 23
  },
  "approvals_pending": {
    "tutor_approvals": 3,
    "content_escalations": 1
  },
  "platform_health": {
    "uptime": "99.9%",
    "api_p95_latency_ms": 320,
    "error_rate": "0.02%"
  },
  "notifications": [
    { "type": "tutor_request", "message": "New tutor registration: Mr. Kumar", "time": "2026-06-19T10:00Z" },
    { "type": "escalation", "message": "Content dispute escalated by Principal Sharma", "time": "2026-06-19T09:30Z" }
  ]
}
```

### 6.2 User Management

```
GET /api/v1/admin/users?role=tutor&status=pending&limit=20
Authorization: Bearer <admin_token>

Response (200):
{
  "data": [
    { "id": "uuid", "full_name": "Mr. Kumar", "role": "tutor", "status": "pending_approval", "registered_at": "2026-06-18" }
  ],
  "pagination": { "next_cursor": "...", "has_more": false }
}

PATCH /api/v1/admin/users/{user_id}
Authorization: Bearer <admin_token>

Request: { "is_active": false }
Response (200): { "updated": true }
```

### 6.3 Organization Analytics

```
GET /api/v1/admin/analytics?period=30d
Authorization: Bearer <admin_token>

Response (200):
{
  "user_growth": [
    { "date": "2026-05-20", "students": 950, "tutors": 32 },
    { "date": "2026-06-19", "students": 1200, "tutors": 50 }
  ],
  "engagement_trend": [
    { "week": "W1", "dau": 320, "sessions": 2100 },
    { "week": "W4", "dau": 480, "sessions": 3500 }
  ],
  "content_metrics": {
    "total_lessons": 2500,
    "lessons_published_this_month": 340,
    "avg_tutor_approval_rate": 0.88
  },
  "learning_outcomes": {
    "avg_student_progress": 0.38,
    "subjects": {
      "mathematics": { "avg_progress": 0.42, "students": 1200 },
      "science": { "avg_progress": 0.31, "students": 850 }
    }
  }
}
```

---

## 7. Content Endpoints

### 7.1 Upload Source Document (PDF)

```
POST /api/v1/content/upload
Authorization: Bearer <admin_or_tutor_token>
Content-Type: multipart/form-data

Form Data:
  file: <pdf_file>
  subject: "Mathematics"
  grade: "3"
  language: "en"

Response (201):
{
  "id": "uuid",
  "title": "NCERT Class 3 Mathematics",
  "status": "extraction_pending",
  "file_url": "/files/source/doc_abc.pdf"
}
```

### 7.2 Generate Lessons from PDF

```
POST /api/v1/content/generate/{document_id}
Authorization: Bearer <admin_token>

Response (202):
{
  "task_id": "uuid",
  "status": "processing",
  "message": "Content generation started. This may take 2-5 minutes.",
  "estimated_completion": "2026-06-19T10:05:00Z"
}

GET /api/v1/content/generate/{document_id}/status

Response (200):
{
  "status": "completed",
  "lessons_generated": 12,
  "chapters_created": 4,
  "videos_generated": 0
}
```

### 7.3 Get Content Feed (Student)

```
GET /api/v1/content/lessons?subject=mathematics&grade=3&language=hi
Authorization: Bearer <student_token>

Response (200):
{
  "subject": { "id": "uuid", "name": "Mathematics" },
  "chapters": [
    {
      "id": "uuid",
      "name": "Multiplication",
      "topics": [
        {
          "id": "uuid",
          "name": "Tables 6-9",
          "lesson": {
            "id": "uuid",
            "type": "interactive",
            "content": { "text": "...", "video_url": "...", "audio_url": "..." },
            "language": "hi",
            "region": "kolkata",
            "personalized": true,
            "progress": 0.65
          }
        }
      ]
    }
  ]
}
```

### 7.4 Tutor Content Review

```
GET /api/v1/content/review?status=pending&tutor_id={tutor_id}
Authorization: Bearer <tutor_token>

Response (200):
{
  "pending_reviews": [
    {
      "lesson_id": "uuid",
      "title": "Introduction to Fractions",
      "generated_by": "ai",
      "created_at": "2026-06-19",
      "content_preview": "..."
    }
  ]
}

POST /api/v1/content/review/{lesson_id}
Authorization: Bearer <tutor_token>

Request:
{
  "action": "approved",              // approved | rejected | modified
  "accuracy_score": 0.95,
  "completeness_score": 0.90,
  "alignment_score": 0.92,
  "feedback": "Content is accurate and well-structured. Minor typo fixed.",
  "modifications": { "title": "Introduction to Fractions — Updated" }
}

Response (200):
{
  "status": "published",
  "reviewed_at": "2026-06-19T11:00:00Z"
}
```

---

## 8. Assessment Endpoints (v2.0)

### 8.1 Generate Assessment

```
POST /api/v1/assessments/generate
Authorization: Bearer <student_or_tutor_token>

Request:
{
  "student_id": "uuid",
  "subject": "mathematics",
  "topic_ids": ["uuid1", "uuid2"],
  "assessment_type": "mixed",       // objective | subjective | mixed
  "question_count": 10,
  "difficulty": "adaptive",
  "language": "hi"
}

Response (201):
{
  "id": "uuid",
  "questions": [
    {
      "question_number": 1,
      "type": "mcq",
      "question_text": "6 × 4 कितना होता है?",
      "options": ["20", "24", "28", "30"],
      "difficulty": 0.4
    },
    {
      "question_number": 8,
      "type": "subjective",
      "question_text": "गुणा क्या होता है? उदाहरण देकर समझाओ।",
      "max_marks": 5
    }
  ],
  "total_marks": 25,
  "duration_minutes": 30
}
```

### 8.2 Submit Subjective Answer (Image Upload)

```
POST /api/v1/assessments/{assessment_id}/questions/{question_number}/submit
Authorization: Bearer <student_token>
Content-Type: multipart/form-data

Form Data:
  answer_text: "गुणा का मतलब है..."  (optional)
  answer_image: <image_file>        (handwritten answer + diagrams)

Response (200):
{
  "submitted": true,
  "ocr_status": "processing",
  "estimated_evaluation": "2026-06-19T10:02:00Z"
}
```

### 8.3 Get Assessment Results

```
GET /api/v1/assessments/{assessment_id}/results
Authorization: Bearer <student_or_tutor_token>

Response (200):
{
  "assessment_id": "uuid",
  "score": 18,
  "max_score": 25,
  "percentage": 72,
  "completed_at": "2026-06-19T10:15:00Z",
  "questions": [
    {
      "question_number": 1,
      "type": "mcq",
      "correct": true,
      "ai_score": 1,
      "ai_feedback": "सही! 6 × 4 = 24"
    },
    {
      "question_number": 8,
      "type": "subjective",
      "student_answer": "गुणा का मतलब है बार-बार जोड़ना...",
      "image_url": "/files/answers/img_abc.jpg",
      "ocr_text": "गुणा का मतलब है बार-बार जोड़ना...",
      "ai_score": 3,
      "max_marks": 5,
      "ai_feedback": "Concept is correct but missing an example. Good understanding.",
      "tutor_feedback": "Excellent explanation! Add one more example for full marks. ⭐",
      "tutor_name": "Mrs. Gupta"
    }
  ],
  "weak_areas": ["Division concepts"],
  "recommended_revision": ["Basic Division", "Division with remainders"]
}
```

---

## 9. Voice Endpoints

### 9.1 Speech-to-Text (STT)

```
POST /api/v1/voice/stt
Authorization: Bearer <token>
Content-Type: multipart/form-data

Form Data:
  audio: <audio_file.webm>
  language: "hi"

Response (200):
{
  "text": "12 गुणा 5 कितना होता है?",
  "language_detected": "hi",
  "confidence": 0.95,
  "duration_seconds": 3.2
}
```

### 9.2 Text-to-Speech (TTS)

```
POST /api/v1/voice/tts
Authorization: Bearer <token>

Request:
{
  "text": "12 × 5 = 60. बहुत अच्छे!",
  "language": "hi",
  "voice_style": "gentle",
  "region": "kolkata"           // Regional accent preference
}

Response (200): audio/mpeg binary
```

---

## 10. Analytics Endpoints

### 10.1 Student Analytics

```
GET /api/v1/analytics/student/{student_id}?period=30d
Authorization: Bearer <student_or_tutor_or_principal_token>

Response (200):
{
  "learning_patterns": {
    "preferred_time": "evening",
    "avg_session_duration_min": 18,
    "sessions_per_week": 5,
    "completion_rate": 0.85
  },
  "progress_trend": [
    { "week": "W1", "accuracy": 0.72, "topics_completed": 3 },
    { "week": "W4", "accuracy": 0.80, "topics_completed": 15 }
  ],
  "knowledge_retention": {
    "week_1_retention": 0.88,
    "week_4_retention": 0.76
  },
  "recommendations": [
    "Review Division chapter — retention dropped from 0.85 to 0.62",
    "Consider morning sessions — accuracy is 12% higher"
  ]
}
```

### 10.2 Platform Analytics

```
GET /api/v1/analytics/platform?period=30d
Authorization: Bearer <admin_token>

Response (200):
{
  "usage_trends": { ... },
  "engagement_metrics": { ... },
  "content_performance": { ... },
  "learning_outcomes": { ... }
}
```

---

## 11. Notifications

### 11.1 Get Notifications

```
GET /api/v1/notifications?unread_only=true
Authorization: Bearer <token>

Response (200):
{
  "data": [
    {
      "id": "uuid",
      "type": "tutor_request",
      "title": "New Tutor Registration",
      "message": "Mr. Kumar has registered as a Mathematics tutor",
      "is_read": false,
      "action_url": "/admin/tutors/pending",
      "created_at": "2026-06-19T10:00:00Z"
    }
  ]
}

POST /api/v1/notifications/{notification_id}/read
Response (204): No Content
```

---

## 12. Health & Admin

### 12.1 Health Check

```
GET /api/v1/health

Response (200):
{
  "status": "healthy",
  "version": "2.0.0",
  "services": {
    "database": "up",
    "redis": "up",
    "qdrant": "up",
    "minio": "up",
    "openai": "up",
    "deepseek": "up",
    "ocr": "up"
  }
}
```

---

## 13. WebSocket Protocol (Tutoring)

```
Connect: wss://api.vidyamitra.com/ws/sessions/{session_id}?token=***

## Student → Server

{ "type": "message", "content": "12 × 5 kitna hota hai?" }
{ "type": "hint_request" }
{ "type": "solution_request" }
{ "type": "voice_message", "audio": "<base64>" }
{ "type": "language_change", "language": "bn" }
{ "type": "end_session" }

## Server → Student

{ "type": "hint", "content": "...", "hint_level": 1 }
{ "type": "feedback", "is_correct": true, "content": "...", "points_earned": 10 }
{ "type": "solution", "steps": [...] }
{ "type": "motivation", "content": "...", "achievement": "streak_5" }
{ "type": "session_summary", "data": {...} }
{ "type": "voice_response", "audio": "<base64>" }
{ "type": "error", "code": "RATE_LIMITED", "message": "..." }
```

---

## 14. Error Responses (RFC 7807)

| Code | Meaning | Example Detail |
|------|---------|---------------|
| 200 | Success | — |
| 201 | Created | Resource created |
| 202 | Accepted | Async processing started |
| 204 | No Content | Deleted/Updated |
| 400 | Bad Request | Invalid parameters |
| 401 | Unauthorized | Invalid/missing token |
| 403 | Forbidden | Wrong role for endpoint |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Duplicate resource |
| 422 | Validation Error | Invalid data format |
| 429 | Rate Limited | Too many requests |
| 500 | Internal Error | Server error |
| 503 | Service Unavailable | AI/O CR service down |

---

## 15. Rate Limiting

| Role | Limit | Window |
|------|-------|--------|
| Student | 120 req/min | Per user |
| Tutor | 180 req/min | Per user |
| Principal | 240 req/min | Per user |
| Admin | 300 req/min | Per user |
| Unauthenticated | 60 req/min | Per IP |
| LLM calls (all) | 30 req/min | Per user |

---

## Next: Implementation → [implementation-roadmap.md](./implementation-roadmap.md)
