"use client";

import { useRouter } from "next/navigation";

export default function AdminDashboardPage() {
  const router = useRouter();

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
