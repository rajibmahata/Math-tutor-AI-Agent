"use client";

import { useRouter } from "next/navigation";

export default function ParentDashboardPage() {
  const router = useRouter();

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-100">
        <div className="max-w-4xl mx-auto px-4 py-3 flex items-center gap-3">
          <button onClick={() => router.push("/login")} className="btn-ghost text-sm">
            ← Back
          </button>
          <h1 className="font-heading font-bold text-gray-800">👨‍👩‍👧 Parent Dashboard</h1>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-8 space-y-6">
        {/* Weekly Stats */}
        <div className="card">
          <h2 className="font-heading font-bold text-gray-700 mb-4">📊 This Week (Riya • Grade 3)</h2>
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center">
              <p className="text-3xl font-bold text-primary-600">5</p>
              <p className="text-xs text-gray-500">Sessions</p>
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold text-primary-600">85</p>
              <p className="text-xs text-gray-500">Questions</p>
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold text-success-600">78%</p>
              <p className="text-xs text-gray-500">Accuracy</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-700">145 min</p>
              <p className="text-xs text-gray-500">Time Spent</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-700">35%</p>
              <p className="text-xs text-gray-500">Grade Progress</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-warning-600">5 🔥</p>
              <p className="text-xs text-gray-500">Day Streak</p>
            </div>
          </div>
        </div>

        {/* Strengths & Weaknesses */}
        <div className="grid grid-cols-2 gap-4">
          <div className="card">
            <h3 className="font-heading font-bold text-success-700 mb-3">🌟 Strengths</h3>
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-sm">
                <span>✅</span>
                <span className="text-gray-700">Addition (3-digit)</span>
                <span className="ml-auto text-success-600 font-medium">95%</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <span>✅</span>
                <span className="text-gray-700">Subtraction (2-digit)</span>
                <span className="ml-auto text-success-600 font-medium">92%</span>
              </div>
            </div>
          </div>

          <div className="card">
            <h3 className="font-heading font-bold text-error-700 mb-3">⚠️ Needs Attention</h3>
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-sm">
                <span>🔴</span>
                <span className="text-gray-700">Division (Basic)</span>
                <span className="ml-auto text-error-600 font-medium">38%</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <span>🟡</span>
                <span className="text-gray-700">Multiplication (6-9)</span>
                <span className="ml-auto text-warning-600 font-medium">45%</span>
              </div>
            </div>
          </div>
        </div>

        {/* Recommendations */}
        <div className="card">
          <h3 className="font-heading font-bold text-gray-700 mb-3">💡 Recommendations</h3>
          <ul className="space-y-2">
            <li className="flex items-start gap-2 text-sm text-gray-600">
              <span>•</span>
              Practice division for 15 minutes daily — use real-life sharing examples
            </li>
            <li className="flex items-start gap-2 text-sm text-gray-600">
              <span>•</span>
              Try skip-counting games to strengthen multiplication tables
            </li>
            <li className="flex items-start gap-2 text-sm text-gray-600">
              <span>•</span>
              Ask your child to explain a math concept — teaching reinforces learning
            </li>
          </ul>
        </div>

        {/* Reports */}
        <div className="card">
          <h3 className="font-heading font-bold text-gray-700 mb-3">📄 Weekly Reports</h3>
          <div className="space-y-2">
            {[
              { date: "Jun 19, 2026", type: "Weekly", unread: true },
              { date: "Jun 12, 2026", type: "Weekly", unread: false },
              { date: "Jun 05, 2026", type: "Weekly", unread: false },
            ].map((r, i) => (
              <div
                key={i}
                className="flex items-center justify-between py-2 border-b border-gray-50 last:border-0"
              >
                <div className="flex items-center gap-2">
                  {r.unread && <span className="w-2 h-2 bg-primary-500 rounded-full" />}
                  <span className="text-sm text-gray-700">{r.date}</span>
                  <span className="text-xs text-gray-400">({r.type})</span>
                </div>
                <button className="text-sm text-primary-600 font-medium">View →</button>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
