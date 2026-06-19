// TypeScript type definitions for GanitMitra

// =============================================================================
// User & Auth
// =============================================================================
export type UserRole = "student" | "parent" | "admin";
export type Language = "en" | "hi" | "bn";
export type Grade = "N" | "KG" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" | "10";

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_verified: boolean;
  created_at: string;
}

export interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

// =============================================================================
// Student (Digital Twin)
// =============================================================================
export interface TopicSummary {
  topic_id: string;
  name: string;
  mastery_score: number;
  questions_attempted: number;
  accuracy_rate: number;
}

export interface ProgressSummary {
  topics_mastered: number;
  topics_in_progress: number;
  topics_remaining: number;
  grade_progress_pct: number;
}

export interface Student {
  id: string;
  user_id: string;
  parent_id: string | null;
  age: number;
  grade: Grade;
  preferred_language: Language;
  board: string;
  learning_speed: number;
  confidence_score: number;
  accuracy_rate: number;
  current_streak: number;
  longest_streak: number;
  total_points: number;
  total_sessions: number;
  total_time_spent: number;
  total_questions: number;
  correct_answers: number;
  current_topic: TopicSummary | null;
  strengths: TopicSummary[];
  weaknesses: TopicSummary[];
  progress_summary: ProgressSummary | null;
  placement_complete: boolean;
  last_session_at: string | null;
}

// =============================================================================
// Session & Messages
// =============================================================================
export type SessionType = "tutoring" | "practice" | "assessment";
export type MessageRole = "student" | "teacher" | "system";
export type ContentType = "text" | "hint" | "solution" | "feedback" | "encouragement";
export type SessionStatus = "active" | "completed" | "abandoned";

export interface Session {
  id: string;
  student_id: string;
  session_type: SessionType;
  language: Language;
  status: SessionStatus;
  started_at: string;
  ended_at?: string;
  ws_endpoint?: string;
}

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  content_type: ContentType;
  hint_level?: number;
  is_correct?: boolean;
  math_expression?: string;
  created_at: string;
}

// =============================================================================
// Practice
// =============================================================================
export type Difficulty = "easy" | "medium" | "hard" | "adaptive";

export interface PracticeQuestion {
  question_number: number;
  question_text: string;
  question_latex?: string;
  difficulty: number;
  hints: string[];
}

export interface PracticeSet {
  id: string;
  title: string;
  topic: TopicSummary | null;
  difficulty: Difficulty;
  question_count: number;
  questions: PracticeQuestion[];
  status: "pending" | "in_progress" | "completed";
}

// =============================================================================
// Progress
// =============================================================================
export interface DailyActivity {
  date: string;
  questions: number;
  accuracy: number;
  time_spent: number;
}

export interface WeakArea {
  topic_id: string;
  name: string;
  mastery_score: number;
  questions_attempted: number;
  accuracy: number;
  common_error?: string;
}

export interface ProgressData {
  student_id: string;
  grade: string;
  grade_progress_pct: number;
  learning_velocity: number;
  weekly_activity: DailyActivity[];
  weak_areas: WeakArea[];
  strong_areas: TopicSummary[];
  confidence_trend: number[];
  updated_at: string;
}

// =============================================================================
// Achievement
// =============================================================================
export interface Achievement {
  type: string;
  title: string;
  description: string;
  earned_at: string;
  icon_url?: string;
}

export interface NextAchievement {
  type: string;
  title: string;
  progress: { current: number; target: number };
}

// =============================================================================
// Voice
// =============================================================================
export type VoiceStyle = "natural" | "gentle" | "excited";

// =============================================================================
// API
// =============================================================================
export interface PaginationMeta {
  next_cursor: string | null;
  has_more: boolean;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: PaginationMeta;
}

export interface ApiError {
  type: string;
  title: string;
  status: number;
  detail: string;
  instance: string;
  errors?: Array<{ field: string; message: string }>;
}
