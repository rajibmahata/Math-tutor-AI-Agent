"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store";
import { cn, gradeDisplay } from "@/lib/utils";

const API = "http://localhost:8000/api/v1";

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

// Smart question sets per grade
const GRADE_QUESTIONS: Record<string, { topic: string; questions: string[] }> = {
  N: { topic: "Counting & Shapes", questions: ["How many fingers on one hand?", "What shape is a ball?", "Count: 1, 2, 3, __", "Which is bigger, an elephant or a cat?"] },
  KG: { topic: "Numbers & Patterns", questions: ["What comes after 5?", "How many sides does a square have?", "What is 2 + 1?", "Which number is bigger: 7 or 3?"] },
  "1": { topic: "Addition Basics", questions: ["What is 3 + 4?", "What is 7 + 2?", "What is 5 + 5?", "What is 8 + 1?"] },
  "2": { topic: "Addition & Subtraction", questions: ["What is 15 + 8?", "What is 23 - 7?", "What is 12 + 9?", "What is 30 - 14?"] },
  "3": { topic: "Multiplication Tables", questions: ["What is 6 × 4?", "What is 7 × 3?", "What is 8 × 5?", "What is 9 × 2?"] },
  "4": { topic: "Multiplication & Division", questions: ["What is 12 × 5?", "What is 84 ÷ 7?", "What is 15 × 6?", "What is 96 ÷ 8?"] },
  "5": { topic: "Fractions & Decimals", questions: ["What is 1/2 + 1/4?", "What is 0.5 + 0.25?", "What is 3/4 of 20?", "Convert 0.75 to a fraction"] },
  "6": { topic: "Integers & Algebra", questions: ["What is -5 + 12?", "Solve: x + 7 = 15", "What is (-3) × 4?", "What is 3x when x = 5?"] },
  "7": { topic: "Equations & Geometry", questions: ["Solve: 2x - 3 = 11", "What is the area of a square with side 5?", "What is 3/5 + 2/5?", "Find the perimeter of a rectangle 4 by 6"] },
  "8": { topic: "Linear Equations", questions: ["Solve: 3x + 4 = 2x + 9", "What is (x+2)(x+3)?", "Find the cube of 4", "What is the square root of 144?"] },
  "9": { topic: "Quadratic & Trigonometry", questions: ["Solve: x² - 5x + 6 = 0", "What is sin 30°?", "Factor: x² - 9", "What is the area of a circle with radius 7?"] },
  "10": { topic: "Advanced Math", questions: ["Solve: x² + 3x - 10 = 0", "What is tan 45°?", "Find the sum of first 10 natural numbers", "What is the probability of getting heads twice?"] },
};

const LANG_INTROS: Record<string, Record<string, string>> = {
  en: {
    intro: "Based on your Grade {grade} level, I've prepared a {topic} practice set! Let's start with this question:",
    action: "Start Learning",
  },
  hi: {
    intro: "आपकी कक्षा {grade} के आधार पर, मैंने {topic} अभ्यास सेट तैयार किया है! आइए इस सवाल से शुरू करें:",
    action: "सीखना शुरू करें",
  },
  bn: {
    intro: "তোমার {grade} শ্রেণির উপর ভিত্তি করে, আমি {topic} অনুশীলন সেট তৈরি করেছি! চলো এই প্রশ্ন দিয়ে শুরু করি:",
    action: "শেখা শুরু করো",
  },
};

export default function DashboardPage() {
  const router = useRouter();
  const { user, isAuthenticated, isLoading } = useAuthStore();
  const [student, setStudent] = useState<StudentData | null>(null);
  const [loading, setLoading] = useState(true);
  const [startQuestion, setStartQuestion] = useState<string | null>(null);
  const [showQuestion, setShowQuestion] = useState(false);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) { router.push("/login"); return; }
    if (isAuthenticated) loadStudent();
  }, [isAuthenticated, isLoading]);

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
      else if (res.status === 409) setStudent(getDemoStudent());
    } catch { setStudent(getDemoStudent()); }
    finally { setLoading(false); }
  };

  const handleStartLearning = async () => {
    const grade = student?.grade || "3";
    const gq = GRADE_QUESTIONS[grade] || GRADE_QUESTIONS["3"];
    const lang = (student?.preferred_language || "en") as string;
    const intros = LANG_INTROS[lang] || LANG_INTROS.en;

    // Pick the first question — agent would normally select based on weaknesses
    const question = gq.questions[0];
    const intro = intros.intro.replace("{grade}", grade).replace("{topic}", gq.topic);

    setStartQuestion(`${intro}\n\n**${question}**`);
    setShowQuestion(true);

    // Auto-navigate to chat with the question after a brief delay
    setTimeout(() => {
      localStorage.setItem("pending_question", question);
      router.push("/chat");
    }, 2000);
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("student_name");
    router.push("/login");
  };

  if (loading) return <div className="min-h-screen flex items-center justify-center"><div className="text-center"><div className="text-5xl mb-4 animate-bounce">🧮</div><p className="text-gray-500">Loading your math world...</p></div></div>;

  const s = student || getDemoStudent();
  const lang = s.preferred_language || "en";
  const intros = LANG_INTROS[lang] || LANG_INTROS.en;
  const gq = GRADE_QUESTIONS[s.grade] || GRADE_QUESTIONS["3"];

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      <header className="bg-white border-b border-gray-100 sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl">🧮</span>
            <div>
              <h1 className="font-heading font-bold text-gray-800 text-lg">Hi, {user?.full_name?.split(" ")[0] || "Student"}! 👋</h1>
              <p className="text-xs text-gray-500">{gradeDisplay(s.grade)} • {s.current_streak}🔥 streak • ⭐ {s.total_points} pts</p>
            </div>
          </div>
          <button onClick={logout} className="btn-ghost text-xs text-error-500">Logout</button>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-6 space-y-6">
        {/* Agent-picked question set */}
        {showQuestion && startQuestion && (
          <div className="card bg-gradient-to-r from-primary-50 to-white border-primary-200 animate-bounce-in">
            <div className="flex items-start gap-3">
              <span className="text-3xl">🧑‍🏫</span>
              <div>
                <p className="text-sm text-primary-700 font-medium mb-2 whitespace-pre-wrap">{startQuestion}</p>
                <div className="flex gap-2 mt-3">
                  <button onClick={() => { localStorage.setItem("pending_question", gq.questions[0]); router.push("/chat"); }} className="btn-primary text-sm">
                    {intros.action} →
                  </button>
                  <button onClick={() => setShowQuestion(false)} className="btn-ghost text-xs">Maybe later</button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Progress Card */}
        <div className="card">
          <div className="flex items-center justify-between mb-3">
            <h2 className="font-heading font-bold text-gray-700">📊 Grade {s.grade} Progress</h2>
            <span className="text-sm font-semibold text-primary-600">{Math.round(s.progress_summary.grade_progress_pct * 100)}%</span>
          </div>
          <div className="w-full bg-gray-100 rounded-full h-3 mb-3">
            <div className="bg-gradient-to-r from-primary-500 to-primary-600 h-3 rounded-full transition-all duration-500" style={{ width: `${s.progress_summary.grade_progress_pct * 100}%` }} />
          </div>
          <div className="flex justify-between text-sm text-gray-500">
            <span>⭐ {s.progress_summary.topics_mastered} mastered</span>
            <span>📝 {s.progress_summary.topics_in_progress} learning</span>
            <span>🔒 {s.progress_summary.topics_remaining} to go</span>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-2 gap-4">
          <button onClick={handleStartLearning} className="card-hover flex flex-col items-center text-center p-6 bg-gradient-to-br from-primary-50 to-white">
            <span className="text-4xl mb-3">📚</span>
            <h3 className="font-heading font-bold text-gray-700">{intros.action}</h3>
            <p className="text-sm text-gray-500 mt-1">{gq.topic} — {gq.questions.length} questions ready</p>
          </button>
          <button onClick={() => router.push("/practice")} className="card-hover flex flex-col items-center text-center p-6 bg-gradient-to-br from-warning-50 to-white">
            <span className="text-4xl mb-3">✏️</span>
            <h3 className="font-heading font-bold text-gray-700">Practice Quiz</h3>
            <p className="text-sm text-gray-500 mt-1">AI-generated adaptive quiz</p>
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-4 gap-3">
          <StatCard value={String(s.total_questions)} label="Answered" />
          <StatCard value={`${Math.round(s.accuracy_rate * 100)}%`} label="Accuracy" color="text-success-600" />
          <StatCard value={String(s.total_points)} label="Points" color="text-warning-600" />
          <StatCard value={String(s.current_streak)} label="Streak" />
        </div>

        {/* Weak Areas */}
        {s.weaknesses.length > 0 && (
          <div className="card">
            <h2 className="font-heading font-bold text-gray-700 mb-3">📌 Improve</h2>
            {s.weaknesses.slice(0, 3).map((w, i) => (
              <div key={i} className="flex items-center gap-3 py-1">
                <span>{w.mastery_score < 0.4 ? "🔴" : "🟡"}</span>
                <span className="text-sm text-gray-700 flex-1">{w.name}</span>
                <span className="text-xs text-gray-500">{Math.round(w.mastery_score * 100)}%</span>
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
                <span className="text-sm text-gray-700 flex-1">{st.name}</span>
                <span className="text-xs text-gray-500">{Math.round(st.mastery_score * 100)}%</span>
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
            { icon: "💬", label: "Learn", action: () => handleStartLearning() },
            { icon: "✏️", label: "Practice", action: () => router.push("/practice") },
            { icon: "📊", label: "Progress", action: () => router.push("/progress") },
          ].map((item) => (
            <button key={item.label} onClick={item.action} className={cn("flex flex-col items-center gap-1 px-4 py-1 rounded-xl transition-colors", item.active ? "text-primary-600" : "text-gray-400 hover:text-gray-600")}>
              <span className="text-xl">{item.icon}</span>
              <span className="text-[10px] font-medium">{item.label}</span>
            </button>
          ))}
        </div>
      </nav>
    </div>
  );
}

function StatCard({ value, label, color = "text-primary-600" }: { value: string; label: string; color?: string }) {
  return <div className="card text-center py-3"><p className={`text-lg font-bold ${color}`}>{value}</p><p className="text-[10px] text-gray-500">{label}</p></div>;
}

function getDemoStudent(): StudentData {
  return {
    id: "demo", grade: "3", preferred_language: "en", accuracy_rate: 0.76, current_streak: 3, longest_streak: 7, total_points: 850, total_questions: 127, correct_answers: 97, learning_speed: 5.5, confidence_score: 0.68, total_sessions: 12,
    strengths: [{ name: "Addition (3-digit)", mastery_score: 0.95 }, { name: "Subtraction (2-digit)", mastery_score: 0.88 }, { name: "Numbers up to 1000", mastery_score: 0.91 }],
    weaknesses: [{ name: "Multiplication (6-9)", mastery_score: 0.42 }, { name: "Division (Basic)", mastery_score: 0.35 }],
    progress_summary: { topics_mastered: 8, topics_in_progress: 4, topics_remaining: 28, grade_progress_pct: 0.25 },
    placement_complete: true,
  };
}
