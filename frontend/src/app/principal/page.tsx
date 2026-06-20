"use client";

import { useRouter } from "next/navigation";

export default function PrincipalDashboardPage() {
  const router = useRouter();

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
