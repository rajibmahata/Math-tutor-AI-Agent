"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function TutorDashboardPage() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState("overview");

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-teal-600 text-white">
        <div className="max-w-5xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl">👨‍🏫</span>
            <div>
              <h1 className="font-heading font-bold text-lg">Tutor Portal</h1>
              <p className="text-teal-100 text-xs">VidyaMitra v2.0</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-sm">⭐ 4.7 · 24 Students</span>
            <button onClick={() => router.push("/login")} className="text-teal-200 text-sm hover:text-white">Logout</button>
          </div>
        </div>
        {/* Tabs */}
        <div className="max-w-5xl mx-auto px-4 flex gap-1 pb-0">
          {[
            { key: "overview", label: "📊 Overview" },
            { key: "reviews", label: "📚 Content Review" },
            { key: "students", label: "👩‍🎓 Students" },
            { key: "feedback", label: "💬 Feedback" },
          ].map((t) => (
            <button
              key={t.key}
              onClick={() => setActiveTab(t.key)}
              className={`px-4 py-2 text-sm rounded-t-lg transition-colors ${
                activeTab === t.key ? "bg-white text-teal-700 font-medium" : "text-teal-100 hover:bg-teal-500"
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>
      </header>

      {/* Content */}
      <main className="max-w-5xl mx-auto px-4 py-6">
        {activeTab === "overview" && (
          <div className="space-y-6">
            {/* Stats */}
            <div className="grid grid-cols-4 gap-4">
              <StatCard value="24" label="Students" color="text-teal-600" />
              <StatCard value="18" label="Active" color="text-teal-600" />
              <StatCard value="5" label="Reviews Pending" color="text-amber-600" />
              <StatCard value="12" label="Assessments" color="text-teal-600" />
            </div>

            {/* Content Review Queue */}
            <div className="card">
              <h2 className="font-heading font-bold text-gray-700 mb-4">📚 Content to Review</h2>
              <div className="space-y-3">
                {[
                  { title: "Introduction to Fractions", grade: "3", lang: "Hindi", date: "Jun 19" },
                  { title: "Multiplication Word Problems", grade: "4", lang: "English", date: "Jun 18" },
                  { title: "Basic Division Concepts", grade: "3", lang: "Bengali", date: "Jun 17" },
                ].map((item, i) => (
                  <div key={i} className="flex items-center justify-between p-3 bg-gray-50 rounded-xl">
                    <div>
                      <p className="font-medium text-gray-700">{item.title}</p>
                      <p className="text-xs text-gray-400">Grade {item.grade} · {item.lang} · {item.date}</p>
                    </div>
                    <div className="flex gap-2">
                      <button className="bg-teal-600 text-white px-3 py-1 rounded-lg text-xs">Approve</button>
                      <button className="bg-gray-200 text-gray-600 px-3 py-1 rounded-lg text-xs">Modify</button>
                      <button className="bg-red-100 text-red-600 px-3 py-1 rounded-lg text-xs">Reject</button>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Student Performance */}
            <div className="card">
              <h2 className="font-heading font-bold text-gray-700 mb-4">👩‍🎓 Student Performance</h2>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b text-left text-gray-500">
                      <th className="pb-2">Name</th><th className="pb-2">Grade</th><th className="pb-2">Accuracy</th><th className="pb-2">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {[
                      { name: "Riya", grade: "3", accuracy: "78%", trend: "⬆️ +3%" },
                      { name: "Arjun", grade: "5", accuracy: "65%", trend: "⬇️ -2%" },
                      { name: "Priya", grade: "2", accuracy: "92%", trend: "⬆️ +5%" },
                    ].map((s, i) => (
                      <tr key={i} className="border-b last:border-0">
                        <td className="py-2">{s.name}</td>
                        <td className="py-2">Math Gr.{s.grade}</td>
                        <td className="py-2">{s.accuracy}</td>
                        <td className="py-2">{s.trend}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {activeTab === "reviews" && (
          <div className="card text-center py-12">
            <div className="text-5xl mb-4">📚</div>
            <h2 className="text-xl font-heading font-bold text-gray-700">Content Review Queue</h2>
            <p className="text-gray-500 mt-2">5 lessons pending review. AI-generated content needs your validation.</p>
          </div>
        )}

        {activeTab === "students" && (
          <div className="card text-center py-12">
            <div className="text-5xl mb-4">👩‍🎓</div>
            <h2 className="text-xl font-heading font-bold text-gray-700">24 Students Assigned</h2>
            <p className="text-gray-500 mt-2">Monitor progress, review assessments, provide feedback.</p>
          </div>
        )}

        {activeTab === "feedback" && (
          <div className="card text-center py-12">
            <div className="text-5xl mb-4">💬</div>
            <h2 className="text-xl font-heading font-bold text-gray-700">Feedback Center</h2>
            <p className="text-gray-500 mt-2">12 assessments waiting for your personalized feedback.</p>
          </div>
        )}
      </main>
    </div>
  );
}

function StatCard({ value, label, color = "text-teal-600" }: { value: string; label: string; color?: string }) {
  return (
    <div className="card text-center py-4">
      <p className={`text-2xl font-bold ${color}`}>{value}</p>
      <p className="text-xs text-gray-500 mt-1">{label}</p>
    </div>
  );
}
