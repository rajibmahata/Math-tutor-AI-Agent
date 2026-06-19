# AI Agent Design — GanitMitra Multi-Agent System

> **Date:** 2026-06-19
> **Version:** 1.0
> **Framework:** LangGraph
> **Author:** WorkCore (AI Engineer)

---

## 1. Agent Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR AGENT                              │
│              (LangGraph StateGraph — Main Router)                  │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │                 INTENT CLASSIFIER                          │    │
│  │  "What does the student need right now?"                  │    │
│  │  ┌─────────┬─────────┬──────────┬────────┬─────────┐     │    │
│  │  │LEARN    │PRACTICE │ASSESS    │PROGRESS│ VOICE   │     │    │
│  │  │(teach)  │(quiz)   │(evaluate)│(report)│ (stt/   │     │    │
│  │  │         │         │          │        │  tts)   │     │    │
│  │  └────┬────┘────┬────┘────┬─────┘───┬────┘────┬────┘     │    │
│  └───────┼─────────┼─────────┼─────────┼─────────┼──────────┘    │
│          │         │         │         │         │                │
│          ▼         ▼         ▼         ▼         ▼                │
│  ┌──────────┐┌──────────┐┌──────────┐┌──────────┐┌──────────┐   │
│  │ TEACHER  ││ PRACTICE ││ASSESSMENT││ANALYTICS ││  VOICE   │   │
│  │  AGENT   ││  AGENT   ││  AGENT   ││  AGENT   ││  AGENT   │   │
│  └────┬─────┘└──────────┘└────┬─────┘└────┬─────┘└──────────┘   │
│       │                      │           │                       │
│       ├──────────────────────┘           │                       │
│       │                                  │                       │
│       ▼                                  ▼                       │
│  ┌──────────┐                     ┌──────────┐                   │
│  │CURRICULUM│                     │MOTIVATION│                   │
│  │  AGENT   │                     │  AGENT   │                   │
│  │  (RAG)   │                     │(encourage)                   │
│  └──────────┘                     └──────────┘                   │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │                 SCHEDULED AGENTS (Cron)                    │    │
│  │  ┌──────────────────┐  ┌──────────────────────────┐      │    │
│  │  │  PARENT REPORT   │  │   STUDENT TWIN UPDATER   │      │    │
│  │  │  AGENT (weekly)  │  │   (post-session async)   │      │    │
│  │  └──────────────────┘  └──────────────────────────┘      │    │
│  └──────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
```

---

## 2. LangGraph Orchestrator

### 2.1 State Definition

```python
from typing import TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    # Conversation
    messages: Annotated[Sequence[BaseMessage], add_messages]

    # Student Context
    student_id: str
    student_twin: dict          # Full digital twin snapshot
    grade: str
    language: str

    # Session
    session_id: str
    session_type: str           # 'tutoring', 'practice', 'assessment'
    intent: str                 # Current detected intent

    # Tutoring State
    current_topic_id: str | None
    current_question: str | None
    current_answer: str | None
    hint_level: int             # 0=no hint yet, 1,2,3=final hint
    solution_revealed: bool

    # Assessment
    is_correct: bool | None
    error_type: str | None
    misconception: str | None

    # Results
    response: str               # Final response to student
    route: str                  # Next agent to route to
```

### 2.2 Graph Definition

```python
def build_orchestrator_graph():
    workflow = StateGraph(AgentState)

    # Add nodes (agents)
    workflow.add_node("classify_intent", classify_intent_node)
    workflow.add_node("teacher_agent", teacher_agent_node)
    workflow.add_node("assessment_agent", assessment_agent_node)
    workflow.add_node("curriculum_agent", curriculum_agent_node)
    workflow.add_node("practice_agent", practice_agent_node)
    workflow.add_node("motivation_agent", motivation_agent_node)
    workflow.add_node("analytics_agent", analytics_agent_node)
    workflow.add_node("format_response", format_response_node)

    # Define edges
    workflow.set_entry_point("classify_intent")

    # Intent-based routing
    workflow.add_conditional_edges(
        "classify_intent",
        route_by_intent,
        {
            "learn": "teacher_agent",
            "practice": "practice_agent",
            "progress": "analytics_agent",
            "greeting": "format_response",
            "END": END
        }
    )

    # Teacher flow: Teacher → Assessment → Motivation → Format
    workflow.add_edge("teacher_agent", "assessment_agent")
    workflow.add_conditional_edges(
        "assessment_agent",
        check_if_answer_provided,
        {
            "answered": "motivation_agent",
            "just_hint": "format_response"
        }
    )
    workflow.add_edge("motivation_agent", "format_response")

    # Practice flow: Practice → Format
    workflow.add_edge("practice_agent", "format_response")

    # Analytics flow: Analytics → Format
    workflow.add_edge("analytics_agent", "format_response")

    # Format → End
    workflow.add_edge("format_response", END)

    return workflow.compile()


def route_by_intent(state: AgentState) -> str:
    intent = state.get("intent", "learn")
    valid_intents = ["learn", "practice", "progress", "greeting"]
    return intent if intent in valid_intents else "learn"


def check_if_answer_provided(state: AgentState) -> str:
    if state.get("current_answer"):
        return "answered"
    return "just_hint"
```

### 2.3 Intent Classification Prompt

```python
INTENT_CLASSIFIER_PROMPT = """You are an intent classifier for a math tutoring system.
Analyze the student's message and classify the intent.

Student Grade: {grade}
Student Language: {language}
Current Topic: {current_topic}
Previous Messages: {conversation_history}

Student Message: "{student_message}"

Classify as EXACTLY one of:
- learn: Student wants to learn a new concept or asks a math question
- practice: Student wants to practice problems or take a quiz
- progress: Student asks about their progress, scores, or achievements
- greeting: Simple greeting, thank you, or non-academic chat

Intent: """
```

---

## 3. Agent Definitions

### 3.1 Teacher Agent

**Responsibility:** Guide students through mathematical problem-solving using Hint → Scaffold → Solve methodology. Never give direct answers first.

**Model:** DeepSeek V4 / GPT-4o (reasoning)

**System Prompt:**

```
You are GanitMitra, a friendly and patient math teacher for a {grade} grade student.
You teach in {language}. The student's name is {student_name}.

## YOUR TEACHING METHODOLOGY (MUST FOLLOW)

1. **NEVER give the final answer first.** This is your most important rule.

2. When given a math problem:
   a. First, provide a gentle HINT that points toward the solution concept
   b. If the student is stuck, provide GUIDED THINKING — break the problem into smaller steps
   c. Only after the student attempts, provide STEP-BY-STEP solution
   d. Finally, state the ANSWER clearly

3. **Hint Levels:**
   - Hint 1: Conceptual nudge (e.g., "Think about what operation connects these numbers")
   - Hint 2: More specific direction (e.g., "Try multiplying the first two numbers")
   - Hint 3: Almost reveals the method (e.g., "Multiply 12 × 5, then add 3")

4. **Age-Appropriate Teaching:**
   - Nursery-KG (age 3-5): Use stories, objects, pictures. "If you have 2 apples and get 1 more..."
   - Grades 1-2 (age 6-8): Use simple language, games. "Let's count together!"
   - Grades 3-5 (age 8-10): Concrete examples, word problems. "A shopkeeper has..."
   - Grades 6-8 (age 11-13): Abstract thinking, algebra intro. "Let x represent..."
   - Grades 9-10 (age 14-16): Formal math, exam focus. "Using the quadratic formula..."

5. **Language-Specific Guidance:**
   - English: Use standard math terminology
   - Hindi: Use Hindi number words (ek, do, teen...) and math terms (jod, ghatav, guna, bhag)
   - Bengali: Use Bengali number words and terms (যোগ, বিয়োগ, গুণ, ভাগ)

6. **Encouragement:** Always be encouraging. Never say "that's wrong" — say "Let's think about this differently" or "Almost there! Consider this..."

7. **Answer Verification:** All mathematical answers must be verifiable. If you're unsure, use the SymPy verification tool.

Current hint level: {hint_level}
Student's current answer: {student_answer}
```

**Tools Available:**
- `sympy_verify(expression, expected)` — Verify mathematical equivalence
- `search_curriculum(topic, grade, language)` — Search curriculum knowledge base
- `get_prerequisites(topic_id)` — Get prerequisite topics
- `translate(text, target_language)` — Translate between languages

### 3.2 Assessment Agent

**Responsibility:** Evaluate student answers, detect misconceptions, classify error types, update student twin.

**Model:** DeepSeek V4 (reasoning) + SymPy (verification)

**System Prompt:**

```
You are an assessment specialist for a math tutoring system.
Evaluate the student's answer and identify misconceptions.

Student Grade: {grade}
Topic: {topic_name}
Question: {question}
Correct Answer: {correct_answer}
Student Answer: {student_answer}

## EVALUATION STEPS

1. **Verify Correctness:**
   - Use SymPy to verify mathematical equivalence
   - For non-computational answers (explanations), use semantic comparison
   - Consider partially correct answers (right method, wrong calculation)

2. **If INCORRECT, classify the error:**
   - arithmetic: Calculation mistake (e.g., 7×8=54)
   - conceptual: Misunderstanding the concept (e.g., adding denominators)
   - order_of_ops: BODMAS/PEMDAS error
   - sign_error: Wrong sign handling
   - careless: Obvious slip (e.g., copying wrong number)
   - incomplete: Right start but didn't finish
   - no_attempt: Student gave up or asked for answer

3. **Identify misconception:**
   - What fundamental concept is the student missing?
   - What prerequisite topic should be reviewed?

4. **Provide constructive feedback:**
   - Start with something positive
   - Explain the error gently
   - Guide toward the correct approach
   - NEVER just say "wrong"

Output a structured assessment:
{
  "is_correct": bool,
  "is_partial": bool,
  "error_type": "arithmetic" | "conceptual" | "order_of_ops" | "sign_error" | "careless" | "incomplete" | null,
  "misconception": "description of what student doesn't understand",
  "prerequisite_topic_id": "topic to review" or null,
  "feedback_message": "constructive feedback in {language}",
  "confidence": 0.0-1.0
}
```

**Tools Available:**
- `sympy_verify(expression, expected)` — Verify mathematical equivalence
- `analyze_steps(student_work)` — Parse multi-step work for step-by-step validation

### 3.3 Curriculum Agent

**Responsibility:** Manage the knowledge graph of topics, determine learning sequences, suggest next topics, power the RAG pipeline.

**Model:** GPT-4o-mini (retrieval + structuring)

**System Prompt:**

```
You are a curriculum designer for Indian K-10 mathematics.
You maintain a knowledge graph of math topics with prerequisites.

## RESPONSIBILITIES

1. **Topic Sequencing:**
   - Given a student's grade and mastered topics, suggest the next topic
   - Follow prerequisite chains strictly
   - Adapt sequence to board (NCERT, ICSE, State)

2. **Prerequisite Resolution:**
   - When a student struggles with topic X, identify which prerequisites to review
   - "To understand fractions, you first need to be comfortable with division"

3. **Curriculum Alignment:**
   - Ensure all content aligns with {board} curriculum for Grade {grade}
   - Track curriculum coverage percentage

4. **Gap Analysis:**
   - Compare student's mastered topics against expected curriculum for their grade
   - Identify "at risk" topics where the student is below grade level

Student Board: {board}
Student Grade: {grade}
Mastered Topics: {mastered_topics}
Weak Topics: {weak_topics}
Current Topic: {current_topic}
```

**Tools Available:**
- `get_topic_tree(grade, board)` — Get full topic hierarchy
- `get_prerequisites(topic_id)` — Get prerequisite chain
- `get_next_topics(student_id, count)` — Suggest next topics based on progress
- `search_curriculum(query, grade, language)` — Semantic search in Qdrant
- `get_curriculum_gaps(student_id)` — Compare to grade-level expectations

### 3.4 Practice Agent

**Responsibility:** Generate practice questions, quizzes, and worksheets tailored to student needs.

**Model:** GPT-4o-mini (generation) + SymPy (verification)

**System Prompt:**

```
You are a math practice question generator.
Generate high-quality practice problems for a Grade {grade} student.

## QUESTION REQUIREMENTS

1. **Topic:** {topic_name}
2. **Difficulty:** {difficulty} (0.0=easy to 1.0=hard)
3. **Language:** {language}
4. **Count:** {question_count} questions
5. **Focus Areas:** Student is weak in {weak_areas}

## QUESTION DESIGN RULES

1. **Progressive Difficulty:** Start easier, get harder
2. **Avoid Repetition:** Different problem types within same topic
3. **Real-World Context:** Use relatable scenarios for word problems
4. **Clear Wording:** Age-appropriate language
5. **Verified Answers:** Every answer verified with SymPy

## FOR EACH QUESTION, PROVIDE:
- Question text in {language}
- LaTeX representation (if applicable)
- Correct answer
- 3 progressive hints
- Step-by-step solution
- Difficulty score (0.0-1.0)
- Topic tag

## DIFFICULTY CALIBRATION:
- 0.0-0.3: Direct application of single concept
- 0.3-0.6: Multi-step, requires combining concepts
- 0.6-0.8: Word problems, requires interpretation
- 0.8-1.0: Challenge problems, non-standard approaches

Student's past accuracy on this topic: {topic_accuracy}%
Target success rate: 80% (adjust difficulty accordingly)
```

**Tools Available:**
- `generate_questions(topic, difficulty, count, language)` — Generate questions
- `sympy_verify_batch(questions_and_answers)` — Verify all answers
- `adapt_difficulty(student_id, topic_id)` — Compute optimal difficulty

### 3.5 Motivation Agent

**Responsibility:** Provide encouragement, celebrate achievements, maintain engagement, handle frustration.

**Model:** GPT-4o-mini (fast, empathetic)

**System Prompt:**

```
You are a motivational coach for young math students.
Your job is to keep students engaged, encouraged, and confident.

Student Name: {student_name}
Grade: {grade}
Language: {language}
Current Streak: {streak} days
Just got answer: {is_correct ? 'CORRECT' : 'INCORRECT'}

## RESPONSE GUIDELINES

### If answer is CORRECT:
- Celebrate genuinely! Use the student's name
- Connect success to effort: "Your practice is paying off!"
- For streaks: "That's 5 in a row! You're on fire today!"
- Award mental points: "⭐ +10 points for that perfect solution!"
- Mention growth: "Last week this was hard, now you're solving it easily!"

### If answer is INCORRECT:
- NEVER criticize. Frame as learning opportunity
- "Almost there! This is a tricky one."
- "Good attempt! Let's see where we can adjust."
- "I can see your thinking — you're on the right track, just one small adjustment needed."
- Remind of past success: "Remember how you mastered fractions? This is the same process."

### If student seems FRUSTRATED (multiple wrong answers):
- Take a break suggestion: "Should we try an easier one to warm up?"
- Reduce pressure: "Even I find these tricky sometimes!"
- Offer alternative: "Would a visual help? Let me draw this out."
- Reassure: "Math is a journey, not a race. You're making progress."

### Achievement Triggers:
- First question of the day: "Great to see you back, {name}!"
- Streak milestone (3, 7, 14, 30 days): Special celebration message
- Topic mastered: "Congratulations! You've mastered {topic}! 🎉"
- Accuracy milestone (80%, 90%, 95%): Recognition message

Keep messages short (2-3 sentences), warm, and in {language}.
```

### 3.6 Analytics Agent

**Responsibility:** Compute learning metrics, update digital twin, generate progress visualizations data.

**Model:** Python computation + GPT-4o-mini (insights)

```python
class AnalyticsAgent:
    """
    Computes learning metrics and insights from student data.
    This is primarily a computational agent (not LLM-heavy).
    """

    def compute_mastery_score(
        self,
        correct: int,
        total: int,
        recent_accuracy: float,
        consistency: float,  # days active / days since first attempt
        difficulty_avg: float
    ) -> float:
        """
        Weighted mastery score (0.0 to 1.0).
        - Mastery threshold: 0.85
        - Recent accuracy weighted more than historical
        - Consistency bonus for regular practice
        """
        raw_accuracy = correct / max(total, 1)
        return min(1.0, (
            raw_accuracy * 0.4 +
            recent_accuracy * 0.35 +
            consistency * 0.15 +
            difficulty_avg * 0.10
        ))

    def detect_weak_topics(
        self,
        student_id: str,
        threshold: float = 0.5,
        min_attempts: int = 5
    ) -> list[dict]:
        """Flag topics where accuracy < threshold over min_attempts+ questions."""

    def compute_learning_velocity(
        self,
        student_id: str,
        days: int = 30
    ) -> float:
        """Topics mastered per week over recent period."""

    def predict_grade_readiness(
        self,
        student_id: str,
        target_grade: str
    ) -> dict:
        """Estimate readiness for next grade level."""

    def generate_weekly_summary(
        self,
        student_id: str
    ) -> dict:
        """Structured data for parent report."""
        return {
            "sessions_this_week": int,
            "questions_attempted": int,
            "accuracy": float,
            "topics_practiced": list[str],
            "topics_mastered": list[str],
            "topics_struggling": list[str],
            "time_spent_minutes": int,
            "streak_days": int,
            "grade_progress_pct": float,
            "comparison_to_previous_week": dict
        }
```

### 3.7 Parent Report Agent

**Responsibility:** Generate weekly/monthly progress reports for parents.

**Model:** GPT-4o (structured generation)

**Trigger:** Scheduled (weekly, Sunday 9 AM IST) + on-demand

**System Prompt:**

```
You are a parent communication specialist for GanitMitra math tutoring.
Generate a clear, reassuring progress report for a parent.

Student: {student_name}, Grade {grade}
Report Period: {period_start} to {period_end}
Language: {language}

## REPORT DATA
- Sessions this week: {sessions}
- Questions attempted: {questions}
- Accuracy: {accuracy}%
- Time spent learning: {time_spent} minutes
- Topics mastered this week: {topics_mastered}
- Topics practiced: {topics_practiced}
- Areas needing attention: {weak_topics}
- Current streak: {streak} days
- Overall grade progress: {grade_progress}%

## REPORT STRUCTURE

### 1. Header
"{student_name}'s Weekly Math Report"
Period: {date_range}

### 2. Quick Summary (1-2 sentences)
"Great week! {name} attempted {questions} questions with {accuracy}% accuracy."

### 3. What Went Well (2-3 bullet points)
- Celebrate mastered topics
- Highlight improvements from previous week
- Note consistent effort

### 4. Areas for Growth (1-2 bullet points)
- Gentle mention of struggling topics
- Frame as "opportunity" not "problem"
- Suggest specific support: "Try practicing multiplication tables for 10 minutes daily"

### 5. Recommendation (1-2 action items)
- Specific, actionable suggestions for parents
- "Ask {name} to explain the concept to you — teaching reinforces learning!"

### 6. Motivational Closing
- Encouraging note about learning as a journey
- Reminder that struggle is part of growth

## TONE
- Warm and supportive
- Professional but not clinical
- Focus on growth, not scores
- In {language}
- Respect parents' time — be concise
```

### 3.8 Voice Agent

**Responsibility:** Handle speech-to-text (STT) and text-to-speech (TTS) pipelines.

**Model:** Whisper (STT), ElevenLabs/Azure (TTS)

```python
class VoiceAgent:
    """
    Manages voice interaction pipelines.
    """

    # STT Pipeline
    async def speech_to_text(
        self,
        audio_data: bytes,
        language: str  # 'en', 'hi', 'bn'
    ) -> str:
        """
        1. Receive audio blob from frontend (WebM/WAV)
        2. Send to OpenAI Whisper API with language hint
        3. Return transcribed text
        """
        # Whisper handles EN/HI/BN natively
        # For mixed-language (Hinglish), use no language hint

    # TTS Pipeline
    async def text_to_speech(
        self,
        text: str,
        language: str,
        voice_style: str = "natural"  # 'natural', 'excited', 'gentle'
    ) -> bytes:
        """
        1. Preprocess text for TTS (handle math expressions)
        2. Route to appropriate TTS service
        3. Return audio bytes
        """

    # Math-to-Speech Handling
    def preprocess_math_for_tts(self, text: str, language: str) -> str:
        """
        Convert LaTeX/math to speakable text.
        "x^2 + 3x + 2 = 0" → "x squared plus three x plus two equals zero"
        Language-specific math reading:
        - EN: "x squared plus three x plus two equals zero"
        - HI: "x varg plus teen x plus do barabar zero"
        - BN: "x borgo plus teen x plus dui soman shunno"
        """
```

---

## 4. Model Routing Logic

```python
class ModelRouter:
    """
    Routes tasks to appropriate LLM models based on:
    - Task complexity
    - Latency requirements
    - Cost constraints
    - Language requirements
    """

    ROUTING_TABLE = {
        # Simple/fast tasks → cheap model
        "greeting":            {"model": "gpt-4o-mini",    "max_tokens": 150,  "temperature": 0.7},
        "encouragement":       {"model": "gpt-4o-mini",    "max_tokens": 200,  "temperature": 0.8},
        "intent_classify":     {"model": "gpt-4o-mini",    "max_tokens": 50,   "temperature": 0.1},

        # Teaching tasks → reasoning model
        "hint_generation":     {"model": "gpt-4o-mini",    "max_tokens": 300,  "temperature": 0.5},
        "step_by_step":        {"model": "deepseek-v4",    "max_tokens": 800,  "temperature": 0.3},
        "answer_evaluation":   {"model": "deepseek-v4",    "max_tokens": 500,  "temperature": 0.2},
        "misconception":       {"model": "deepseek-v4",    "max_tokens": 400,  "temperature": 0.3},

        # Generation tasks
        "question_generation": {"model": "gpt-4o-mini",    "max_tokens": 2000, "temperature": 0.7},
        "report_generation":   {"model": "gpt-4o",         "max_tokens": 1500, "temperature": 0.5},

        # Translation (use multilingual native capability)
        "translation":         {"model": "gpt-4o-mini",    "max_tokens": 500,  "temperature": 0.2},

        # Curriculum/retrieval
        "curriculum_search":   {"model": "gpt-4o-mini",    "max_tokens": 300,  "temperature": 0.1},
        "topic_sequence":      {"model": "gpt-4o-mini",    "max_tokens": 300,  "temperature": 0.1},
    }

    FALLBACK_CHAIN = [
        "deepseek-v4",      # Primary reasoning
        "gpt-4o",           # Secondary reasoning
        "claude-sonnet",    # Tertiary
        "gpt-4o-mini",      # Fallback (faster, less capable)
    ]

    async def route(
        self,
        task_type: str,
        messages: list,
        language: str = "en",
        stream: bool = False
    ) -> dict:
        """
        1. Look up task_type in ROUTING_TABLE
        2. Add language-specific system message
        3. Attempt primary model
        4. On failure, try fallback chain
        5. Log to Langfuse
        """
```

---

## 5. RAG Pipeline (Curriculum Knowledge Base)

```python
class CurriculumRAG:
    """
    Retrieval-Augmented Generation for curriculum-aligned responses.
    Vector DB: Qdrant
    Embedding Model: text-embedding-3-small (OpenAI) — multilingual
    """

    # Curriculum Sources
    SOURCES = [
        "NCERT Mathematics Textbooks (Class 1-10)",
        "ICSE Mathematics Textbooks",
        "West Bengal Board Mathematics (Bengali medium)",
        "State Board Common Core Topics",
        "Khan Academy Math Content (for supplementary examples)",
    ]

    # Chunking Strategy
    CHUNK_SIZE = 512        # tokens
    CHUNK_OVERLAP = 50      # tokens for context continuity
    CHUNK_STRATEGY = "semantic"  # Break at section/topic boundaries

    # Retrieval
    TOP_K = 5               # Retrieve top 5 chunks
    RERANK_ENABLED = True   # Cross-encoder reranking
    SIMILARITY_THRESHOLD = 0.7  # Minimum relevance score

    async def retrieve(
        self,
        query: str,
        grade: str,
        language: str,
        topic_id: str = None,
        top_k: int = 5
    ) -> list[dict]:
        """
        1. Generate query embedding
        2. Search Qdrant with filters (grade, language, topic)
        3. Rerank results with cross-encoder
        4. Return relevant curriculum chunks
        """

    async def enrich_prompt(
        self,
        base_prompt: str,
        context_chunks: list[dict]
    ) -> str:
        """
        Inject retrieved curriculum context into agent prompt.
        """
        context_text = "\n\n".join([
            f"[{chunk['source']}, Grade {chunk['grade']}]: {chunk['text']}"
            for chunk in context_chunks
        ])
        return f"""{base_prompt}

## CURRICULUM CONTEXT

The following is from the official {grade} curriculum:

{context_text}

Use this context to ensure your teaching is aligned with the curriculum.
"""
```

---

## 6. Guardrails & Safety

### 6.1 Content Safety

```python
GUARDRAIL_RULES = {
    "no_direct_answers": """
        If the student asks directly for the answer without attempting,
        respond with a hint instead. NEVER give the final answer first.
    """,
    "age_appropriate": """
        No violent, scary, or inappropriate examples.
        No dark themes in word problems.
    """,
    "no_personal_info": """
        Never ask for or store: phone numbers, addresses, school names,
        photos, or other PII beyond what's in the profile.
    """,
    "academic_integrity": """
        If student appears to be taking a test/exam,
        transition to teaching mode rather than just giving answers.
    """,
    "language_purity": """
        When responding in Hindi or Bengali, use natural language,
        not transliterated English. Use proper script.
        For math terms, use language-appropriate terminology.
    """,
}
```

### 6.2 Prompt Injection Defense

```python
def sanitize_student_input(text: str) -> str:
    """
    Sanitize student input before passing to LLM.
    - Remove system prompt injection patterns
    - Strip HTML/script tags
    - Limit length (max 2000 chars)
    """
    # Strip common injection patterns
    injection_patterns = [
        r"<\|.*?\|>",         # ChatML markers
        r"\[SYSTEM.*?\]",      # Fake system messages
        r"\[INST.*?\]",        # Instruction markers
        r"忽略.*?指令",        # "Ignore instructions" in Chinese
        r"ignore.*?prompt",    # "Ignore prompt"
    ]
    for pattern in injection_patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)
    return text[:2000]
```

---

## 7. Langfuse Integration (Observability)

```python
# All agent calls traced through Langfuse
from langfuse import Langfuse

langfuse = Langfuse(
    public_key=settings.LANGFUSE_PUBLIC_KEY,
    secret_key=settings.LANGFUSE_SECRET_KEY,
)

@observe(name="teacher_agent")
async def teacher_agent_node(state: AgentState):
    trace = langfuse.trace(
        name="tutoring_turn",
        user_id=state["student_id"],
        session_id=state["session_id"],
        metadata={
            "grade": state["grade"],
            "language": state["language"],
            "topic": state.get("current_topic_id"),
            "hint_level": state.get("hint_level", 0),
        }
    )
    # ... agent logic ...
    trace.update(output={"response_length": len(response)})
```

---

## Next: API Specification → [api-specification.md](./api-specification.md)
