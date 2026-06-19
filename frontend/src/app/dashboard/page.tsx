"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store";
import { apiRequest, cn } from "@/lib/utils";
import type { Student, Achievement } from "@/types";

export default function DashboardPage() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuthStore();
  const [student, setStudent] = useState<Student | null>(null);
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated && !loading) {
      router.push("/login");
      return;
    }
    loadDashboard();
  }, [isAuthenticated]);

  const loadDashboard = async () => {
    try {
      const data = await apiRequest("/students/me"); // stub — would need actual ID
      if (data) setStudent(data);
    } catch {}

    try {
      const ach = await apiRequest("/achievements/me");
      if (ach?.achievements) setAchievements(ach.achievements);
    } catch {}

    setLoading(false);
  };

  if (loading && !student) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="text-5xl mb-4 animate-bounce">🧮</div>
          <p className="text-gray-500">Loading your math world...</p>
        </div>
      </div>
    );
  }

  // Demo data for UI preview
  const demoStudent: Student = student || {
    id: "demo",
    user_id: "demo",
    age: 8,
    grade: "3",
    preferred_language: "hi",
    board: "ncert",
    learning_speed: 5.5,
    confidence_score: 0.72,
    accuracy_rate: 0.78,
    current_streak: 5,
    longest_streak: 12,
    total_points: 1250,
    total_sessions: 34,
    total_time_spent: 20400,
    total_questions: 342,
    correct_answers: 267,
    current_topic: null,
    strengths: [
      { topic_id: "1", name: "Addition (3-digit)", mastery_score: 0.95, questions_attempted: 25, accuracy_rate: 0.96 },
      { topic_id: "2", name: "Subtraction (2-digit)", mastery_score: 0.92, questions_attempted: 30, accuracy_rate: 0.90 },
      { topic_id: "3", name: "Numbers up to 1000", mastery_score: 0.88, questions_attempted: 20, accuracy_rate: 0.85 },
    ],
    weaknesses: [
      { topic_id: "4", name: "Multiplication (6-9)", mastery_score: 0.45, questions_attempted: 28, accuracy_rate: 0.46 },
      { topic_id: "5", name: "Division (Basic)", mastery_score: 0.38, questions_attempted: 15, accuracy_rate: 0.40 },
    ],
    progress_summary: {
      topics_mastered: 12,
      topics_in_progress: 5,
      topics_remaining: 28,
      grade_progress_pct: 0.35,
    },
    placement_complete: true,
    last_session_at: new Date().toISOString(),
  };

  const s = demoStudent;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-100 sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl">🧮</span>
            <div>
              <h1 className="font-heading font-bold text-gray-800 text-lg">
                Hi, {user?.full_name?.split(" ")[0] || "Student"}!
              </h1>
              <p className="text-xs text-gray-500">
                Grade {s.grade} • {s.current_streak}🔥 streak
              </p>
            </div>
          </div>
          <button className="btn-ghost text-sm">🌐 EN</button>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-6 space-y-6">
        {/* Progress Card */}
        <div className="card">
          <div className="flex items-center justify-between mb-3">
            <h2 className="font-heading font-bold text-gray-700">📊 Your Progress</h2>
            <span className="text-sm font-semibold text-primary-600">
              {Math.round(s.progress_summary!.grade_progress_pct * 100)}%
            </span>
          </div>
          <div className="w-full bg-gray-100 rounded-full h-3 mb-3">
            <div
              className="bg-gradient-to-r from-primary-500 to-primary-600 h-3 rounded-full transition-all duration-500"
              style={{ width: `${s.progress_summary!.grade_progress_pct * 100}%` }}
            />
          </div>
          <div className="flex justify-between text-sm text-gray-500">
            <span>⭐ {s.progress_summary!.topics_mastered} mastered</span>
            <span>📝 {s.progress_summary!.topics_in_progress} learning</span>
            <span>🔒 {s.progress_summary!.topics_remaining} remaining</span>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-2 gap-4">
          <button
            onClick={() => router.push("/chat")}
            className="card-hover flex flex-col items-center text-center p-6 bg-gradient-to-br from-primary-50 to-white"
          >
            <span className="text-4xl mb-3">📚</span>
            <h3 className="font-heading font-bold text-gray-700">Continue Learning</h3>
            <p className="text-sm text-gray-500 mt-1">
              {s.weaknesses?.[0]?.name || "Start a new topic"}
            </p>
          </button>

          <button
            onClick={() => router.push("/practice")}
            className="card-hover flex flex-col items-center text-center p-6 bg-gradient-to-br from-warning-50 to-white"
          >
            <span className="text-4xl mb-3">✏️</span>
            <h3 className="font-heading font-bold text-gray-700">Practice Quiz</h3>
            <p className="text-sm text-gray-500 mt-1">Adaptive questions for you</p>
          </button>
        </div>

        {/* Weak Areas */}
        <div className="card">
          <h2 className="font-heading font-bold text-gray-700 mb-3">📌 Topics to Improve</h2>
          <div className="space-y-3">
            {s.weaknesses?.map((w) => (
              <div key={w.topic_id} className="flex items-center gap-3">
                <span className="text-red-500">🔴</span>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-700">{w.name}</p>
                  <div className="w-full bg-gray-100 rounded-full h-2 mt-1">
                    <div
                      className="bg-error-500 h-2 rounded-full"
                      style={{ width: `${w.mastery_score * 100}%` }}
                    />
                  </div>
                </div>
                <span className="text-sm text-gray-500">{Math.round(w.mastery_score * 100)}%</span>
              </div>
            )) || <p className="text-sm text-gray-400">No weak areas — great job!</p>}
          </div>
        </div>

        {/* Strengths */}
        <div className="card">
          <h2 className="font-heading font-bold text-gray-700 mb-3">🌟 Your Strengths</h2>
          <div className="space-y-3">
            {s.strengths?.map((st) => (
              <div key={st.topic_id} className="flex items-center gap-3">
                <span className="text-success-500">✅</span>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-700">{st.name}</p>
                  <div className="w-full bg-gray-100 rounded-full h-2 mt-1">
                    <div
                      className="bg-success-500 h-2 rounded-full"
                      style={{ width: `${st.mastery_score * 100}%` }}
                    />
                  </div>
                </div>
                <span className="text-sm text-gray-500">{Math.round(st.mastery_score * 100)}%</span>
              </div>
            ))}
          </div>
        </div>

        {/* Stats Row */}
        <div className="grid grid-cols-3 gap-3">
          <div className="card text-center py-3">
            <p className="text-2xl font-bold text-primary-600">{s.total_questions}</p>
            <p className="text-xs text-gray-500">Questions</p>
          </div>
          <div className="card text-center py-3">
            <p className="text-2xl font-bold text-success-600">{Math.round(s.accuracy_rate * 100)}%</p>
            <p className="text-xs text-gray-500">Accuracy</p>
          </div>
          <div className="card text-center py-3">
            <p className="text-2xl font-bold text-warning-600">{s.total_points}</p>
            <p className="text-xs text-gray-500">Points</p>
          </div>
        </div>

        {/* Achievements */}
        {achievements.length > 0 && (
          <div className="card">
            <h2 className="font-heading font-bold text-gray-700 mb-3">🏆 Achievements</h2>
            <div className="flex flex-wrap gap-2">
              {achievements.map((a) => (
                <span
                  key={a.type}
                  className="bg-primary-50 text-primary-700 px-3 py-1.5 rounded-full text-sm font-medium"
                >
                  {a.title}
                </span>
              ))}
            </div>
          </div>
        )}
      </main>

      {/* Bottom Navigation */}
      <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-100 safe-area-bottom">
        <div className="max-w-4xl mx-auto flex justify-around py-2">
          <NavItem icon="🏠" label="Home" active />
          <NavItem icon="💬" label="Learn" onClick={() => router.push("/chat")} />
          <NavItem icon="✏️" label="Practice" onClick={() => router.push("/practice")} />
          <NavItem icon="📊" label="Progress" />
        </div>
      </nav>
    </div>
  );
}

function NavItem({
  icon,
  label,
  active,
  onClick,
}: {
  icon: string;
  label: string;
  active?: boolean;
  onClick?: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={cn(
        "flex flex-col items-center gap-1 px-4 py-1 rounded-xl transition-colors",
        active ? "text-primary-600" : "text-gray-400 hover:text-gray-600"
      )}
    >
      <span className="text-xl">{icon}</span>
      <span className="text-xs font-medium">{label}</span>
    </button>
  );
}
