# Architecture Diagrams

> **Date:** 2026-06-19
> **Format:** Mermaid (renders on GitHub)

---

## 1. System Architecture

```mermaid
graph TB
    subgraph Client["CLIENT LAYER"]
        Web["Next.js SSR\n(Desktop)"]
        PWA["PWA\n(Mobile)"]
        Voice["Voice Interface\n(STT/TTS)"]
    end

    subgraph Gateway["API GATEWAY"]
        Nginx["Nginx\n(Reverse Proxy + TLS)"]
        FastAPI["FastAPI\n(Uvicorn Workers)"]
        WS["WebSocket\nHandler"]
    end

    subgraph Services["SERVICE LAYER"]
        Tutoring["Tutoring\nService"]
        Assessment["Assessment\nService"]
        Practice["Practice\nService"]
        Analytics["Analytics\nService"]
        Student["Student Profile\nService"]
        Curriculum["Curriculum\nService"]
        Report["Report\nService"]
        VoiceSvc["Voice\nService"]
    end

    subgraph AI["AI AGENT LAYER"]
        Orch["LangGraph\nOrchestrator"]
        Teacher["Teacher\nAgent"]
        AssessA["Assessment\nAgent"]
        CurricA["Curriculum\nAgent"]
        PractA["Practice\nAgent"]
        MotivA["Motivation\nAgent"]
        AnalytA["Analytics\nAgent"]
        ParentA["Parent Report\nAgent"]
        VoiceA["Voice\nAgent"]
        Router["Model\nRouter"]
    end

    subgraph Models["MODEL LAYER"]
        GPT4o["GPT-4o\n(Reasoning)"]
        GPT4oMini["GPT-4o-mini\n(Fast Chat)"]
        DeepSeek["DeepSeek V4\n(Math)"]
        Whisper["Whisper\n(STT)"]
        ElevenLabs["ElevenLabs\n(TTS)"]
        SymPy["SymPy\n(Verify)"]
    end

    subgraph Data["DATA LAYER"]
        PG["PostgreSQL\n(Primary DB)"]
        Redis["Redis\n(Cache/Sessions)"]
        Qdrant["Qdrant\n(Vector DB)"]
    end

    subgraph Observe["OBSERVABILITY"]
        Langfuse["Langfuse\n(LLM Trace)"]
        Prometheus["Prometheus\n(Metrics)"]
        Grafana["Grafana\n(Dashboards)"]
    end

    Web --> Nginx
    PWA --> Nginx
    Voice --> Nginx
    Nginx --> FastAPI
    Nginx --> WS
    FastAPI --> Services
    Services --> AI
    Orch --> Teacher & AssessA & CurricA & PractA & MotivA & AnalytA
    ParentA -.-> Orch
    VoiceA -.-> Orch
    AI --> Router
    Router --> GPT4o & GPT4oMini & DeepSeek
    VoiceSvc --> Whisper & ElevenLabs
    AssessA --> SymPy
    Services --> PG
    Services --> Redis
    CurricA --> Qdrant
    AI --> Langfuse
    FastAPI --> Prometheus
    Prometheus --> Grafana
```

---

## 2. Multi-Agent Workflow

```mermaid
flowchart TD
    Student["👤 Student Message"] --> Classify["🎯 Intent Classifier"]

    Classify -->|"learn"| Teacher["🧑‍🏫 Teacher Agent\nHint → Guide → Solve"]
    Classify -->|"practice"| Practice["✏️ Practice Agent\nGenerate Quiz"]
    Classify -->|"progress"| Analytics["📊 Analytics Agent\nCompute Progress"]
    Classify -->|"greeting"| Format["💬 Format Response"]

    Teacher -->|"student answers"| Assessment["✅ Assessment Agent\nEvaluate + Detect Misconception"]
    Teacher -->|"just a hint"| Format

    Assessment -->|"answered"| Motivation["🎯 Motivation Agent\nEncourage + Celebrate"]
    Assessment -->|"wrong answer\nneeds context"| Curriculum["📚 Curriculum Agent\nRAG Retrieval"]
    Curriculum --> Teacher

    Motivation --> StudentTwin["👤 Update Student Twin"]
    Motivation --> Format

    Practice --> Format
    Analytics --> Format

    Format --> Response["📤 Response to Student"]

    subgraph Scheduled["⏰ Scheduled (Cron)"]
        ParentReport["📄 Parent Report Agent\nWeekly Report Generation"]
        TwinUpdate["🔄 Twin Updater\nPost-Session Async"]
    end

    ParentReport --> Notification["📧 Parent Notification"]
```

---

## 3. Data Flow: Tutoring Session

```mermaid
sequenceDiagram
    actor S as Student
    participant FE as Next.js Frontend
    participant API as FastAPI
    participant O as LangGraph Orchestrator
    participant TA as Teacher Agent
    participant AA as Assessment Agent
    participant CA as Curriculum Agent
    participant MR as Model Router
    participant LLM as LLM (DeepSeek/GPT)
    participant SP as SymPy
    participant DB as PostgreSQL
    participant R as Redis

    S->>FE: Ask math question
    FE->>API: POST /sessions (WS connect)
    API->>DB: Load Student Twin
    DB-->>API: Student profile
    API->>R: Cache session state
    API->>O: Route to Orchestrator

    O->>O: Classify Intent
    O->>CA: Get curriculum context
    CA->>DB: Search topic knowledge
    DB-->>CA: Topic + prerequisites
    CA-->>O: Curriculum context

    O->>TA: Generate hint
    TA->>MR: Route to LLM (DeepSeek V4)
    MR->>LLM: Generate hint
    LLM-->>MR: Hint response
    MR-->>TA: Hint
    TA-->>O: Hint ready
    O-->>API: Response
    API-->>FE: Hint (WebSocket)
    FE-->>S: Display hint

    S->>FE: Submit answer ("60")
    FE->>API: WS: student answer
    API->>O: Route to Assessment

    O->>AA: Evaluate answer
    AA->>SP: Verify 12×5=60
    SP-->>AA: True
    AA->>MR: Classify correctness + misconception
    MR->>LLM: DeepSeek V4
    LLM-->>AA: Correct, no misconception
    AA-->>O: is_correct=true

    O->>DB: Update Student Twin
    O->>DB: Save session message
    O->>API: Response
    API-->>FE: Feedback + motivation
    FE-->>S: "⭐ Bilkul sahi! +10 points"
```

---

## 4. Model Routing Decision Tree

```mermaid
flowchart TD
    Task["Incoming Task"] --> Classify["Task Classifier"]

    Classify --> Type1{"Task Type?"}

    Type1 -->|"greeting/encouragement"| Fast["GPT-4o-mini\nFast + Cheap"]
    Type1 -->|"intent classification"| Fast2["GPT-4o-mini\nLow temp"]
    Type1 -->|"hint generation"| Fast3["GPT-4o-mini\nMed temp"]
    Type1 -->|"step-by-step solution"| Reason["DeepSeek V4 / GPT-4o\nStrong Reasoning"]
    Type1 -->|"answer evaluation"| Reason2["DeepSeek V4\n+ SymPy verify"]
    Type1 -->|"misconception detection"| Reason3["GPT-4o\nAnalysis"]
    Type1 -->|"question generation"| Fast4["GPT-4o-mini\n+ SymPy batch verify"]
    Type1 -->|"report generation"| Reason4["GPT-4o\nStructured output"]
    Type1 -->|"translation"| Multi["GPT-4o-mini\nMultilingual native"]
    Type1 -->|"curriculum search"| Fast5["GPT-4o-mini\n+ Qdrant RAG"]

    Reason --> Fallback{"Primary OK?"}
    Reason2 --> Fallback
    Reason3 --> Fallback
    Reason4 --> Fallback
    Fast --> Done["Return Response"]
    Fast2 --> Done
    Fast3 --> Done
    Fast4 --> Done
    Fast5 --> Done
    Multi --> Done

    Fallback -->|"yes"| Done
    Fallback -->|"no"| FB2["Fallback: GPT-4o"]
    FB2 -->|"ok"| Done
    FB2 -->|"no"| FB3["Fallback: Claude Sonnet"]
    FB3 -->|"ok"| Done
    FB3 -->|"no"| Cache["Return Cached/Error"]
```

---

## 5. Database ER Diagram

```mermaid
erDiagram
    users ||--|| students : "has"
    users ||--o{ parent_reports : "receives (as parent)"
    users ||--o{ refresh_tokens : "has"
    students ||--o{ sessions : "participates"
    students ||--o{ student_topic_progress : "tracks"
    students ||--o{ practice_sets : "completes"
    students ||--o{ student_achievements : "earns"
    students ||--o{ assessments : "evaluated"
    sessions ||--o{ messages : "contains"
    messages ||--|| assessments : "evaluated by"
    topics ||--o{ topic_prerequisites : "requires"
    topics ||--o{ student_topic_progress : "tracked in"
    topics ||--o{ assessments : "categorized by"
    topics ||--o{ knowledge_documents : "covered by"
    practice_sets ||--o{ practice_questions : "contains"
    practice_questions }o--|| topics : "belongs to"

    users {
        uuid id PK
        string email UK
        string password_hash
        string full_name
        string role
        string google_id
        boolean is_active
        timestamp created_at
    }

    students {
        uuid id PK
        uuid user_id FK
        uuid parent_id FK
        int age
        string grade
        string preferred_language
        float learning_speed
        float confidence_score
        int total_questions
        float accuracy_rate
        int current_streak
        int total_points
    }

    sessions {
        uuid id PK
        uuid student_id FK
        string session_type
        string language
        int questions_asked
        string status
        timestamp started_at
    }

    messages {
        uuid id PK
        uuid session_id FK
        string role
        text content
        string content_type
        int hint_level
        boolean is_correct
    }

    assessments {
        uuid id PK
        uuid message_id FK
        uuid student_id FK
        uuid topic_id FK
        boolean is_correct
        string error_type
        text misconception
        boolean sympy_verified
    }

    topics {
        uuid id PK
        uuid parent_id FK
        string name_en
        string name_hi
        string name_bn
        string grade_start
        string category
    }

    student_topic_progress {
        uuid id PK
        uuid student_id FK
        uuid topic_id FK
        float mastery_score
        boolean is_weak
        int questions_attempted
    }

    practice_sets {
        uuid id PK
        uuid student_id FK
        uuid topic_id FK
        string difficulty
        int question_count
        string status
    }

    practice_questions {
        uuid id PK
        uuid practice_set_id FK
        int question_number
        text question_text
        text correct_answer
        jsonb hints
    }

    parent_reports {
        uuid id PK
        uuid student_id FK
        uuid parent_id FK
        string report_type
        date period_start
        date period_end
        jsonb report_data
    }

    topic_prerequisites {
        uuid id PK
        uuid topic_id FK
        uuid prerequisite_id FK
        string importance
    }

    knowledge_documents {
        uuid id PK
        string title
        uuid topic_id FK
        string grade
        string language
        string qdrant_collection
    }
```

---

## 6. Deployment Architecture

```mermaid
graph TB
    subgraph Docker["DOCKER HOST"]
        subgraph Frontend["Frontend Container"]
            Next["Next.js :3000"]
        end

        subgraph Backend["Backend Container"]
            FastAPI1["FastAPI Worker 1"]
            FastAPI2["FastAPI Worker 2"]
            FastAPI3["FastAPI Worker 3"]
            FastAPI4["FastAPI Worker 4"]
        end

        subgraph Proxy["Reverse Proxy"]
            NginxD["Nginx :80/:443"]
        end

        subgraph DataS["Data Services"]
            PGD["PostgreSQL :5432"]
            RedisD["Redis :6379"]
            QdrantD["Qdrant :6333"]
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
    FastAPI1 & FastAPI2 & FastAPI3 & FastAPI4 --> PGD
    FastAPI1 & FastAPI2 & FastAPI3 & FastAPI4 --> RedisD
    FastAPI1 & FastAPI2 & FastAPI3 & FastAPI4 --> QdrantD
    FastAPI1 & FastAPI2 & FastAPI3 & FastAPI4 --> LangfuseD
    PromD --> FastAPI1 & FastAPI2 & FastAPI3 & FastAPI4
    GrafanaD --> PromD
```

---

## 7. Hint → Guide → Solve Flow

```mermaid
stateDiagram-v2
    [*] --> QuestionReceived: Student asks question

    QuestionReceived --> Hint1: Teacher gives Hint 1\n(Conceptual nudge)
    Hint1 --> StudentAttempt1: Student tries
    StudentAttempt1 --> Correct1: Answer correct ✅
    StudentAttempt1 --> Hint2: Answer wrong ❌

    Hint2 --> StudentAttempt2: Student tries again
    StudentAttempt2 --> Correct2: Answer correct ✅
    StudentAttempt2 --> Hint3: Answer wrong ❌

    Hint3 --> StudentAttempt3: Student tries again
    StudentAttempt3 --> Correct3: Answer correct ✅
    StudentAttempt3 --> Solution: Student gives up/asks

    Solution --> StepByStep: Show step-by-step\nsolution
    StepByStep --> FinalAnswer: Show final answer

    Correct1 --> Celebrate: Motivation + points
    Correct2 --> Celebrate: Motivation + points
    Correct3 --> Celebrate: Motivation + points
    FinalAnswer --> UpdateTwin: Save to student profile

    Celebrate --> UpdateTwin
    UpdateTwin --> [*]: Session continues
```

---

*These diagrams are rendered natively by GitHub when viewing the markdown files.*
