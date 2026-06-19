"use client";

import { useRouter } from "next/navigation";

export default function PracticePage() {
  const router = useRouter();

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center card max-w-md mx-4">
        <div className="text-6xl mb-4">✏️</div>
        <h1 className="text-2xl font-heading font-bold text-gray-800 mb-2">
          Practice Mode
        </h1>
        <p className="text-gray-500 mb-6">
          Adaptive quizzes coming in Phase 2! Practice with AI-generated questions
          tailored to your learning level.
        </p>
        <button onClick={() => router.push("/dashboard")} className="btn-primary">
          ← Back to Dashboard
        </button>
      </div>
    </div>
  );
}
