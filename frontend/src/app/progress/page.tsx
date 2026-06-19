"use client";

import { useRouter } from "next/navigation";

export default function ProgressPage() {
  const router = useRouter();

  const weeklyData = [
    { day: "Mon", questions: 24, accuracy: 75 },
    { day: "Tue", questions: 18, accuracy: 83 },
    { day: "Wed", questions: 30, accuracy: 70 },
    { day: "Thu", questions: 22, accuracy: 81 },
    { day: "Fri", questions: 35, accuracy: 77 },
    { day: "Sat", questions: 15, accuracy: 86 },
    { day: "Sun", questions: 8, accuracy: 88 },
  ];

  const maxQuestions = Math.max(...weeklyData.map((d) => d.questions));

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-100">
        <div className="max-w-4xl mx-auto px-4 py-3 flex items-center gap-3">
          <button onClick={() => router.push("/dashboard")} className="btn-ghost text-sm">
            ← Back
          </button>
          <h1 className="font-heading font-bold text-gray-800">📊 My Progress</h1>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-8 space-y-6">
        {/* Grade Progress */}
        <div className="card">
          <div className="flex items-center justify-between mb-3">
            <h2 className="font-heading font-bold text-gray-700">Grade 3 Math Progress</h2>
            <span className="text-sm font-semibold text-primary-600">35%</span>
          </div>
          <div className="w-full bg-gray-100 rounded-full h-3 mb-2">
            <div
              className="bg-gradient-to-r from-primary-500 to-primary-600 h-3 rounded-full"
              style={{ width: "35%" }}
            />
          </div>
          <div className="flex justify-between text-sm text-gray-500">
            <span>⭐ 12 Mastered</span>
            <span>📝 5 Learning</span>
            <span>🔒 28 Remaining</span>
          </div>
        </div>

        {/* Weekly Activity Bar Chart */}
        <div className="card">
          <h2 className="font-heading font-bold text-gray-700 mb-4">📈 Weekly Activity</h2>
          <div className="flex items-end justify-between gap-2 h-32">
            {weeklyData.map((d) => (
              <div key={d.day} className="flex flex-col items-center gap-1 flex-1">
                <span className="text-xs text-gray-400">{d.accuracy}%</span>
                <div
                  className="w-full bg-primary-400 rounded-t-lg transition-all hover:bg-primary-500 min-h-[4px]"
                  style={{ height: `${(d.questions / maxQuestions) * 100}%` }}
                />
                <span className="text-xs text-gray-500">{d.day}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Topic Mastery Map */}
        <div className="card">
          <h2 className="font-heading font-bold text-gray-700 mb-4">🧠 Topic Mastery</h2>

          <div className="space-y-4">
            <CategorySection
              name="Arithmetic (अंकगणित)"
              topics={[
                { name: "Addition (3-digit)", mastery: 0.95, status: "mastered" },
                { name: "Subtraction (2-digit)", mastery: 0.92, status: "mastered" },
                { name: "Multiplication (1-5)", mastery: 0.78, status: "learning" },
                { name: "Multiplication (6-9)", mastery: 0.45, status: "weak" },
                { name: "Division (Basic)", mastery: 0.38, status: "weak" },
              ]}
            />

            <CategorySection
              name="Number Sense (संख्या ज्ञान)"
              topics={[
                { name: "Place Value (up to 1000)", mastery: 0.90, status: "mastered" },
                { name: "Roman Numerals", mastery: 0.55, status: "learning" },
                { name: "Odd and Even Numbers", mastery: 0.88, status: "mastered" },
              ]}
            />

            <CategorySection
              name="Measurement (मापन)"
              topics={[
                { name: "Length (m, cm)", mastery: 0.82, status: "learning" },
                { name: "Weight (kg, g)", mastery: 0.70, status: "learning" },
                { name: "Money", mastery: 0.85, status: "mastered" },
              ]}
            />
          </div>
        </div>

        {/* Confidence Trend */}
        <div className="card">
          <h2 className="font-heading font-bold text-gray-700 mb-4">🎯 Confidence Trend</h2>
          <div className="flex items-end justify-between gap-1 h-24">
            {[0.5, 0.55, 0.58, 0.62, 0.65, 0.68, 0.72].map((val, i) => (
              <div key={i} className="flex flex-col items-center gap-1 flex-1">
                <div
                  className="w-full bg-success-400 rounded-t transition-all min-h-[4px]"
                  style={{ height: `${val * 100}%` }}
                />
                <span className="text-[10px] text-gray-400">W{i + 1}</span>
              </div>
            ))}
          </div>
          <p className="text-center text-sm text-success-600 mt-3">
            ↑ Confidence rising — from 0.50 to 0.72
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-4 gap-3">
          <StatCard value="342" label="Questions" />
          <StatCard value="78%" label="Accuracy" color="text-success-600" />
          <StatCard value="1,250" label="Points" color="text-warning-600" />
          <StatCard value="12 🔥" label="Best Streak" />
        </div>
      </main>
    </div>
  );
}

function CategorySection({
  name,
  topics,
}: {
  name: string;
  topics: { name: string; mastery: number; status: "mastered" | "learning" | "weak" }[];
}) {
  const statusIcon = {
    mastered: "✅",
    learning: "📝",
    weak: "🔴",
  };
  const barColor = {
    mastered: "bg-success-500",
    learning: "bg-primary-400",
    weak: "bg-error-400",
  };

  return (
    <div>
      <h3 className="text-sm font-semibold text-gray-600 mb-2">{name}</h3>
      <div className="space-y-2">
        {topics.map((t) => (
          <div key={t.name} className="flex items-center gap-2">
            <span className="text-sm">{statusIcon[t.status]}</span>
            <span className="text-sm text-gray-700 flex-1">{t.name}</span>
            <div className="w-24 bg-gray-100 rounded-full h-2">
              <div
                className={`h-2 rounded-full ${barColor[t.status]}`}
                style={{ width: `${t.mastery * 100}%` }}
              />
            </div>
            <span className="text-xs text-gray-500 w-10 text-right">
              {Math.round(t.mastery * 100)}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

function StatCard({
  value,
  label,
  color = "text-primary-600",
}: {
  value: string;
  label: string;
  color?: string;
}) {
  return (
    <div className="card text-center py-3">
      <p className={`text-xl font-bold ${color}`}>{value}</p>
      <p className="text-xs text-gray-500">{label}</p>
    </div>
  );
}
