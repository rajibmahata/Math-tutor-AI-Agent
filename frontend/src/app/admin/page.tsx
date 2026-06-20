"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { NotificationBell } from "@/components/ui/notification-bell";

const API = "http://localhost:8000/api/v1";

interface DashboardData {
  organization_overview: { total_users: number; total_students: number; total_tutors: number; total_principals: number };
  approval_queue: { tutor_approvals_pending: number; content_pending_review: number };
  content: { published_lessons: number };
  engagement: { total_sessions: number };
  platform_health: { uptime: string; status: string };
}

interface PendingTutor {
  tutor_id: string;
  name: string;
  email: string;
  subjects: any[];
  experience_yrs: number;
  verification_status: string;
}

export default function AdminDashboardPage() {
  const router = useRouter();
  const [dashboard, setDashboard] = useState<DashboardData | null>(null);
  const [pendingTutors, setPendingTutors] = useState<PendingTutor[]>([]);
  const [activeTab, setActiveTab] = useState("overview");
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  const token = () => localStorage.getItem("access_token") ?? "";

  useEffect(() => { loadDashboard(); }, []);
  useEffect(() => { if (activeTab === "approvals") loadPendingTutors(); }, [activeTab]);

  const loadDashboard = async () => {
    try {
      const r = await fetch(`${API}/admin/dashboard`, { headers: { Authorization: `Bearer ${token()}` } });
      if (r.ok) setDashboard(await r.json());
    } catch {}
    setLoading(false);
  };

  const loadPendingTutors = async () => {
    try {
      const r = await fetch(`${API}/admin/tutors/pending`, { headers: { Authorization: `Bearer ${token()}` } });
      if (r.ok) {
        const data = await r.json();
        setPendingTutors(data.data || []);
      }
    } catch {}
  };

  const approveTutor = async (tutorId: string, action: "approve" | "reject") => {
    setActionLoading(tutorId);
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
    setActionLoading(null);
  };

  const logout = () => { localStorage.clear(); router.push("/login"); };

  const ov = dashboard?.organization_overview;
  const aq = dashboard?.approval_queue;

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-slate-800 text-white">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl">⚡</span>
            <div>
              <h1 className="font-heading font-bold text-lg">Super Admin</h1>
              <p className="text-slate-300 text-xs">VidyaMitra Platform v2.0</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500" />
            </span>
            <span className="text-sm text-slate-300">
              {dashboard?.platform_health?.status === "healthy" ? "System Healthy" : "Checking…"}
            </span>
            <NotificationBell size={18} />
            <button onClick={logout} className="text-slate-400 text-sm hover:text-white">Logout</button>
          </div>
        </div>

        {/* Tabs */}
        <div className="max-w-6xl mx-auto px-4 flex gap-1">
          {[
            { key: "overview", label: "📊 Overview" },
            { key: "approvals", label: `⚡ Approvals${aq?.tutor_approvals_pending ? ` (${aq.tutor_approvals_pending})` : ""}` },
            { key: "users", label: "👥 Users" },
          ].map((t) => (
            <button
              key={t.key}
              onClick={() => setActiveTab(t.key)}
              className={`px-4 py-2 text-sm rounded-t-lg transition ${
                activeTab === t.key ? "bg-gray-100 text-slate-800 font-semibold" : "text-slate-300 hover:text-white"
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-6 space-y-6">

        {/* ── Overview Tab ── */}
        {activeTab === "overview" && (
          <>
            <div className="grid grid-cols-4 gap-4">
              <StatCard value={String(ov?.total_users ?? "—")} label="Total Users" color="text-slate-700" />
              <StatCard value={String(ov?.total_students ?? "—")} label="Students" color="text-indigo-600" />
              <StatCard value={String(ov?.total_tutors ?? "—")} label="Tutors" color="text-teal-600" />
              <StatCard value={String(ov?.total_principals ?? "—")} label="Principals" color="text-amber-600" />
            </div>

            <div className="grid grid-cols-3 gap-4">
              <StatCard value={String(aq?.tutor_approvals_pending ?? "—")} label="Pending Tutor Approvals" color="text-red-500" />
              <StatCard value={String(aq?.content_pending_review ?? "—")} label="Content Pending Review" color="text-amber-600" />
              <StatCard value={String(dashboard?.content?.published_lessons ?? "—")} label="Published Lessons" color="text-green-600" />
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div className="card text-center py-4">
                <p className="text-2xl font-bold text-green-600">{dashboard?.platform_health?.uptime ?? "—"}</p>
                <p className="text-xs text-gray-500 mt-1">Uptime</p>
              </div>
              <div className="card text-center py-4">
                <p className="text-2xl font-bold text-slate-700">320ms</p>
                <p className="text-xs text-gray-500 mt-1">API P95 Latency</p>
              </div>
              <div className="card text-center py-4">
                <p className="text-2xl font-bold text-slate-700">{String(dashboard?.engagement?.total_sessions ?? "—")}</p>
                <p className="text-xs text-gray-500 mt-1">Total Sessions</p>
              </div>
            </div>

            <div className="grid grid-cols-4 gap-4">
              {[
                { icon: "👨‍🏫", label: "Tutor Portal", href: "/tutor" },
                { icon: "👨‍💼", label: "Principal Portal", href: "/principal" },
                { icon: "👩‍🎓", label: "Student Portal", href: "/dashboard" },
                { icon: "📱", label: "Demo", href: "/demo" },
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
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <h2 className="font-heading font-bold text-gray-700 mb-4">⚡ Tutor Approval Queue</h2>
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
                      <p className="text-xs text-gray-400">
                        {tutor.email} · {tutor.experience_yrs}yr exp ·
                        <span className="ml-1 px-1.5 py-0.5 bg-amber-100 text-amber-700 rounded text-[10px]">
                          {tutor.verification_status}
                        </span>
                      </p>
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={() => approveTutor(tutor.tutor_id, "approve")}
                        disabled={actionLoading === tutor.tutor_id}
                        className="bg-slate-700 text-white px-3 py-1 rounded-lg text-xs disabled:opacity-50"
                      >
                        {actionLoading === tutor.tutor_id ? "…" : "Approve"}
                      </button>
                      <button
                        onClick={() => approveTutor(tutor.tutor_id, "reject")}
                        disabled={actionLoading === tutor.tutor_id}
                        className="bg-red-100 text-red-600 px-3 py-1 rounded-lg text-xs disabled:opacity-50"
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

        {/* ── Users Tab ── */}
        {activeTab === "users" && (
          <UsersPanel token={token()} />
        )}
      </main>
    </div>
  );
}

function UsersPanel({ token }: { token: string }) {
  const [users, setUsers] = useState<any[]>([]);
  const [role, setRole] = useState("");

  useEffect(() => {
    const fetchUsers = async () => {
      const url = role ? `${API}/admin/users?role=${role}&limit=50` : `${API}/admin/users?limit=50`;
      const r = await fetch(url, { headers: { Authorization: `Bearer ${token}` } });
      if (r.ok) { const d = await r.json(); setUsers(d.data || []); }
    };
    fetchUsers();
  }, [role, token]);

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="font-heading font-bold text-gray-700">👥 User Management</h2>
        <select value={role} onChange={(e) => setRole(e.target.value)} className="border rounded-lg px-2 py-1 text-sm text-gray-600">
          <option value="">All Roles</option>
          <option value="student">Students</option>
          <option value="tutor">Tutors</option>
          <option value="principal">Principals</option>
          <option value="admin">Admins</option>
        </select>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b text-left text-gray-500 text-xs">
              <th className="pb-2">Name</th>
              <th className="pb-2">Email</th>
              <th className="pb-2">Role</th>
              <th className="pb-2">Status</th>
              <th className="pb-2">Joined</th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id} className="border-b last:border-0 text-xs">
                <td className="py-2 font-medium text-gray-800">{u.full_name}</td>
                <td className="py-2 text-gray-500">{u.email}</td>
                <td className="py-2">
                  <span className="px-1.5 py-0.5 rounded-full bg-gray-100 text-gray-600">{u.role}</span>
                </td>
                <td className="py-2">
                  <span className={`px-1.5 py-0.5 rounded-full ${u.is_active ? "bg-green-100 text-green-700" : "bg-red-100 text-red-600"}`}>
                    {u.is_active ? "Active" : "Inactive"}
                  </span>
                </td>
                <td className="py-2 text-gray-400">{u.created_at ? new Date(u.created_at).toLocaleDateString() : "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {users.length === 0 && <p className="text-center py-4 text-gray-400 text-sm">No users found</p>}
      </div>
    </div>
  );
}

function StatCard({ value, label, color = "text-slate-700" }: { value: string; label: string; color?: string }) {
  return (
    <div className="card text-center py-4">
      <p className={`text-2xl font-bold ${color}`}>{value}</p>
      <p className="text-xs text-gray-500 mt-1">{label}</p>
    </div>
  );
}


  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-slate-800 text-white">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl">⚡</span>
            <div>
              <h1 className="font-heading font-bold text-lg">Super Admin</h1>
              <p className="text-slate-300 text-xs">VidyaMitra Platform v2.0</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500" />
            </span>
            <span className="text-sm text-slate-300">System Healthy</span>
            <button onClick={() => router.push("/login")} className="text-slate-400 text-sm hover:text-white">Logout</button>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-6 space-y-6">
        {/* Org Overview */}
        <div className="grid grid-cols-4 gap-4">
          <StatCard value="1,500" label="Total Users" color="text-slate-700" />
          <StatCard value="1,200" label="Students" color="text-indigo-600" />
          <StatCard value="50" label="Tutors" color="text-teal-600" />
          <StatCard value="8" label="Principals" color="text-amber-600" />
        </div>

        {/* Approval Queue */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
          <h2 className="font-heading font-bold text-gray-700 mb-4">⚡ Approval Queue</h2>
          <div className="space-y-3">
            {[
              { name: "Mr. Kumar", role: "Tutor", subject: "Mathematics", ai: "✅ Verified", principal: "✅ Approved", action: "pending" },
              { name: "Ms. Das", role: "Tutor", subject: "Science", ai: "⚠️ Review", principal: "⏳ Pending", action: "waiting" },
              { name: "Content #452", role: "Lesson", subject: "Math Gr.3", ai: "N/A", principal: "🔴 Escalated", action: "review" },
            ].map((item, i) => (
              <div key={i} className="flex items-center justify-between p-3 bg-gray-50 rounded-xl">
                <div>
                  <p className="font-medium text-gray-700">{item.name} · {item.role}</p>
                  <p className="text-xs text-gray-400">{item.subject} · AI: {item.ai} · Principal: {item.principal}</p>
                </div>
                <div className="flex gap-2">
                  {item.action === "pending" && (
                    <>
                      <button className="bg-slate-700 text-white px-3 py-1 rounded-lg text-xs">Approve</button>
                      <button className="bg-red-100 text-red-600 px-3 py-1 rounded-lg text-xs">Reject</button>
                    </>
                  )}
                  {item.action === "review" && (
                    <button className="bg-amber-100 text-amber-700 px-3 py-1 rounded-lg text-xs">Review →</button>
                  )}
                  {item.action === "waiting" && (
                    <span className="text-xs text-gray-400">⏳ Awaiting Principal</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Platform Health */}
        <div className="grid grid-cols-3 gap-4">
          <div className="card text-center py-4">
            <p className="text-2xl font-bold text-green-600">99.9%</p>
            <p className="text-xs text-gray-500 mt-1">Uptime</p>
          </div>
          <div className="card text-center py-4">
            <p className="text-2xl font-bold text-slate-700">320ms</p>
            <p className="text-xs text-gray-500 mt-1">API P95 Latency</p>
          </div>
          <div className="card text-center py-4">
            <p className="text-2xl font-bold text-green-600">0.02%</p>
            <p className="text-xs text-gray-500 mt-1">Error Rate</p>
          </div>
        </div>

        {/* Quick Links */}
        <div className="grid grid-cols-4 gap-4">
          <button onClick={() => router.push("/tutor")} className="card-hover text-center py-4">
            <span className="text-2xl">👨‍🏫</span>
            <p className="text-sm font-medium text-gray-700 mt-1">Tutor Portal</p>
          </button>
          <button onClick={() => router.push("/principal")} className="card-hover text-center py-4">
            <span className="text-2xl">👨‍💼</span>
            <p className="text-sm font-medium text-gray-700 mt-1">Principal Portal</p>
          </button>
          <button onClick={() => router.push("/dashboard")} className="card-hover text-center py-4">
            <span className="text-2xl">👩‍🎓</span>
            <p className="text-sm font-medium text-gray-700 mt-1">Student Portal</p>
          </button>
          <button onClick={() => router.push("/demo")} className="card-hover text-center py-4">
            <span className="text-2xl">📱</span>
            <p className="text-sm font-medium text-gray-700 mt-1">Demo</p>
          </button>
        </div>
      </main>
    </div>
  );
}

function StatCard({ value, label, color = "text-slate-700" }: { value: string; label: string; color?: string }) {
  return (
    <div className="card text-center py-4">
      <p className={`text-2xl font-bold ${color}`}>{value}</p>
      <p className="text-xs text-gray-500 mt-1">{label}</p>
    </div>
  );
}
