"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store";
import { cn, gradeDisplay } from "@/lib/utils";

interface StudentData {
  id: string;
  grade: string;
  preferred_language: string;
  accuracy_rate: number;
  current_streak: number;
  longest_streak: number;
  total_points: number;
  total_questions: number;
  correct_answers: number;
  learning_speed: number;
  confidence_score: number;
  total_sessions: number;
  strengths: { name: string; mastery_score: number }[];
  weaknesses: { name: string; mastery_score: number }[];
  progress_summary: {
    topics_mastered: number;
    topics_in_progress: number;
    topics_remaining: number;
    grade_progress_pct: number;
  };
  placement_complete: boolean;
}

export default function DashboardPage() {
  const router = useRouter();
  const { user, isAuthenticated, isLoading } = useAuthStore();
  const [student, setStudent] = useState<StudentData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) { router.push("/login"); return; }
    if (isAuthenticated) loadStudent();
  }, [isAuthenticated, isLoading]);

  const loadStudent = async () => {
    try {
      const token = localStorage.getItem("access_token");
      if (!token) return;
      // Try to load student via user's linked profile
      const res = await fetch("http://localhost:8000/api/v1/students", {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ age: 8, grade: "3", preferred_language: "en" }),
      });
      if (res.ok) {
        const data = await res.json();
        setStudent(data);
      } else if (res.status === 409) {
        // Profile already exists, tried to create again
        // For now use demo data
        setStudent(getDemoStudent());
      }
    } catch {
      setStudent(getDemoStudent());
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="min-h-screen flex items-center justify-center"><div className="text-center"><div className="text-5xl mb-4 animate-bounce">🧮</div><p className="text-gray-500">Loading your math world...</p></div></div>;

  const s = student || getDemoStudent();

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      <header className="bg-white border-b border-gray-100 sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl">🧮</span>
            <div>
              <h1 className="font-heading font-bold text-gray-800 text-lg">Hi, {user?.full_name?.split(" ")[0] || "Student"}! 👋</h1>
              <p className="text-xs text-gray-500">{gradeDisplay(s.grade)} • {s.current_streak}🔥 streak</p>
            </div>
          </div>
          <button onClick={() => { useAuthStore.getState().logout(); router.push("/login"); }} className="btn-ghost text-xs">Logout</button>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-6 space-y-6">
        {/* Progress Card */}
        <div className="card">
          <div className="flex items-center justify-between mb-3">
            <h2 className="font-heading font-bold text-gray-700">📊 Grade Progress</h2>
            <span className="text-sm font-semibold text-primary-600">{Math.round(s.progress_summary.grade_progress_pct * 100)}%</span>
          </div>
          <div className="w-full bg-gray-100 rounded-full h-3 mb-3">
            <div className="bg-gradient-to-r from-primary-500 to-primary-600 h-3 rounded-full transition-all duration-500" style={{ width: `${s.progress_summary.grade_progress_pct * 100}%` }} />
          </div>
          <div className="flex justify-between text-sm text-gray-500">
            <span>⭐ {s.progress_summary.topics_mastered} mastered</span>
            <span>📝 {s.progress_summary.topics_in_progress} learning</span>
            <span>🔒 {s.progress_summary.topics_remaining} remaining</span>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-2 gap-4">
          <button onClick={() => router.push("/chat")} className="card-hover flex flex-col items-center text-center p-6 bg-gradient-to-br from-primary-50 to-white">
            <span className="text-4xl mb-3">📚</span>
            <h3 className="font-heading font-bold text-gray-700">Start Learning</h3>
            <p className="text-sm text-gray-500 mt-1">Ask a math question</p>
          </button>
          <button onClick={() => router.push("/practice")} className="card-hover flex flex-col items-center text-center p-6 bg-gradient-to-br from-warning-50 to-white">
            <span className="text-4xl mb-3">✏️</span>
            <h3 className="font-heading font-bold text-gray-700">Practice Quiz</h3>
            <p className="text-sm text-gray-500 mt-1">Adaptive questions</p>
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-4 gap-3">
          <StatCard value={String(s.total_questions)} label="Questions" />
          <StatCard value={`${Math.round(s.accuracy_rate * 100)}%`} label="Accuracy" color="text-success-600" />
          <StatCard value={String(s.total_points)} label="Points" color="text-warning-600" />
          <StatCard value={String(s.current_streak)} label="Streak 🔥" />
        </div>

        {/* Weak Areas */}
        {s.weaknesses.length > 0 && (
          <div className="card">
            <h2 className="font-heading font-bold text-gray-700 mb-3">📌 Topics to Improve</h2>
            {s.weaknesses.slice(0, 3).map((w, i) => (
              <div key={i} className="flex items-center gap-3 py-1">
                <span>{w.mastery_score < 0.4 ? "🔴" : "🟡"}</span>
                <div className="flex-1"><p className="text-sm font-medium text-gray-700">{w.name}</p></div>
                <span className="text-sm text-gray-500">{Math.round(w.mastery_score * 100)}%</span>
              </div>
            ))}
          </div>
        )}

        {/* Strengths */}
        {s.strengths.length > 0 && (
          <div className="card">
            <h2 className="font-heading font-bold text-gray-700 mb-3">🌟 Strengths</h2>
            {s.strengths.slice(0, 3).map((st, i) => (
              <div key={i} className="flex items-center gap-3 py-1">
                <span>✅</span>
                <div className="flex-1"><p className="text-sm font-medium text-gray-700">{st.name}</p></div>
                <span className="text-sm text-gray-500">{Math.round(st.mastery_score * 100)}%</span>
              </div>
            ))}
          </div>
        )}
      </main>

      {/* Bottom Nav */}
      <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-100">
        <div className="max-w-4xl mx-auto flex justify-around py-2">
          {[
            { icon: "🏠", label: "Home", active: true },
            { icon: "💬", label: "Learn", action: () => router.push("/chat") },
            { icon: "✏️", label: "Practice", action: () => router.push("/practice") },
            { icon: "📊", label: "Progress", action: () => router.push("/progress") },
          ].map((item) => (
            <button key={item.label} onClick={item.action} className={cn("flex flex-col items-center gap-1 px-4 py-1 rounded-xl transition-colors", item.active ? "text-primary-600" : "text-gray-400 hover:text-gray-600")}>
              <span className="text-xl">{item.icon}</span>
              <span className="text-xs font-medium">{item.label}</span>
            </button>
          ))}
        </div>
      </nav>
    </div>
  );
}

function StatCard({ value, label, color = "text-primary-600" }: { value: string; label: string; color?: string }) {
  return <div className="card text-center py-3"><p className={`text-xl font-bold ${color}`}>{value}</p><p className="text-xs text-gray-500">{label}</p></div>;
}

function getDemoStudent(): StudentData {
  return {
    id: "demo", grade: "3", preferred_language: "en", accuracy_rate: 0.76, current_streak: 3, longest_streak: 7, total_points: 850, total_questions: 127, correct_answers: 97, learning_speed: 5.5, confidence_score: 0.68, total_sessions: 12,
    strengths: [
      { name: "Addition (3-digit)", mastery_score: 0.95 },
      { name: "Subtraction (2-digit)", mastery_score: 0.88 },
      { name: "Numbers up to 1000", mastery_score: 0.91 },
    ],
    weaknesses: [
      { name: "Multiplication (6-9)", mastery_score: 0.42 },
      { name: "Division (Basic)", mastery_score: 0.35 },
    ],
    progress_summary: { topics_mastered: 8, topics_in_progress: 4, topics_remaining: 28, grade_progress_pct: 0.25 },
    placement_complete: true,
  };
}
