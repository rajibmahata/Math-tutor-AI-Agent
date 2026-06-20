"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store";
import { cn, gradeDisplay } from "@/lib/utils";

const API = "http://localhost:8000/api";

interface StudentData {
  id: string; grade: string; preferred_language: string; accuracy_rate: number;
  current_streak: number; total_points: number; total_questions: number;
  strengths: { name: string; mastery_score: number }[];
  weaknesses: { name: string; mastery_score: number }[];
  progress_summary: { topics_mastered: number; topics_in_progress: number; topics_remaining: number; grade_progress_pct: number };
}

export default function DashboardPage() {
  const router = useRouter();
  const { user, isAuthenticated, isLoading } = useAuthStore();
  const [student, setStudent] = useState<StudentData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) { router.push("/login"); return; }
    if (user) {
      // Auto-redirect based on role
      if (user.role === "tutor") { router.push("/tutor"); return; }
      if (user.role === "principal") { router.push("/principal"); return; }
      if (user.role === "admin") { router.push("/admin"); return; }
      // Student — try to load profile
      loadStudent();
    }
  }, [isAuthenticated, isLoading, user]);

  const loadStudent = async () => {
    try {
      const token = localStorage.getItem("access_token");
      if (!token) { setLoading(false); return; }
      const res = await fetch(`${API}/students`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ age: 8, grade: "3", preferred_language: "en" }),
      });
      if (res.ok) setStudent(await res.json());
    } catch {} finally { setLoading(false); }
  };

  const logout = () => { useAuthStore.getState().logout(); router.push("/login"); };

  if (loading) return <div className="flex-1 flex items-center justify-center"><div className="text-4xl animate-bounce">🧮</div></div>;

  const s = student || { grade: "3", accuracy_rate: 0.76, current_streak: 3, total_points: 850, total_questions: 127,
    strengths: [{ name: "Addition", mastery_score: 0.95 }, { name: "Subtraction", mastery_score: 0.88 }],
    weaknesses: [{ name: "Multiplication (6-9)", mastery_score: 0.42 }, { name: "Division", mastery_score: 0.35 }],
    progress_summary: { topics_mastered: 8, topics_in_progress: 4, topics_remaining: 28, grade_progress_pct: 0.25 },
  };

  return (
    <div className="flex-1 flex flex-col bg-gray-50">
      <header className="bg-white border-b border-gray-100 flex-shrink-0">
        <div className="px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-xl">🧮</span>
            <div>
              <h1 className="font-heading font-bold text-gray-800 text-sm">Hi, {user?.full_name?.split(" ")[0] || "Student"}!</h1>
              <p className="text-[10px] text-gray-400">{gradeDisplay(s.grade)} · 🔥{s.current_streak}</p>
            </div>
          </div>
          <button onClick={logout} className="text-xs text-gray-400">Logout</button>
        </div>
      </header>

      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
        {/* Progress */}
        <div className="card">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-bold text-gray-700">📊 Progress</span>
            <span className="text-xs font-semibold text-primary-600">{Math.round(s.progress_summary.grade_progress_pct * 100)}%</span>
          </div>
          <div className="w-full bg-gray-100 rounded-full h-2 mb-2">
            <div className="bg-primary-500 h-2 rounded-full" style={{ width: `${s.progress_summary.grade_progress_pct * 100}%` }} />
          </div>
          <div className="flex justify-between text-[10px] text-gray-400">
            <span>⭐{s.progress_summary.topics_mastered}</span>
            <span>📝{s.progress_summary.topics_in_progress}</span>
            <span>🔒{s.progress_summary.topics_remaining}</span>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="grid grid-cols-2 gap-3">
          <button onClick={() => router.push("/chat")} className="card flex flex-col items-center py-4 bg-gradient-to-br from-primary-50">
            <span className="text-2xl mb-1">💬</span>
            <span className="text-xs font-medium text-gray-700">Learn</span>
          </button>
          <button onClick={() => router.push("/practice")} className="card flex flex-col items-center py-4 bg-gradient-to-br from-amber-50">
            <span className="text-2xl mb-1">✏️</span>
            <span className="text-xs font-medium text-gray-700">Practice</span>
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-4 gap-2">
          <MiniStat v={String(s.total_questions)} l="Q's" />
          <MiniStat v={`${Math.round(s.accuracy_rate * 100)}%`} l="Acc" c="text-green-600" />
          <MiniStat v={String(s.total_points)} l="Pts" c="text-amber-600" />
          <MiniStat v={String(s.current_streak)} l="🔥" />
        </div>

        {/* Weaknesses */}
        <div className="card">
          <h2 className="text-sm font-bold text-gray-700 mb-2">📌 Improve</h2>
          {s.weaknesses.slice(0, 3).map((w, i) => (
            <div key={i} className="flex items-center gap-2 py-1">
              <span>{w.mastery_score < 0.4 ? "🔴" : "🟡"}</span>
              <span className="text-xs text-gray-600 flex-1">{w.name}</span>
              <span className="text-[10px] text-gray-400">{Math.round(w.mastery_score * 100)}%</span>
            </div>
          ))}
        </div>
      </div>

      {/* Bottom Nav */}
      <nav className="bg-white border-t border-gray-100 flex-shrink-0 px-4 py-2 flex justify-around">
        {[
          { icon: "🏠", label: "Home", active: true },
          { icon: "💬", label: "Chat", action: () => router.push("/chat") },
          { icon: "✏️", label: "Quiz", action: () => router.push("/practice") },
          { icon: "📊", label: "Stats", action: () => router.push("/progress") },
        ].map((n) => (
          <button key={n.label} onClick={n.action} className={cn("flex flex-col items-center gap-0.5", n.active ? "text-primary-600" : "text-gray-400")}>
            <span className="text-lg">{n.icon}</span>
            <span className="text-[10px]">{n.label}</span>
          </button>
        ))}
      </nav>
    </div>
  );
}

function MiniStat({ v, l, c = "text-primary-600" }: { v: string; l: string; c?: string }) {
  return <div className="card text-center py-2"><p className={`text-sm font-bold ${c}`}>{v}</p><p className="text-[9px] text-gray-400">{l}</p></div>;
}
