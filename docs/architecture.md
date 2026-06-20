# System Architecture — AI Student Tutor Platform v2.1

> **Date:** 2026-06-20 | **Version:** 2.1 (Revised) | **Source:** Functional Specification V1

---

## 1. Key Architectural Changes (v2.1)

| Change | Detail |
|--------|--------|
| **Notification Centers** | Every role (Tutor, Principal, Admin) has dedicated notification + approval centers with actionable links |
| **Tutor Analytics per Student** | Interest areas, time spent, learning patterns, knowledge retention per assigned student |
| **Student Feedback on Tutors** | Ratings + written feedback rolled up to Principal Module |
| **Tutor Reports to Students** | Structured reports with performance summary + study plan recommendations |
| **Principal Institution-Wide Visibility** | Sees ALL students and ALL tutors, not just assigned subset |
| **Super Admin Platform-Wide** | Sees everything across all institutions |

---

## 2. Notification & Approval Flow Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    NOTIFICATION CENTERS                           │
│                                                                  │
│  Tutor Notification Center                                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ • Content pending approval (Approve/Reject/Modify)        │   │
│  │ • New student assignments requiring acknowledgment        │   │
│  │ • Subjective answers awaiting evaluation                  │   │
│  │ • Reassignment request status updates                     │   │
│  │ [Each links directly to relevant action screen]           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  Principal Notification & Approval Center                        │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ • Tutor approvals after AI Verification                   │   │
│  │ • Tutor reassignment requests                             │   │
│  │ • Escalations raised by tutors or students                │   │
│  │ • Content/quality flags requiring review                   │   │
│  │ • Low student-feedback alerts on tutor performance        │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  Super Admin Notification & Approval Center                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ • Final-stage tutor approvals (after Principal Review)    │   │
│  │ • Escalations flagged upward by Principals                │   │
│  │ • Platform-wide content alerts                            │   │
│  │ • AI recommendations requiring governance sign-off        │   │
│  │ • Compliance and policy exceptions                        │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Student Feedback Flow

```
Student completes learning session
  │
  ▼
Student submits feedback on Tutor
  (Rating + Written Comments)
  │
  ▼
Feedback stored in student_feedback table
  │
  ▼
Aggregated & displayed on:
  ├── Tutor Dashboard (personal view)
  ├── Principal Dashboard (all tutors' feedback)
  └── Super Admin Dashboard (platform-wide)
```

---

## 4. Tutor Report Flow

```
Tutor creates report for Student
  │  Performance summary
  │  Strengths
  │  Weak areas
  │  Recommended study plan
  ▼
Report sent to Student
  │  Visible on Student Dashboard
  │  Notification triggered
  ▼
Report stored in tutor_reports table
  │  Tracked in analytics
```

---

## 5. Updated Notification Types

| Type | Sent To | Trigger |
|------|---------|---------|
| `content_pending` | Tutor | AI content generated, awaiting review |
| `student_assigned` | Tutor | New student added to roster |
| `subjective_pending` | Tutor | Subjective answer submitted, needs evaluation |
| `reassignment_update` | Tutor | Reassignment request status changed |
| `tutor_approval` | Principal | Tutor passed AI verification, needs review |
| `reassignment_request` | Principal | Tutor requested reassignment |
| `escalation` | Principal | Issue escalated by tutor/student |
| `quality_flag` | Principal | Content or quality concern flagged |
| `low_feedback_alert` | Principal | Tutor received low student ratings |
| `final_approval` | Admin | Tutor approved by Principal, needs final sign-off |
| `escalated_upward` | Admin | Escalation from Principal |
| `content_alert` | Admin | Platform-wide content issue |
| `ai_recommendation` | Admin | AI governance recommendation |
| `compliance_exception` | Admin | Policy exception requiring review |
| `report_ready` | Student | Tutor report available |
| `feedback_response` | Tutor | Student submitted feedback |

---

## Next: Database Schema → [database-schema.md](./database-schema.md)
