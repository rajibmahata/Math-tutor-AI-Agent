"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { NotificationBell } from "@/components/ui/notification-bell";

const API = "http://localhost:8000/api/v1";

interface PendingLesson {
  id: string;
  title: string;
  language: string;
  content_preview: string;
  created_at: string;
}

interface AssignedStudent {
  student_id: string;
  name: string;
  grade: string;
  accuracy_rate: number;
  current_streak: number;
  total_points: number;
  total_sessions: number;
  weak_topics: { topic_id: string; accuracy: number }[];
  last_session_at: string | null;
}

export default function TutorPortalPage() {
  const router = useRouter();
  const [tutor, setTutor] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("overview");
  const [pendingLessons, setPendingLessons] = useState<PendingLesson[]>([]);
  const [students, setStudents] = useState<AssignedStudent[]>([]);
  const [reviewLesson, setReviewLesson] = useState<any>(null);
  const [reviewLoading, setReviewLoading] = useState(false);
  const [feedbackStudentId, setFeedbackStudentId] = useState<string | null>(null);
  const [feedbackText, setFeedbackText] = useState("");
  const [feedbackSending, setFeedbackSending] = useState(false);

  const token = () => localStorage.getItem("access_token") ?? "";

  useEffect(() => {
    loadDashboard();
  }, []);

  useEffect(() => {
    if (activeTab === "reviews") loadPendingLessons();
    if (activeTab === "students") loadStudents();
  }, [activeTab]);

  const loadDashboard = async () => {
    if (!token()) { router.push("/login"); return; }
    try {
      const r = await fetch(`${API}/tutors/dashboard`, { headers: { Authorization: `Bearer ${token()}` } });
      if (r.ok) {
        setTutor(await r.json());
      } else if (r.status === 404) {
        const r2 = await fetch(`${API}/tutors/register`, {
          method: "POST",
          headers: { "Content-Type": "application/json", Authorization: `Bearer ${token()}` },
          body: JSON.stringify({ subjects: [{ subject: "Mathematics", grade_start: "1", grade_end: "8" }], experience_yrs: 1, bio: "New tutor" }),
        });
        if (r2.ok) setTutor(await r2.json());
      }
    } catch {}
    setLoading(false);
  };

  const loadPendingLessons = async () => {
    try {
      const r = await fetch(`${API}/content/lessons/pending`, { headers: { Authorization: `Bearer ${token()}` } });
      if (r.ok) {
        const data = await r.json();
        setPendingLessons(data.data || []);
      }
    } catch {}
  };

  const loadStudents = async () => {
    try {
      const r = await fetch(`${API}/tutors/students`, { headers: { Authorization: `Bearer ${token()}` } });
      if (r.ok) {
        const data = await r.json();
        setStudents(data.data || []);
      }
    } catch {}
  };

  const loadFullLesson = async (lessonId: string) => {
    setReviewLoading(true);
    try {
      const r = await fetch(`${API}/content/lessons/${lessonId}`, { headers: { Authorization: `Bearer ${token()}` } });
      if (r.ok) setReviewLesson(await r.json());
    } catch {}
    setReviewLoading(false);
  };

  const submitReview = async (lessonId: string, action: "approve" | "reject" | "modify", modifiedContent?: string) => {
    try {
      const r = await fetch(`${API}/content/lessons/${lessonId}/review`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token()}` },
        body: JSON.stringify({
          action,
          feedback: action === "reject" ? "Content requires regeneration" : undefined,
          modified_content: action === "modify" ? modifiedContent : undefined,
          accuracy_score: action === "approve" ? 0.9 : undefined,
          completeness_score: action === "approve" ? 0.85 : undefined,
          alignment_score: action === "approve" ? 0.9 : undefined,
        }),
      });
      if (r.ok) {
        setReviewLesson(null);
        loadPendingLessons();
      }
    } catch {}
  };

  const sendFeedback = async () => {
    if (!feedbackStudentId || !feedbackText.trim()) return;
    setFeedbackSending(true);
    try {
      await fetch(`${API}/tutors/feedback`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token()}` },
        body: JSON.stringify({ student_id: feedbackStudentId, message: feedbackText }),
      });
      setFeedbackText("");
      setFeedbackStudentId(null);
    } catch {}
    setFeedbackSending(false);
  };

  const logout = () => { localStorage.clear(); router.push("/login"); };

  if (loading) return (
    <div className="flex-1 flex items-center justify-center">
      <div className="text-center">
        <div className="text-4xl animate-bounce">🧮</div>
        <p className="text-gray-400 text-sm mt-2">Loading…</p>
      </div>
    </div>
  );

  return (
    <div className="flex-1 flex flex-col bg-gray-50">
      {/* Header */}
      <header className="bg-teal-600 text-white flex-shrink-0">
        <div className="px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-xl">👨‍🏫</span>
            <div>
              <h1 className="font-heading font-bold text-base">Tutor Portal</h1>
              <p className="text-teal-100 text-[10px]">
                {tutor?.verification_status === "admin_approved" ? "✅ Verified" : "⏳ Pending Verification"}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <NotificationBell size={18} />
            <button onClick={logout} className="text-teal-200 text-xs">Logout</button>
          </div>
        </div>

        {/* Tabs */}
        <div className="px-4 flex gap-1">
          {[
            { key: "overview", label: "📊 Overview" },
            { key: "reviews", label: "📚 Reviews" },
            { key: "students", label: "👩‍🎓 Students" },
          ].map((t) => (
            <button
              key={t.key}
              onClick={() => setActiveTab(t.key)}
              className={`px-3 py-2 text-xs rounded-t-lg transition ${
                activeTab === t.key ? "bg-white text-teal-700 font-semibold" : "text-teal-100 hover:text-white"
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>
      </header>

      {/* Content */}
      <div className="flex-1 overflow-y-auto px-4 py-4">

        {/* ── Overview Tab ── */}
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
              <h2 className="font-heading font-bold text-gray-700 text-sm mb-2">✅ Verification Status</h2>
              <div className="flex items-center gap-2">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  tutor?.verification_status === "admin_approved"
                    ? "bg-green-100 text-green-700"
                    : tutor?.verification_status === "rejected"
                    ? "bg-red-100 text-red-700"
                    : "bg-amber-100 text-amber-700"
                }`}>
                  {tutor?.verification_status ?? "pending"}
                </span>
              </div>
              <p className="text-xs text-gray-400 mt-2">
                Workflow: Registration → AI Verification → Principal Review → Admin Approval
              </p>
            </div>
          </div>
        )}

        {/* ── Content Reviews Tab ── */}
        {activeTab === "reviews" && (
          <div className="space-y-4">
            {reviewLesson ? (
              /* Full lesson review view */
              <div className="card space-y-4">
                <div className="flex items-start justify-between">
                  <div>
                    <h2 className="font-heading font-bold text-gray-800 text-sm">{reviewLesson.title}</h2>
                    <span className="text-xs text-gray-400">{reviewLesson.language.toUpperCase()} · AI-generated</span>
                  </div>
                  <button onClick={() => setReviewLesson(null)} className="text-gray-400 text-xs hover:text-gray-600">← Back</button>
                </div>

                <div className="bg-gray-50 rounded-xl p-3 max-h-64 overflow-y-auto">
                  <pre className="text-xs text-gray-700 whitespace-pre-wrap font-sans">
                    {reviewLesson.content_text}
                  </pre>
                </div>

                <div className="grid grid-cols-3 gap-2">
                  <button
                    onClick={() => submitReview(reviewLesson.id, "approve")}
                    className="bg-teal-600 text-white py-2 rounded-xl text-xs font-medium hover:bg-teal-700"
                  >
                    ✅ Approve
                  </button>
                  <button
                    onClick={() => submitReview(reviewLesson.id, "reject")}
                    className="bg-red-100 text-red-600 py-2 rounded-xl text-xs font-medium hover:bg-red-200"
                  >
                    ❌ Reject
                  </button>
                  <button
                    onClick={() => {
                      const edited = window.prompt("Edit the lesson content:", reviewLesson.content_text);
                      if (edited && edited !== reviewLesson.content_text) {
                        submitReview(reviewLesson.id, "modify", edited);
                      }
                    }}
                    className="bg-amber-100 text-amber-700 py-2 rounded-xl text-xs font-medium hover:bg-amber-200"
                  >
                    ✏️ Modify
                  </button>
                </div>
              </div>
            ) : (
              <>
                <div className="flex items-center justify-between">
                  <h2 className="font-heading font-bold text-gray-700 text-sm">
                    Pending Reviews ({pendingLessons.length})
                  </h2>
                  <button
                    onClick={loadPendingLessons}
                    className="text-xs text-teal-600 hover:underline"
                  >
                    Refresh
                  </button>
                </div>

                {pendingLessons.length === 0 ? (
                  <div className="card text-center py-8">
                    <div className="text-3xl mb-2">📚</div>
                    <p className="text-sm text-gray-400">No lessons pending review</p>
                    <p className="text-xs text-gray-300 mt-1">
                      You'll be notified when AI generates new content
                    </p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {pendingLessons.map((lesson) => (
                      <div key={lesson.id} className="card">
                        <div className="flex items-start justify-between mb-2">
                          <div>
                            <p className="text-sm font-semibold text-gray-800">{lesson.title}</p>
                            <span className="text-xs text-gray-400">
                              {lesson.language.toUpperCase()} · {new Date(lesson.created_at).toLocaleDateString()}
                            </span>
                          </div>
                          <span className="bg-amber-100 text-amber-700 text-[10px] px-2 py-0.5 rounded-full">
                            Pending Review
                          </span>
                        </div>
                        <p className="text-xs text-gray-500 line-clamp-2 mb-3">{lesson.content_preview}</p>
                        <div className="grid grid-cols-3 gap-2">
                          <button
                            onClick={() => submitReview(lesson.id, "approve")}
                            className="bg-teal-600 text-white py-1.5 rounded-lg text-xs font-medium"
                          >
                            ✅ Approve
                          </button>
                          <button
                            onClick={() => { setReviewLoading(true); loadFullLesson(lesson.id); }}
                            className="bg-blue-50 text-blue-700 py-1.5 rounded-lg text-xs font-medium"
                          >
                            👁️ Review
                          </button>
                          <button
                            onClick={() => submitReview(lesson.id, "reject")}
                            className="bg-red-50 text-red-600 py-1.5 rounded-lg text-xs font-medium"
                          >
                            ❌ Reject
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </>
            )}
          </div>
        )}

        {/* ── Students Tab ── */}
        {activeTab === "students" && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="font-heading font-bold text-gray-700 text-sm">
                Assigned Students ({students.length})
              </h2>
              <button onClick={loadStudents} className="text-xs text-teal-600 hover:underline">
                Refresh
              </button>
            </div>

            {students.length === 0 ? (
              <div className="card text-center py-8">
                <div className="text-3xl mb-2">👩‍🎓</div>
                <p className="text-sm text-gray-400">No students assigned yet</p>
              </div>
            ) : (
              students.map((s) => (
                <div key={s.student_id} className="card space-y-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-semibold text-gray-800 text-sm">{s.name}</p>
                      <p className="text-xs text-gray-400">Grade {s.grade} · {s.total_sessions} sessions</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-bold text-teal-600">{Math.round(s.accuracy_rate * 100)}%</p>
                      <p className="text-[10px] text-gray-400">accuracy</p>
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-2 text-center">
                    <div className="bg-amber-50 rounded-lg py-1.5">
                      <p className="text-sm font-bold text-amber-600">🔥{s.current_streak}</p>
                      <p className="text-[10px] text-gray-400">streak</p>
                    </div>
                    <div className="bg-primary-50 rounded-lg py-1.5">
                      <p className="text-sm font-bold text-primary-600">{s.total_points}</p>
                      <p className="text-[10px] text-gray-400">points</p>
                    </div>
                    <div className="bg-red-50 rounded-lg py-1.5">
                      <p className="text-sm font-bold text-red-500">{s.weak_topics.length}</p>
                      <p className="text-[10px] text-gray-400">weak areas</p>
                    </div>
                  </div>

                  {s.weak_topics.length > 0 && (
                    <div>
                      <p className="text-xs text-gray-500 mb-1">⚠️ Weak areas:</p>
                      <div className="flex flex-wrap gap-1">
                        {s.weak_topics.map((w, i) => (
                          <span key={i} className="bg-red-50 text-red-600 text-[10px] px-2 py-0.5 rounded-full">
                            {Math.round(w.accuracy * 100)}% acc
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Send Feedback */}
                  {feedbackStudentId === s.student_id ? (
                    <div className="space-y-2">
                      <textarea
                        value={feedbackText}
                        onChange={(e) => setFeedbackText(e.target.value)}
                        placeholder="Write personalized feedback…"
                        className="w-full border border-gray-200 rounded-xl p-2 text-xs resize-none h-20"
                      />
                      <div className="flex gap-2">
                        <button
                          onClick={sendFeedback}
                          disabled={feedbackSending || !feedbackText.trim()}
                          className="bg-teal-600 text-white px-3 py-1 rounded-lg text-xs disabled:opacity-50"
                        >
                          {feedbackSending ? "Sending…" : "Send Feedback"}
                        </button>
                        <button
                          onClick={() => { setFeedbackStudentId(null); setFeedbackText(""); }}
                          className="text-gray-400 text-xs"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    <button
                      onClick={() => setFeedbackStudentId(s.student_id)}
                      className="w-full bg-teal-50 text-teal-700 py-2 rounded-xl text-xs font-medium hover:bg-teal-100"
                    >
                      💬 Send Feedback
                    </button>
                  )}
                </div>
              ))
            )}
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
