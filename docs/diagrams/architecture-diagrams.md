# Architecture Diagrams — AI Student Tutor Platform v2.1 (Revised)

> **Date:** 2026-06-19 | **Version:** 2.0 | **Format:** Mermaid (renders on GitHub)

---

## 1. System Architecture (v2.0 — Multi-Role)

```mermaid
graph TB
    subgraph Client["CLIENT LAYER — 4 Portals"]
        StudentP["Student Portal\n(Learning, Chat, Practice)"]
        TutorP["Tutor Portal\n(Review, Students, Feedback)"]
        PrincipalP["Principal Portal\n(Monitor, Quality, Reports)"]
        AdminP["Admin Portal\n(Governance, Users, Analytics)"]
    end

    subgraph Gateway["API GATEWAY"]
        Nginx["Nginx (TLS 1.3)"]
        FastAPI["FastAPI (Uvicorn Workers)"]
        WS["WebSocket Handler"]
        Auth["JWT Auth\n(4 Roles)"]
    end

    subgraph Services["SERVICE LAYER"]
        LearnSvc["Learning\nService"]
        AssessSvc["Assessment\nService"]
        ContentSvc["Content\nGenerator"]
        ReviewSvc["Content\nReview"]
        VerifySvc["Verification\nService"]
        MatchSvc["Matching\nService"]
        AnalyticsSvc["Analytics\nService"]
        VoiceSvc["Voice\nService"]
    end

    subgraph AI["AI AGENT LAYER — 12 Agents"]
        Orch["LangGraph\nOrchestrator"]
        Teacher["1. Teacher\nAgent"]
        AssessA["2. Assessment\nAgent"]
        CurricA["3. Curriculum\nAgent"]
        MotivA["4. Motivation\nAgent"]
        ContentA["5. Content Gen\nAgent"]
        PersonalA["6. Personalize\nAgent"]
        VideoA["7. Video Gen\nAgent"]
        VerifyA["8. Verification\nAgent"]
        VoiceA["9. Voice\nAgent"]
        MatchA["10. Matching\nAgent"]
        AnalyticsA["11. Analytics\nAgent"]
        ReportA["12. Report\nAgent"]
        Router["Model\nRouter"]
    end

    subgraph Models["MODEL LAYER"]
        GPT4o["GPT-4o"]
        GPT4oMini["GPT-4o-mini"]
        DeepSeek["DeepSeek V4"]
        Whisper["Whisper (STT)"]
        TTS["ElevenLabs/Azure (TTS)"]
        SymPy["SymPy (Math)"]
        OCR["Tesseract (OCR)"]
    end

    subgraph Data["DATA LAYER"]
        PG["PostgreSQL 16"]
        Redis["Redis 7"]
        Qdrant["Qdrant\n(Vector DB)"]
        MinIO["MinIO / S3\n(Files)"]
        RabbitMQ["RabbitMQ\n(Async Tasks)"]
    end

    subgraph Observe["OBSERVABILITY"]
        Langfuse["Langfuse\n(LLM Trace)"]
        Prometheus["Prometheus"]
        Grafana["Grafana"]
    end

    StudentP & TutorP & PrincipalP & AdminP --> Nginx
    Nginx --> Auth
    Auth --> FastAPI
    FastAPI --> WS
    FastAPI --> Services
    Services --> AI
    Orch --> Teacher & AssessA & CurricA & MotivA & ContentA & PersonalA & VideoA & VerifyA
    Orch --> VoiceA & MatchA & AnalyticsA & ReportA
    AI --> Router
    Router --> GPT4o & GPT4oMini & DeepSeek
    VoiceSvc --> Whisper & TTS
    AssessA --> SymPy & OCR
    ContentA --> GPT4o
    Services --> PG & Redis
    CurricA & ContentA --> Qdrant
    ContentSvc --> MinIO
    ContentSvc --> RabbitMQ
    AI --> Langfuse
    FastAPI --> Prometheus --> Grafana
```

---

## 2. Content Generation Pipeline

```mermaid
flowchart TD
    Upload["📄 Admin Uploads PDF/Notes"] --> Extract["Step 1: Extract Content\n(PyMuPDF + OCR)"]
    Extract --> Embed["Step 2: Create Embeddings\n(text-embedding-3-small)"]
    Embed --> Store["Store in Qdrant\nVector Database"]
    Store --> GenLesson["Step 3: Generate Lessons\n(GPT-4o)"]
    GenLesson --> GenVideo["Step 4: Generate Video\n+ Voice Narration"]
    GenVideo --> Personalize["Step 5: Personalize\n(Language, Region, Culture, Grade)"]
    Personalize --> TutorReview{"Step 6: Tutor Review"}
    TutorReview -->|"Approve ✅"| Publish["📚 Published to\nKnowledge Base"]
    TutorReview -->|"Modify ✏️"| GenLesson
    TutorReview -->|"Reject ❌"| Rejected["Returned to Admin"]
    Publish --> Student["👩‍🎓 Student Accesses\nPersonalized Content"]
```

---

## 3. Tutor Approval Workflow

```mermaid
flowchart TD
    Register["📝 Tutor Registration\n(Personal + Professional + Documents)"] --> AIVerify["🤖 AI Verification Agent\n(OCR Docs → Cross-reference → Report)"]
    AIVerify --> PrincipalReview{"👨‍💼 Principal Review\n(Check AI Report + Suitability)"}
    PrincipalReview -->|"Approve"| AdminApproval{"⚡ Super Admin Approval\n(Final Decision)"}
    PrincipalReview -->|"Reject"| Rejected["❌ Rejected\n(With Reason)"]
    PrincipalReview -->|"Need Info"| MoreInfo["📋 Request More\nInformation"]
    MoreInfo --> Register
    AdminApproval -->|"Approve"| Activated["✅ Tutor Activated\n(Dashboard + Students Access)"]
    AdminApproval -->|"Reject"| Rejected
```

---

## 4. Student Learning Journey (8 Steps)

```mermaid
flowchart TD
    S1["Step 1: Subject Selection\n(Subject → Chapter → Topic)"] --> S2["Step 2: Personalized Content\n(Text + Audio + Video)"]
    S2 --> S3["Step 3: Voice-Based Learning\n(Ask Questions → AI Responds)"]
    S3 --> S4["Step 4: Chapter Learning\n(Videos + Exercises + Practice)"]
    S4 --> S5["Step 5: Mock Test\n(MCQ + Short Answer + Subjective)"]
    S5 --> S6["Step 6: Personalized Revision\n(AI Identifies Weak Areas)"]
    S6 --> S7["Step 7: Final Assessment\n(Comprehensive Evaluation)"]
    S7 --> S8["Step 8: Progress Dashboard\n(Scores + Badges + Streaks)"]
    S8 --> S1
```

---

## 5. Assessment Engine Architecture

```mermaid
flowchart TD
    subgraph Objective["Objective Assessment"]
        MCQ["MCQ"] --> AutoGrade["Auto-Graded\n(SymPy + Rule Engine)"]
        FillBlanks["Fill in Blanks"] --> AutoGrade
        Match["Match Following"] --> AutoGrade
    end

    subgraph Subjective["Subjective Assessment"]
        Write["Student Writes on Paper"] --> Upload["Upload Image"]
        Draw["Draws Diagrams"] --> Upload
        Upload --> OCR["OCR Processing\n(Tesseract / Azure)"]
        OCR --> AIEval["AI Evaluation\n(GPT-4o)"]
        AIEval --> AIScore["AI Score + Feedback"]
    end

    AutoGrade --> Report["Assessment Report"]
    AIScore --> Report
    Report --> TutorFB["👨‍🏫 Tutor Review\n(Additional Feedback)"]
    TutorFB --> Final["Final Score + Feedback\n(AI + Tutor Combined)"]
```

---

## 6. Multi-Agent Orchestration Flow

```mermaid
flowchart TD
    Student["👤 Student Input"] --> Intent["🎯 Intent Classifier"]

    Intent -->|"learn"| Teacher["1. Teacher Agent\n(Hint → Guide → Solve)"]
    Intent -->|"answer"| Assessment["2. Assessment Agent\n(Evaluate + Score)"]
    Intent -->|"browse"| Curriculum["3. Curriculum Agent\n(Subject → Topic)"]
    Intent -->|"progress"| Analytics["11. Analytics Agent\n(Patterns + Trends)"]

    Teacher -->|"needs context"| Curriculum
    Teacher -->|"wrong answer"| Assessment
    Assessment -->|"encourage"| Motivation["4. Motivation Agent\n(Streaks + Badges)"]
    Assessment -->|"weak area"| Curriculum

    Curriculum --> Response["📤 Response to Student"]

    subgraph Pipeline["Background Pipeline Agents"]
        ContentGen["5. Content Gen Agent\n(PDF → Lessons)"]
        Personalize["6. Personalize Agent\n(Language/Region/Culture)"]
        VideoGen["7. Video Gen Agent\n(Animated Explainers)"]
        Verify["8. Verification Agent\n(Tutor Docs Check)"]
        Matching["10. Matching Agent\n(Tutor ↔ Student)"]
        Report["12. Report Agent\n(All Roles)"]
    end

    Pipeline -.->|"content ready"| Curriculum
```

---

## 7. Database Entity Relationship (v2.0)

```mermaid
erDiagram
    users ||--o| students : "has (student)"
    users ||--o| tutors : "has (tutor)"
    users ||--o| principals : "has (principal)"
    users ||--o{ notifications : "receives"

    tutors ||--o{ tutor_documents : "submits"
    tutors ||--o{ content_reviews : "performs"
    tutors ||--o{ assessments : "reviews (as tutor)"

    principals ||--o{ approval_workflows : "manages"

    students ||--o{ sessions : "participates"
    students ||--o{ assessments : "takes"
    students }o--|| tutors : "matched to"

    curriculum_nodes ||--o{ curriculum_nodes : "parent of"
    curriculum_nodes ||--o{ content_lessons : "organizes"

    source_documents ||--o{ content_lessons : "generates"
    content_lessons ||--o{ content_reviews : "reviewed in"

    approval_workflows }o--|| tutors : "for"
    approval_workflows }o--|| content_lessons : "for"

    users {
        uuid id PK
        string email
        string password_hash
        string full_name
        string role
        string phone
        string country
        string state
        timestamp created_at
    }

    students {
        uuid id PK
        uuid user_id FK
        string gender
        string school
        string learning_style
        jsonb interests
        uuid matched_tutor_id FK
    }

    tutors {
        uuid id PK
        uuid user_id FK
        jsonb subjects
        int experience_yrs
        string verification_status
        float rating
    }

    tutor_documents {
        uuid id PK
        uuid tutor_id FK
        string doc_type
        string file_url
        boolean ai_verified
        float ai_confidence
    }

    principals {
        uuid id PK
        uuid user_id FK
        string institution
        jsonb jurisdiction
    }

    curriculum_nodes {
        uuid id PK
        uuid parent_id FK
        string node_type
        string name_en
        string name_hi
        string grade_start
    }

    content_lessons {
        uuid id PK
        uuid curriculum_node_id FK
        string title
        text content_text
        string language
        string region
        string video_url
        string status
    }

    content_reviews {
        uuid id PK
        uuid lesson_id FK
        uuid tutor_id FK
        string action
        text feedback
        float accuracy_score
    }

    approval_workflows {
        uuid id PK
        string workflow_type
        uuid target_id
        string current_step
        string status
        jsonb steps_history
    }

    source_documents {
        uuid id PK
        string title
        string file_url
        uuid uploaded_by FK
        string extraction_status
    }

    notifications {
        uuid id PK
        uuid user_id FK
        string type
        string title
        text message
        boolean is_read
    }

    assessments {
        uuid id PK
        uuid student_id FK
        string assessment_type
        string image_url
        text ocr_text
        text tutor_feedback
        text ai_feedback
    }
```

---

## 8. Deployment Architecture

```mermaid
graph TB
    subgraph Docker["DOCKER HOST"]
        subgraph Frontend["Frontend"]
            Next["Next.js :3000"]
        end
        subgraph Backend["Backend"]
            FastAPI1["FastAPI Worker 1"]
            FastAPI2["FastAPI Worker 2"]
            FastAPI3["FastAPI Worker 3"]
            FastAPI4["FastAPI Worker 4"]
        end
        subgraph Proxy["Proxy"]
            NginxD["Nginx :80/:443"]
        end
        subgraph DataS["Data Services"]
            PGD["PostgreSQL :5432"]
            RedisD["Redis :6379"]
            QdrantD["Qdrant :6333"]
            MinioD["MinIO :9000"]
        end
        subgraph Queue["Async Tasks"]
            Rabbit["RabbitMQ :5672"]
            Worker["Celery Worker"]
        end
        subgraph Monitor["Monitoring"]
            LangfuseD["Langfuse :3000"]
            PromD["Prometheus :9090"]
            GrafanaD["Grafana :3001"]
        end
    end

    Internet["Internet"] --> NginxD
    NginxD --> Next
    NginxD --> FastAPI1 & FastAPI2 & FastAPI3 & FastAPI4
    FastAPI1 & FastAPI2 & FastAPI3 & FastAPI4 --> PGD & RedisD & QdrantD & MinioD
    FastAPI1 --> Rabbit
    Rabbit --> Worker
    Worker --> PGD & MinioD
    PromD --> FastAPI1
    GrafanaD --> PromD
```

---

## 9. Hint → Guide → Solve Flow (Student Interaction)

```mermaid
stateDiagram-v2
    [*] --> QuestionReceived: Student asks question

    QuestionReceived --> Hint1: AI Teacher gives Hint 1\n(Conceptual nudge)
    Hint1 --> StudentAttempt1: Student tries
    StudentAttempt1 --> Correct1: Answer correct ✅
    StudentAttempt1 --> Hint2: Answer wrong ❌

    Hint2 --> StudentAttempt2: Student tries again
    StudentAttempt2 --> Correct2: Answer correct ✅
    StudentAttempt2 --> Hint3: Answer wrong ❌

    Hint3 --> StudentAttempt3: Student tries again
    StudentAttempt3 --> Correct3: Answer correct ✅
    StudentAttempt3 --> Solution: Student gives up / asks

    Solution --> StepByStep: Show step-by-step solution\n+ Explain why answer was wrong
    StepByStep --> FinalAnswer: Show correct answer

    Correct1 --> Celebrate: 🎉 Celebration + points
    Correct2 --> Celebrate: 🎉 Celebration + points
    Correct3 --> Celebrate: 🎉 Celebration + points
    FinalAnswer --> UpdateTwin: Save to Digital Twin

    Celebrate --> UpdateTwin
    UpdateTwin --> [*]: Session continues
```

---

*Diagrams render natively on GitHub when viewing the markdown file.*

---

## 10. Notification & Feedback Flow (v2.1)

```mermaid
flowchart TD
    subgraph Triggers["TRIGGERS"]
        AI_Content["AI Content Generated"]
        Student_Answer["Subjective Answer Submitted"]
        Student_FB["Student Submits Tutor Feedback"]
        Tutor_Report["Tutor Creates Student Report"]
        Reassign_Req["Tutor Requests Reassignment"]
    end

    subgraph Notifications["NOTIFICATION CENTERS"]
        Tutor_NC["👨‍🏫 Tutor Notification Center<br/>• Content pending<br/>• Answers to evaluate<br/>• Reassignment updates"]
        Principal_NC["👨‍💼 Principal Notification Center<br/>• Tutor approvals<br/>• Reassignment requests<br/>• Low feedback alerts<br/>• Escalations"]
        Admin_NC["⚡ Admin Notification Center<br/>• Final tutor approvals<br/>• Platform alerts<br/>• Compliance exceptions"]
        Student_NC["👩‍🎓 Student<br/>• Tutor report ready<br/>• Assessment results"]
    end

    AI_Content --> Tutor_NC
    Student_Answer --> Tutor_NC
    Reassign_Req --> Tutor_NC
    Reassign_Req --> Principal_NC
    Student_FB --> Principal_NC
    Student_FB --> Admin_NC
    Tutor_Report --> Student_NC
    
    Tutor_NC --> Action["Action Taken<br/>(Approve/Reject/Escalate)"]
    Principal_NC --> Action
    Admin_NC --> Action
```

## 11. Student Feedback → Principal Oversight Flow (v2.1)

```mermaid
flowchart LR
    Student["👩‍🎓 Student"] -->|Rating + Feedback| System["Feedback System"]
    System --> Tutor_DB[("Tutor Feedback DB")]
    Tutor_DB --> Agg["AI Aggregation"]
    Agg --> Tutor_View["Tutor: Personal Rating"]
    Agg --> Principal_View["Principal: All Tutors' Ratings"]
    Agg --> Admin_View["Admin: Platform-Wide"]
    Agg -->|Rating < 3.0| Alert["⚠️ Low Feedback Alert → Principal NC"]
```
