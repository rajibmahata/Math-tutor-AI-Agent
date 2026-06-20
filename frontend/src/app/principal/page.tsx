"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { NotificationBell } from "@/components/ui/notification-bell";

const API = "http://localhost:8000/api/v1";

interface PrincipalDashboard {
  institution: string;
  overview: {
    total_students: number;
    active_students: number;
    total_tutors: number;
    pending_tutor_approvals: number;
    total_sessions: number;
  };
  tutors: {
    tutor_id: string;
    name: string;
    subjects: any[];
    total_students: number;
    rating: number;
    verification_status: string;
  }[];
}

export default function PrincipalDashboardPage() {
  const router = useRouter();
  const [data, setData] = useState<PrincipalDashboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("overview");
  const [approvingId, setApprovingId] = useState<string | null>(null);
  const [pendingTutors, setPendingTutors] = useState<any[]>([]);

  const token = () => localStorage.getItem("access_token") ?? "";

  useEffect(() => { loadDashboard(); }, []);
  useEffect(() => { if (activeTab === "approvals") loadPendingTutors(); }, [activeTab]);

  const loadDashboard = async () => {
    try {
      const r = await fetch(`${API}/admin/principal/dashboard`, {
        headers: { Authorization: `Bearer ${token()}` },
      });
      if (r.ok) setData(await r.json());
    } catch {}
    setLoading(false);
  };

  const loadPendingTutors = async () => {
    try {
      const r = await fetch(`${API}/admin/tutors/pending`, { headers: { Authorization: `Bearer ${token()}` } });
      if (r.ok) { const d = await r.json(); setPendingTutors(d.data || []); }
    } catch {}
  };

  const approveTutor = async (tutorId: string, action: "approve" | "reject") => {
    setApprovingId(tutorId);
    try {
      const r = await fetch(`${API}/admin/tutors/${tutorId}/approve?action=${action}`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token()}` },
      });
      if (r.ok) {
        setPendingTutors((prev) => prev.filter((t) => t.tutor_id !== tutorId));
        loadDashboard();
      }
    } catch {}
    setApprovingId(null);
  };

  const logout = () => { localStorage.clear(); router.push("/login"); };

  const ov = data?.overview;

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-amber-600 text-white">
        <div className="max-w-5xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl">👨‍💼</span>
            <div>
              <h1 className="font-heading font-bold text-lg">Principal Portal</h1>
              <p className="text-amber-100 text-xs">{data?.institution ?? "VidyaMitra"}</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <NotificationBell size={18} />
            <button onClick={logout} className="text-amber-200 text-sm hover:text-white">Logout</button>
          </div>
        </div>

        {/* Tabs */}
        <div className="max-w-5xl mx-auto px-4 flex gap-1">
          {[
            { key: "overview", label: "📊 Overview" },
            { key: "approvals", label: `✅ Approvals${ov?.pending_tutor_approvals ? ` (${ov.pending_tutor_approvals})` : ""}` },
            { key: "tutors", label: "👨‍🏫 Tutors" },
          ].map((t) => (
            <button
              key={t.key}
              onClick={() => setActiveTab(t.key)}
              className={`px-4 py-2 text-sm rounded-t-lg transition ${
                activeTab === t.key ? "bg-white text-amber-700 font-semibold" : "text-amber-100 hover:text-white"
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 py-6 space-y-6">

        {/* ── Overview Tab ── */}
        {activeTab === "overview" && (
          <>
            <div className="grid grid-cols-4 gap-4">
              <StatCard value={String(ov?.total_students ?? "—")} label="Total Students" />
              <StatCard value={String(ov?.active_students ?? "—")} label="Active Students" />
              <StatCard value={String(ov?.total_tutors ?? "—")} label="Tutors" />
              <StatCard value={String(ov?.pending_tutor_approvals ?? "—")} label="Pending Approvals" color="text-amber-600" />
            </div>

            <div className="card">
              <h2 className="font-heading font-bold text-gray-700 mb-2">📈 Platform Activity</h2>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-amber-50 rounded-xl p-3 text-center">
                  <p className="text-2xl font-bold text-amber-700">{ov?.total_sessions ?? "—"}</p>
                  <p className="text-xs text-gray-500 mt-1">Total Sessions</p>
                </div>
                <div className="bg-green-50 rounded-xl p-3 text-center">
                  <p className="text-2xl font-bold text-green-600">{ov?.total_tutors ?? "—"}</p>
                  <p className="text-xs text-gray-500 mt-1">Active Tutors</p>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4">
              {[
                { icon: "👨‍🏫", label: "Tutor Portal", href: "/tutor" },
                { icon: "⚡", label: "Admin Portal", href: "/admin" },
                { icon: "👩‍🎓", label: "Student Portal", href: "/dashboard" },
              ].map((link) => (
                <button key={link.href} onClick={() => router.push(link.href)} className="card text-center py-4 hover:shadow-md transition">
                  <span className="text-2xl">{link.icon}</span>
                  <p className="text-sm font-medium text-gray-700 mt-1">{link.label}</p>
                </button>
              ))}
            </div>
          </>
        )}

        {/* ── Approvals Tab ── */}
        {activeTab === "approvals" && (
          <div className="card">
            <h2 className="font-heading font-bold text-gray-700 mb-4">✅ Tutor Approval Queue</h2>
            {pendingTutors.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-3xl mb-2">✅</p>
                <p className="text-gray-400">No pending approvals</p>
              </div>
            ) : (
              <div className="space-y-3">
                {pendingTutors.map((tutor) => (
                  <div key={tutor.tutor_id} className="flex items-center justify-between p-3 bg-gray-50 rounded-xl">
                    <div>
                      <p className="font-medium text-gray-700">{tutor.name}</p>
                      <p className="text-xs text-gray-400">{tutor.email} · {tutor.experience_yrs}yr exp</p>
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={() => approveTutor(tutor.tutor_id, "approve")}
                        disabled={approvingId === tutor.tutor_id}
                        className="bg-amber-600 text-white px-3 py-1 rounded-lg text-xs disabled:opacity-50"
                      >
                        {approvingId === tutor.tutor_id ? "…" : "Approve"}
                      </button>
                      <button
                        onClick={() => approveTutor(tutor.tutor_id, "reject")}
                        disabled={approvingId === tutor.tutor_id}
                        className="bg-red-100 text-red-600 px-3 py-1 rounded-lg text-xs"
                      >
                        Reject
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* ── Tutors Tab ── */}
        {activeTab === "tutors" && (
          <div className="card">
            <h2 className="font-heading font-bold text-gray-700 mb-4">👨‍🏫 Tutor Performance</h2>
            {(data?.tutors ?? []).length === 0 ? (
              <p className="text-center text-gray-400 py-6">No active tutors yet</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b text-left text-gray-500 text-xs">
                      <th className="pb-2">Tutor</th>
                      <th className="pb-2">Students</th>
                      <th className="pb-2">Rating</th>
                      <th className="pb-2">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(data?.tutors ?? []).map((t) => (
                      <tr key={t.tutor_id} className="border-b last:border-0">
                        <td className="py-2 font-medium text-gray-800">{t.name}</td>
                        <td className="py-2">{t.total_students}</td>
                        <td className="py-2">{t.rating > 0 ? `⭐${t.rating}` : "—"}</td>
                        <td className="py-2">
                          <span className={`px-1.5 py-0.5 rounded-full text-[10px] ${
                            t.verification_status === "admin_approved"
                              ? "bg-green-100 text-green-700"
                              : "bg-amber-100 text-amber-700"
                          }`}>
                            {t.verification_status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}

function StatCard({ value, label, color = "text-amber-700" }: { value: string; label: string; color?: string }) {
  return (
    <div className="card text-center py-4">
      <p className={`text-2xl font-bold ${color}`}>{value}</p>
      <p className="text-xs text-gray-500 mt-1">{label}</p>
    </div>
  );
}


  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-amber-600 text-white">
        <div className="max-w-5xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl">👨‍💼</span>
            <div>
              <h1 className="font-heading font-bold text-lg">Principal Portal</h1>
              <p className="text-amber-100 text-xs">DAV Group · Kolkata</p>
            </div>
          </div>
          <button onClick={() => router.push("/login")} className="text-amber-200 text-sm hover:text-white">Logout</button>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 py-6 space-y-6">
        {/* Stats */}
        <div className="grid grid-cols-4 gap-4">
          <StatCard value="450" label="Students" />
          <StatCard value="380" label="Active" />
          <StatCard value="12" label="Tutors" />
          <StatCard value="2" label="Pending Approvals" color="text-amber-600" />
        </div>

        {/* Tutor Performance */}
        <div className="card">
          <h2 className="font-heading font-bold text-gray-700 mb-4">👨‍🏫 Tutor Performance</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-gray-500">
                  <th className="pb-2">Tutor</th><th className="pb-2">Students</th><th className="pb-2">Rating</th><th className="pb-2">Reviews</th>
                </tr>
              </thead>
              <tbody>
                {[
                  { name: "Mrs. Gupta", students: 24, rating: "⭐4.7", reviews: "92% ✅" },
                  { name: "Mr. Kumar", students: 18, rating: "⭐4.2", reviews: "78% ⚠️" },
                  { name: "Ms. Sharma", students: 30, rating: "⭐4.9", reviews: "96% ✅" },
                ].map((t, i) => (
                  <tr key={i} className="border-b last:border-0">
                    <td className="py-2 font-medium">{t.name}</td>
                    <td className="py-2">{t.students}</td>
                    <td className="py-2">{t.rating}</td>
                    <td className="py-2">{t.reviews}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Pending Actions */}
        <div className="card">
          <h2 className="font-heading font-bold text-gray-700 mb-4">⚠️ Pending Actions</h2>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-red-50 rounded-xl">
              <div>
                <p className="font-medium text-gray-700">🔴 Content Dispute</p>
                <p className="text-xs text-gray-400">Escalated by Mrs. Gupta — Math Grade 3</p>
              </div>
              <button className="bg-amber-600 text-white px-3 py-1 rounded-lg text-xs">Resolve →</button>
            </div>
            <div className="flex items-center justify-between p-3 bg-amber-50 rounded-xl">
              <div>
                <p className="font-medium text-gray-700">🟡 New Tutor Registration</p>
                <p className="text-xs text-gray-400">Mr. Verma — Science, AI Verified</p>
              </div>
              <button className="bg-amber-600 text-white px-3 py-1 rounded-lg text-xs">Review →</button>
            </div>
          </div>
        </div>

        {/* Quick Links */}
        <div className="grid grid-cols-3 gap-4">
          <button onClick={() => router.push("/tutor")} className="card-hover text-center py-4">
            <span className="text-2xl">👨‍🏫</span>
            <p className="text-sm font-medium text-gray-700 mt-1">Tutor Portal</p>
          </button>
          <button onClick={() => router.push("/admin")} className="card-hover text-center py-4">
            <span className="text-2xl">⚡</span>
            <p className="text-sm font-medium text-gray-700 mt-1">Admin Portal</p>
          </button>
          <button onClick={() => router.push("/dashboard")} className="card-hover text-center py-4">
            <span className="text-2xl">👩‍🎓</span>
            <p className="text-sm font-medium text-gray-700 mt-1">Student Portal</p>
          </button>
        </div>
      </main>
    </div>
  );
}

function StatCard({ value, label, color = "text-amber-700" }: { value: string; label: string; color?: string }) {
  return (
    <div className="card text-center py-4">
      <p className={`text-2xl font-bold ${color}`}>{value}</p>
      <p className="text-xs text-gray-500 mt-1">{label}</p>
    </div>
  );
}
