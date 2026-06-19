"use client";

import { useRouter } from "next/navigation";

export default function ProgressPage() {
  const router = useRouter();

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

      <main className="max-w-4xl mx-auto px-4 py-8">
        <div className="text-center card">
          <div className="text-5xl mb-4">📊</div>
          <h2 className="text-xl font-heading font-bold text-gray-700 mb-2">
            Detailed Analytics Coming in Phase 2
          </h2>
          <p className="text-gray-500">
            Full progress tracking with charts, topic mastery maps, and learning velocity.
          </p>
        </div>
      </main>
    </div>
  );
}
