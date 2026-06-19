# API Specification — GanitMitra Math Tutor

> **Date:** 2026-06-19
> **Version:** 1.0
> **Base URL:** `/api/v1`
> **Protocol:** REST + WebSocket
> **Format:** JSON

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
| **Authentication** | Bearer JWT in `Authorization` header |
| **Language Header** | `Accept-Language: en/hi/bn` |

---

## 2. Authentication

### 2.1 Sign Up

```
POST /api/v1/auth/signup
Content-Type: application/json

Request:
{
  "email": "student@example.com",
  "password": "SecurePass123!",
  "full_name": "Riya Sharma",
  "role": "student"               // "student" | "parent"
}

Response (201):
{
  "id": "uuid",
  "email": "student@example.com",
  "full_name": "Riya Sharma",
  "role": "student",
  "is_verified": false,
  "created_at": "2026-06-19T10:00:00Z"
}
```

### 2.2 Login

```
POST /api/v1/auth/login
Content-Type: application/json

Request:
{
  "email": "student@example.com",
  "password": "SecurePass123!"
}

Response (200):
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "uuid",
    "email": "student@example.com",
    "full_name": "Riya Sharma",
    "role": "student"
  }
}
```

### 2.3 Google OAuth

```
POST /api/v1/auth/google

Request:
{
  "id_token": "google-oauth-id-token",
  "role": "student"
}

Response (200):
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "is_new_user": false,
  "user": { ... }
}
```

### 2.4 Refresh Token

```
POST /api/v1/auth/refresh

Request:
{
  "refresh_token": "eyJ..."
}

Response (200):
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "expires_in": 3600
}
```

### 2.5 Logout

```
POST /api/v1/auth/logout
Authorization: Bearer <access_token>

Request:
{
  "refresh_token": "eyJ..."
}

Response (204): No Content
```

---

## 3. Students

### 3.1 Create Student Profile

```
POST /api/v1/students
Authorization: Bearer <token>

Request:
{
  "age": 8,
  "grade": "3",
  "preferred_language": "hi",
  "board": "ncert"
}

Response (201):
{
  "id": "uuid",
  "user_id": "uuid",
  "age": 8,
  "grade": "3",
  "preferred_language": "hi",
  "board": "ncert",
  "learning_speed": 5.0,
  "confidence_score": 0.5,
  "placement_complete": false,
  "created_at": "2026-06-19T10:00:00Z"
}
```

### 3.2 Get Student Profile (Digital Twin)

```
GET /api/v1/students/{student_id}
Authorization: Bearer <token>

Response (200):
{
  "id": "uuid",
  "user_id": "uuid",
  "parent_id": null,
  "age": 8,
  "grade": "3",
  "preferred_language": "hi",
  "board": "ncert",
  "learning_speed": 5.5,
  "confidence_score": 0.72,
  "accuracy_rate": 0.78,
  "current_streak": 5,
  "longest_streak": 12,
  "total_points": 1250,
  "total_sessions": 34,
  "total_time_spent": 20400,
  "total_questions": 342,
  "correct_answers": 267,
  "current_topic": {
    "id": "uuid",
    "name": "Multiplication Tables (6-9)",
    "mastery_score": 0.65
  },
  "strengths": [
    {"topic_id": "uuid", "name": "Addition (3-digit)", "mastery_score": 0.95},
    {"topic_id": "uuid", "name": "Subtraction (2-digit)", "mastery_score": 0.92}
  ],
  "weaknesses": [
    {"topic_id": "uuid", "name": "Multiplication Tables (6-9)", "mastery_score": 0.45},
    {"topic_id": "uuid", "name": "Division (Basic)", "mastery_score": 0.38}
  ],
  "progress_summary": {
    "topics_mastered": 12,
    "topics_in_progress": 5,
    "topics_remaining": 28,
    "grade_progress_pct": 0.35
  },
  "placement_complete": true,
  "last_session_at": "2026-06-19T09:30:00Z"
}
```

### 3.3 Update Student Profile

```
PATCH /api/v1/students/{student_id}
Authorization: Bearer <token>

Request:
{
  "preferred_language": "bn",
  "board": "wb_board"
}

Response (200): { ... updated profile ... }
```

### 3.4 Take Placement Assessment

```
POST /api/v1/students/{student_id}/placement
Authorization: Bearer <token>

Response (201):
{
  "session_id": "uuid",
  "questions": [
    {
      "question_number": 1,
      "question_text": "What is 24 + 37?",
      "question_latex": "24 + 37",
      "difficulty": 0.3,
      "hints": ["Think about adding the ones place first.", "7 + 4 = 11, carry the 1"]
    }
    // ... 5 questions at increasing difficulty
  ]
}
```

### 3.5 Link Parent to Student

```
POST /api/v1/students/{student_id}/link-parent
Authorization: Bearer <parent_token>

Request:
{
  "parent_email": "parent@example.com",
  "relationship": "mother"
}

Response (200): { "linked": true }
```

---

## 4. Tutoring Sessions

### 4.1 Start Tutoring Session

```
POST /api/v1/sessions
Authorization: Bearer <token>

Request:
{
  "session_type": "tutoring",    // "tutoring" | "practice" | "assessment"
  "language": "hi",
  "topic_id": "uuid"              // Optional: start with specific topic
}

Response (201):
{
  "id": "uuid",
  "student_id": "uuid",
  "session_type": "tutoring",
  "language": "hi",
  "status": "active",
  "started_at": "2026-06-19T10:00:00Z",
  "ws_endpoint": "wss://api.ganitmitra.com/ws/sessions/{session_id}?token={jwt}"
}
```

### 4.2 WebSocket Protocol (Tutoring)

```
Connect: wss://api.ganitmitra.com/ws/sessions/{session_id}?token={jwt}

## Student → Server Messages

// Send question or answer
{
  "type": "message",
  "content": "12 × 5 kitna hota hai?",
  "content_type": "text"
}

// Request next hint
{
  "type": "hint_request"
}

// Request full solution
{
  "type": "solution_request"
}

// Change language mid-session
{
  "type": "language_change",
  "language": "bn"
}

// End session
{
  "type": "end_session"
}


## Server → Student Messages

// Hint response
{
  "type": "hint",
  "content": "Socho: 12 × 5 ka matlab 12 ko 5 baar jodna. Pehle 12 × 10 karo, phir aadha.",
  "hint_level": 1,
  "timestamp": "2026-06-19T10:00:05Z"
}

// Feedback on answer
{
  "type": "feedback",
  "is_correct": true,
  "content": "Bilkul sahi! ⭐ 12 × 5 = 60. Bahut achhe!",
  "points_earned": 10,
  "timestamp": "2026-06-19T10:00:10Z"
}

// Step-by-step solution
{
  "type": "solution",
  "steps": [
    {"step": 1, "text": "12 × 5 ka matlab hai 12 + 12 + 12 + 12 + 12", "latex": null},
    {"step": 2, "text": "12 + 12 = 24", "latex": "12 + 12 = 24"},
    {"step": 3, "text": "24 + 12 = 36", "latex": "24 + 12 = 36"},
    {"step": 4, "text": "36 + 12 = 48", "latex": "36 + 12 = 48"},
    {"step": 5, "text": "48 + 12 = 60", "latex": "48 + 12 = 60"},
    {"step": 6, "text": "Isliye, 12 × 5 = 60", "latex": "12 \\times 5 = 60"}
  ],
  "timestamp": "2026-06-19T10:00:15Z"
}

// Motivation message
{
  "type": "motivation",
  "content": "Tumne aaj 5 sawal sahi kiye! 🔥 Lagatar 5 din ki streak!",
  "achievement": "streak_5",
  "timestamp": "2026-06-19T10:00:20Z"
}

// Session summary
{
  "type": "session_summary",
  "data": {
    "questions_asked": 8,
    "questions_correct": 6,
    "hints_used": 3,
    "duration_seconds": 900,
    "topics_covered": ["Multiplication Tables"],
    "points_earned": 45
  },
  "timestamp": "2026-06-19T10:15:00Z"
}

// Error
{
  "type": "error",
  "code": "RATE_LIMITED",
  "message": "Thoda ruko, bahut tez ja rahe ho! 5 second mein phir se puchho."
}
```

### 4.3 Get Session History

```
GET /api/v1/sessions?student_id={uuid}&status=completed&limit=20&cursor={cursor}
Authorization: Bearer <token>

Response (200):
{
  "data": [
    {
      "id": "uuid",
      "session_type": "tutoring",
      "language": "hi",
      "topic": {"id": "uuid", "name": "Multiplication Tables"},
      "questions_asked": 8,
      "questions_correct": 6,
      "duration_seconds": 900,
      "started_at": "2026-06-19T09:00:00Z",
      "ended_at": "2026-06-19T09:15:00Z"
    }
  ],
  "pagination": {
    "next_cursor": "base64_encoded_cursor",
    "has_more": true
  }
}
```

### 4.4 Get Session Messages

```
GET /api/v1/sessions/{session_id}/messages?limit=50
Authorization: Bearer <token>

Response (200):
{
  "data": [
    {
      "id": "uuid",
      "role": "student",
      "content": "12 × 5 kitna hota hai?",
      "content_type": "text",
      "created_at": "2026-06-19T09:00:05Z"
    },
    {
      "id": "uuid",
      "role": "teacher",
      "content": "Socho: 12 × 5 ka matlab...",
      "content_type": "hint",
      "hint_level": 1,
      "created_at": "2026-06-19T09:00:07Z"
    }
  ],
  "pagination": { ... }
}
```

---

## 5. Practice (Quizzes)

### 5.1 Generate Practice Set

```
POST /api/v1/practice/generate
Authorization: Bearer <token>

Request:
{
  "topic_id": "uuid",           // Optional: specific topic
  "difficulty": "adaptive",     // "easy" | "medium" | "hard" | "adaptive"
  "question_count": 10,
  "language": "hi"
}

Response (201):
{
  "id": "uuid",
  "title": "Multiplication Practice",
  "topic": {"id": "uuid", "name": "Multiplication Tables"},
  "difficulty": "adaptive",
  "question_count": 10,
  "questions": [
    {
      "question_number": 1,
      "question_text": "5 × 7 = ?",
      "question_latex": "5 \\times 7",
      "difficulty": 0.3,
      "hints": [
        "5 × 7 ka matlab 5 ko 7 baar jodna",
        "5, 10, 15, 20... ginati karo 7 tak"
      ]
    }
    // ... more questions
  ],
  "status": "pending"
}
```

### 5.2 Submit Practice Answer

```
POST /api/v1/practice/{practice_set_id}/questions/{question_number}/answer
Authorization: Bearer <token>

Request:
{
  "answer": "35",
  "time_taken_seconds": 45,
  "hints_used": 0
}

Response (200):
{
  "is_correct": true,
  "correct_answer": "35",
  "solution": {
    "steps": [
      {"step": 1, "text": "5 × 7 = 5 + 5 + 5 + 5 + 5 + 5 + 5", "latex": null},
      {"step": 2, "text": "5 + 5 + 5 + 5 + 5 + 5 + 5 = 35", "latex": null},
      {"step": 3, "text": "5 × 7 = 35", "latex": "5 \\times 7 = 35"}
    ]
  },
  "points_earned": 10,
  "new_streak": 6
}
```

### 5.3 Complete Practice Set

```
POST /api/v1/practice/{practice_set_id}/complete
Authorization: Bearer <token>

Response (200):
{
  "id": "uuid",
  "score": 8,
  "max_score": 10,
  "accuracy": 0.80,
  "time_taken_total": 420,
  "topics_updated": [
    {"topic_id": "uuid", "name": "Multiplication Tables", "new_mastery": 0.72}
  ],
  "points_earned": 80,
  "achievement_unlocked": null
}
```

---

## 6. Progress & Analytics

### 6.1 Get Student Progress

```
GET /api/v1/progress/{student_id}
Authorization: Bearer <token>

Response (200):
{
  "student_id": "uuid",
  "grade": "3",
  "grade_progress_pct": 0.35,
  "topics_by_category": {
    "arithmetic": {
      "mastered": 8,
      "in_progress": 3,
      "not_started": 10,
      "avg_mastery": 0.62
    },
    "number_sense": {
      "mastered": 4,
      "in_progress": 1,
      "not_started": 5,
      "avg_mastery": 0.78
    }
  },
  "learning_velocity": 2.5,           // Topics mastered per week
  "weekly_activity": [
    {"date": "2026-06-13", "questions": 24, "accuracy": 0.75, "time_spent": 1800},
    {"date": "2026-06-14", "questions": 18, "accuracy": 0.83, "time_spent": 1200}
  ],
  "weak_areas": [
    {
      "topic_id": "uuid",
      "name": "Division (Basic)",
      "mastery_score": 0.38,
      "questions_attempted": 15,
      "accuracy": 0.40,
      "common_error": "Reversing dividend and divisor"
    }
  ],
  "strong_areas": [ ... ],
  "confidence_trend": [0.5, 0.55, 0.58, 0.62, 0.68, 0.72],
  "updated_at": "2026-06-19T10:00:00Z"
}
```

### 6.2 Get Topic Details

```
GET /api/v1/progress/{student_id}/topics/{topic_id}
Authorization: Bearer <token>

Response (200):
{
  "topic_id": "uuid",
  "name": "Multiplication Tables (6-9)",
  "category": "arithmetic",
  "grade_introduced": "3",
  "mastery_score": 0.45,
  "questions_attempted": 28,
  "questions_correct": 13,
  "accuracy_rate": 0.46,
  "recent_accuracy": 0.55,        // Last 10 questions
  "time_spent_minutes": 95,
  "last_attempted": "2026-06-19T09:30:00Z",
  "is_weak": true,
  "common_errors": [
    {"type": "arithmetic", "count": 8, "example": "6×7=41 instead of 42"},
    {"type": "careless", "count": 4, "example": "Skipped 8× table"}
  ],
  "prerequisites": [
    {"topic_id": "uuid", "name": "Multiplication Concepts", "mastery": 0.85},
    {"topic_id": "uuid", "name": "Multiplication Tables (1-5)", "mastery": 0.78}
  ],
  "recommended_actions": [
    "Practice 6× and 7× tables specifically",
    "Try skip-counting by 6, 7, 8, and 9"
  ]
}
```

---

## 7. Topics & Curriculum

### 7.1 Get Topic Tree

```
GET /api/v1/topics?grade=3&board=ncert&language=hi
Authorization: Bearer <token>

Response (200):
{
  "grade": "3",
  "board": "ncert",
  "categories": [
    {
      "category": "arithmetic",
      "name_hi": "अंकगणित",
      "topics": [
        {
          "id": "uuid",
          "name_hi": "जोड़ (3-अंकीय)",
          "name_en": "Addition (3-digit)",
          "mastery_score": 0.85,     // Only if student_id provided
          "is_mastered": true
        }
      ]
    }
  ]
}
```

### 7.2 Get Recommended Next Topic

```
GET /api/v1/topics/next/{student_id}
Authorization: Bearer <token>

Response (200):
{
  "recommended_topic": {
    "id": "uuid",
    "name": "Multiplication Tables (6-9)",
    "reason": "You've mastered tables 1-5. Ready for the next set! Also, this is your weakest active topic."
  },
  "alternatives": [
    {
      "id": "uuid",
      "name": "Division (Basic)",
      "reason": "A prerequisite for upcoming Grade 4 topics. Currently weak."
    }
  ]
}
```

---

## 8. Parent Reports

### 8.1 Generate/Get Report

```
GET /api/v1/reports/{student_id}?type=weekly&period_start=2026-06-12&period_end=2026-06-19
Authorization: Bearer <parent_token>

Response (200):
{
  "id": "uuid",
  "student_id": "uuid",
  "report_type": "weekly",
  "period_start": "2026-06-12",
  "period_end": "2026-06-19",
  "summary_text": "Riya had a great week! She attempted 85 questions with 78% accuracy...",
  "key_strengths": [
    {"topic": "Addition (3-digit)", "mastery": 0.95, "trend": "improving"}
  ],
  "key_weaknesses": [
    {"topic": "Division (Basic)", "mastery": 0.38, "trend": "needs_attention"}
  ],
  "recommendations": [
    {"action": "Practice division for 15 minutes daily", "topic": "Division (Basic)"},
    {"action": "Use real-life examples: sharing sweets, dividing toys", "topic": "Division (Basic)"}
  ],
  "stats": {
    "sessions_this_week": 5,
    "questions_attempted": 85,
    "accuracy": 0.78,
    "time_spent_minutes": 145,
    "topics_practiced": ["Addition", "Subtraction", "Multiplication", "Division"],
    "topics_mastered_this_week": 1,
    "streak_days": 5,
    "grade_progress": 0.35,
    "comparison_to_previous": {
      "accuracy_change": 0.03,
      "time_change_pct": 0.12
    }
  },
  "is_read": false,
  "generated_at": "2026-06-19T10:00:00Z"
}
```

### 8.2 Mark Report as Read

```
POST /api/v1/reports/{report_id}/read
Authorization: Bearer <parent_token>

Response (204): No Content
```

### 8.3 List All Reports

```
GET /api/v1/reports/{student_id}?limit=10
Authorization: Bearer <parent_token>

Response (200):
{
  "data": [
    {
      "id": "uuid",
      "report_type": "weekly",
      "period_start": "2026-06-12",
      "period_end": "2026-06-19",
      "summary_snippet": "Great week! 78% accuracy...",
      "is_read": false,
      "generated_at": "2026-06-19T10:00:00Z"
    }
  ]
}
```

---

## 9. Voice

### 9.1 Speech-to-Text

```
POST /api/v1/voice/stt
Authorization: Bearer <token>
Content-Type: multipart/form-data

Form Data:
  audio: <audio_file.webm>
  language: "hi"             // Optional hint

Response (200):
{
  "text": "12 गुना 5 कितना होता है?",
  "language_detected": "hi",
  "confidence": 0.95,
  "duration_seconds": 3.2
}
```

### 9.2 Text-to-Speech

```
POST /api/v1/voice/tts
Authorization: Bearer <token>

Request:
{
  "text": "12 × 5 = 60. बहुत अच्छे!",
  "language": "hi",
  "voice_style": "gentle"   // "natural" | "gentle" | "excited"
}

Response (200): audio/mpeg binary
```

---

## 10. Achievements

### 10.1 Get Student Achievements

```
GET /api/v1/students/{student_id}/achievements
Authorization: Bearer <token>

Response (200):
{
  "achievements": [
    {
      "type": "streak_7",
      "title": "7-Day Streak! 🔥",
      "description": "You've been learning for 7 days in a row!",
      "earned_at": "2026-06-18T10:00:00Z"
    },
    {
      "type": "questions_100",
      "title": "Century! 💯",
      "description": "You've solved 100 questions!",
      "earned_at": "2026-06-15T14:30:00Z"
    }
  ],
  "next_achievements": [
    {
      "type": "topic_master_5",
      "title": "Master of 5",
      "progress": {"current": 3, "target": 5}
    }
  ]
}
```

---

## 11. Health & Admin

### 11.1 Health Check

```
GET /api/v1/health

Response (200):
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "database": "up",
    "redis": "up",
    "qdrant": "up",
    "openai": "up",
    "deepseek": "up"
  },
  "timestamp": "2026-06-19T10:00:00Z"
}
```

### 11.2 Metrics (Prometheus)

```
GET /metrics
# Prometheus text format
```

---

## 12. Error Responses

### 12.1 Standard Error Format (RFC 7807)

```json
{
  "type": "https://api.ganitmitra.com/errors/validation-error",
  "title": "Validation Error",
  "status": 422,
  "detail": "Grade must be between N and 10",
  "instance": "/api/v1/students",
  "errors": [
    {
      "field": "grade",
      "message": "Value '15' is not valid. Expected: N, KG, 1-10"
    }
  ]
}
```

### 12.2 HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 204 | No Content |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden (wrong role) |
| 404 | Not Found |
| 409 | Conflict (duplicate) |
| 422 | Validation Error |
| 429 | Rate Limited |
| 500 | Internal Server Error |
| 503 | Service Unavailable |

---

## 13. Rate Limiting Headers

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1718791260
Retry-After: 5 (only on 429)
```

---

## Next: UI/UX Design → [ui-wireframes.md](./ui-wireframes.md)
