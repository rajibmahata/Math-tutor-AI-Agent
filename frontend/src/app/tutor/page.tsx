"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

const API = "http://localhost:8000/api/v1";

export default function TutorPortalPage() {
  const router = useRouter();
  const [tutor, setTutor] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("overview");

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    const token = localStorage.getItem("access_token");
    if (!token) { router.push("/login"); return; }
    try {
      const r = await fetch(`${API}/tutors/dashboard`, { headers: { Authorization: `Bearer ${token}` } });
      if (r.ok) setTutor(await r.json());
      else if (r.status === 404) {
        // Try to register
        const r2 = await fetch(`${API}/tutors/register`, {
          method: "POST",
          headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
          body: JSON.stringify({ subjects: [{ subject: "Mathematics", grade_start: "1", grade_end: "8" }], experience_yrs: 1, bio: "New tutor" }),
        });
        if (r2.ok) setTutor(await r2.json());
      }
    } catch {}
    setLoading(false);
  };

  const logout = () => { localStorage.clear(); router.push("/login"); };

  if (loading) return <div className="flex-1 flex items-center justify-center"><div className="text-center"><div className="text-4xl animate-bounce">🧮</div><p className="text-gray-400 text-sm mt-2">Loading...</p></div></div>;

  return (
    <div className="flex-1 flex flex-col bg-gray-50">
      {/* Header */}
      <header className="bg-teal-600 text-white flex-shrink-0">
        <div className="px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-xl">👨‍🏫</span>
            <div>
              <h1 className="font-heading font-bold text-base">Tutor Portal</h1>
              <p className="text-teal-100 text-[10px]">{tutor?.verification_status === "admin_approved" ? "✅ Verified" : "⏳ Pending"}</p>
            </div>
          </div>
          <button onClick={logout} className="text-teal-200 text-xs">Logout</button>
        </div>
        {/* Tabs */}
        <div className="px-4 flex gap-1">
          {[
            { key: "overview", label: "📊" },
            { key: "reviews", label: "📚" },
            { key: "students", label: "👩‍🎓" },
          ].map((t) => (
            <button key={t.key} onClick={() => setActiveTab(t.key)}
              className={`px-3 py-2 text-sm rounded-t-lg transition ${activeTab === t.key ? "bg-white text-teal-700 font-medium" : "text-teal-100"}`}>
              {t.label}
            </button>
          ))}
        </div>
      </header>

      {/* Content */}
      <div className="flex-1 overflow-y-auto px-4 py-4">
        {activeTab === "overview" && (
          <div className="space-y-4">
            <div className="grid grid-cols-3 gap-3">
              <StatCard value={String(tutor?.assigned_students || 0)} label="Students" />
              <StatCard value={String(tutor?.experience_yrs || 0)} label="Yrs Exp" />
              <StatCard value={tutor?.rating ? `⭐${tutor.rating}` : "—"} label="Rating" />
            </div>

            <div className="card">
              <h2 className="font-heading font-bold text-gray-700 text-sm mb-3">📚 Teaching Subjects</h2>
              {(tutor?.subjects || []).map((s: any, i: number) => (
                <div key={i} className="flex items-center justify-between py-2 border-b last:border-0">
                  <span className="text-sm font-medium text-gray-700">{s.subject}</span>
                  <span className="text-xs text-gray-400">Class {s.grade_start}–{s.grade_end}</span>
                </div>
              ))}
              {(!tutor?.subjects || tutor.subjects.length === 0) && (
                <p className="text-sm text-gray-400">No subjects configured yet</p>
              )}
            </div>

            <div className="card">
              <h2 className="font-heading font-bold text-gray-700 text-sm mb-3">👩‍🎓 Student Performance</h2>
              <div className="text-center py-4">
                <p className="text-3xl font-bold text-teal-600">{tutor?.assigned_students || 0}</p>
                <p className="text-xs text-gray-400 mt-1">Students assigned to you</p>
              </div>
            </div>
          </div>
        )}

        {activeTab === "reviews" && (
          <div className="card text-center py-8">
            <div className="text-4xl mb-3">📚</div>
            <h2 className="font-heading font-bold text-gray-700">Content Review</h2>
            <p className="text-sm text-gray-400 mt-2">AI-generated lessons ready for your validation.</p>
            <div className="mt-4 space-y-2">
              {["Fractions Introduction", "Multiplication Tables", "Division Basics"].map((t, i) => (
                <div key={i} className="flex items-center justify-between p-3 bg-gray-50 rounded-xl">
                  <span className="text-sm text-gray-700">{t}</span>
                  <div className="flex gap-1">
                    <button className="bg-teal-600 text-white px-2 py-1 rounded text-xs">✓</button>
                    <button className="bg-gray-200 text-gray-600 px-2 py-1 rounded text-xs">✏️</button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === "students" && (
          <div className="card text-center py-8">
            <div className="text-4xl mb-3">👩‍🎓</div>
            <h2 className="font-heading font-bold text-gray-700">{tutor?.assigned_students || 0} Students</h2>
            <p className="text-sm text-gray-400 mt-2">Monitor progress and provide personalized feedback.</p>
          </div>
        )}
      </div>
    </div>
  );
}

function StatCard({ value, label }: { value: string; label: string }) {
  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-3 text-center">
      <p className="text-xl font-bold text-teal-600">{value}</p>
      <p className="text-[10px] text-gray-400 mt-0.5">{label}</p>
    </div>
  );
}
