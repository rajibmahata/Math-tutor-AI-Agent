"""Pydantic schemas for GanitMitra API."""

from datetime import datetime, date
from typing import Optional, Literal
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, field_validator


# =============================================================================
# Authentication
# =============================================================================

class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=255)
    role: Literal["student", "tutor", "principal", "parent", "admin"] = "student"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class GoogleAuthRequest(BaseModel):
    id_token: str
    role: Literal["student", "tutor", "principal", "parent", "admin"] = "student"


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: "UserResponse"
    is_new_user: bool = False


class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    role: str
    is_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# =============================================================================
# Students
# =============================================================================

class StudentCreateRequest(BaseModel):
    age: int = Field(ge=3, le=16)
    grade: str = Field(pattern=r"^(N|KG|[1-9]|10)$")
    preferred_language: Literal["en", "hi", "bn"] = "en"
    board: str = "ncert"

    @field_validator("grade")
    @classmethod
    def validate_grade(cls, v: str) -> str:
        valid = {"N", "KG", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"}
        if v not in valid:
            raise ValueError(f"Grade must be one of: {valid}")
        return v


class StudentUpdateRequest(BaseModel):
    age: Optional[int] = Field(default=None, ge=3, le=16)
    grade: Optional[str] = None
    preferred_language: Optional[Literal["en", "hi", "bn"]] = None
    board: Optional[str] = None


class LinkParentRequest(BaseModel):
    parent_email: EmailStr
    relationship: str = "parent"


class TopicSummary(BaseModel):
    topic_id: UUID
    name: str
    mastery_score: float
    questions_attempted: int
    accuracy_rate: float


class ProgressSummary(BaseModel):
    topics_mastered: int
    topics_in_progress: int
    topics_remaining: int
    grade_progress_pct: float


class StudentResponse(BaseModel):
    id: UUID
    user_id: UUID
    parent_id: Optional[UUID] = None
    age: int
    grade: str
    preferred_language: str
    board: str
    learning_speed: float
    confidence_score: float
    accuracy_rate: float
    current_streak: int
    longest_streak: int
    total_points: int
    total_sessions: int
    total_time_spent: int
    total_questions: int
    correct_answers: int
    current_topic: Optional[TopicSummary] = None
    strengths: list[TopicSummary] = Field(default_factory=list)
    weaknesses: list[TopicSummary] = Field(default_factory=list)
    progress_summary: Optional[ProgressSummary] = None
    placement_complete: bool
    last_session_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# =============================================================================
# Sessions & Tutoring
# =============================================================================

class StartSessionRequest(BaseModel):
    session_type: Literal["tutoring", "practice", "assessment"] = "tutoring"
    language: Literal["en", "hi", "bn"] = "en"
    topic_id: Optional[UUID] = None


class SessionResponse(BaseModel):
    id: UUID
    student_id: UUID
    session_type: str
    language: str
    status: str
    started_at: datetime
    ws_endpoint: str


class SessionSummary(BaseModel):
    id: UUID
    session_type: str
    language: str
    topic: Optional[TopicSummary] = None
    questions_asked: int
    questions_correct: int
    duration_seconds: Optional[int]
    started_at: datetime
    ended_at: Optional[datetime]


class MessageResponse(BaseModel):
    id: UUID
    role: str
    content: str
    content_type: str
    hint_level: Optional[int] = None
    is_correct: Optional[bool] = None
    math_expression: Optional[str] = None
    created_at: datetime


# =============================================================================
# Practice
# =============================================================================

class GeneratePracticeRequest(BaseModel):
    topic_id: Optional[UUID] = None
    difficulty: Literal["easy", "medium", "hard", "adaptive"] = "adaptive"
    question_count: int = Field(default=10, ge=1, le=50)
    language: Literal["en", "hi", "bn"] = "en"


class PracticeQuestionResponse(BaseModel):
    question_number: int
    question_text: str
    question_latex: Optional[str] = None
    difficulty: float
    hints: list[str] = Field(default_factory=list)


class PracticeSetResponse(BaseModel):
    id: UUID
    title: str
    topic: Optional[TopicSummary] = None
    difficulty: str
    question_count: int
    questions: list[PracticeQuestionResponse]
    status: str


class SubmitAnswerRequest(BaseModel):
    answer: str
    time_taken_seconds: Optional[int] = None
    hints_used: int = 0


class SubmitAnswerResponse(BaseModel):
    is_correct: bool
    correct_answer: str
    solution: Optional[dict] = None
    points_earned: int = 0
    new_streak: int = 0


# =============================================================================
# Progress & Analytics
# =============================================================================

class TopicCategoryProgress(BaseModel):
    mastered: int
    in_progress: int
    not_started: int
    avg_mastery: float


class DailyActivity(BaseModel):
    date: date
    questions: int
    accuracy: float
    time_spent: int


class WeakArea(BaseModel):
    topic_id: UUID
    name: str
    mastery_score: float
    questions_attempted: int
    accuracy: float
    common_error: Optional[str] = None


class ProgressResponse(BaseModel):
    student_id: UUID
    grade: str
    grade_progress_pct: float
    topics_by_category: dict[str, TopicCategoryProgress]
    learning_velocity: float
    weekly_activity: list[DailyActivity]
    weak_areas: list[WeakArea]
    strong_areas: list[TopicSummary]
    confidence_trend: list[float]
    updated_at: datetime


# =============================================================================
# Parent Reports
# =============================================================================

class ReportResponse(BaseModel):
    id: UUID
    student_id: UUID
    report_type: str
    period_start: date
    period_end: date
    summary_text: Optional[str]
    key_strengths: list[dict]
    key_weaknesses: list[dict]
    recommendations: list[dict]
    stats: dict
    is_read: bool
    generated_at: datetime


# =============================================================================
# Voice
# =============================================================================

class TTSRequest(BaseModel):
    text: str = Field(max_length=2000)
    language: Literal["en", "hi", "bn"] = "en"
    voice_style: Literal["natural", "gentle", "excited"] = "natural"


class STTResponse(BaseModel):
    text: str
    language_detected: str
    confidence: float
    duration_seconds: float


# =============================================================================
# Health
# =============================================================================

class HealthResponse(BaseModel):
    status: str
    version: str
    services: dict
    timestamp: datetime


# =============================================================================
# Pagination
# =============================================================================

class PaginationMeta(BaseModel):
    next_cursor: Optional[str] = None
    has_more: bool = False


class PaginatedResponse(BaseModel):
    data: list
    pagination: PaginationMeta
