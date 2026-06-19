"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { createStudent } from "@/lib/api";
import type { Language, Grade } from "@/types";

const LANGUAGES: { value: Language; label: string; emoji: string }[] = [
  { value: "en", label: "English", emoji: "🇬🇧" },
  { value: "hi", label: "हिंदी", emoji: "🇮🇳" },
  { value: "bn", label: "বাংলা", emoji: "🇧🇩" },
];

const GRADES: { value: Grade; label: string; age: number }[] = [
  { value: "N", label: "Nursery", age: 3 },
  { value: "KG", label: "Kindergarten", age: 4 },
  { value: "1", label: "Class 1", age: 5 },
  { value: "2", label: "Class 2", age: 6 },
  { value: "3", label: "Class 3", age: 7 },
  { value: "4", label: "Class 4", age: 8 },
  { value: "5", label: "Class 5", age: 9 },
  { value: "6", label: "Class 6", age: 10 },
  { value: "7", label: "Class 7", age: 11 },
  { value: "8", label: "Class 8", age: 12 },
  { value: "9", label: "Class 9", age: 13 },
  { value: "10", label: "Class 10", age: 14 },
];

export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [grade, setGrade] = useState<Grade>("3");
  const [language, setLanguage] = useState<Language>("en");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async () => {
    setLoading(true);
    setError("");
    try {
      const gradeData = GRADES.find((g) => g.value === grade)!;
      await createStudent(gradeData.age, grade, language);
      router.push("/dashboard");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to create profile");
    } finally {
      setLoading(false);
    }
  };

  const gradeData = GRADES.find((g) => g.value === grade);

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-primary-50 to-white">
      <div className="w-full max-w-md">
        {step === 1 && (
          <div className="card space-y-6 animate-bounce-in">
            <div className="text-center">
              <div className="text-5xl mb-4">📝</div>
              <h2 className="text-2xl font-heading font-bold text-gray-800">Your Grade</h2>
              <p className="text-gray-500 mt-1">We'll customize your learning</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">What grade are you in?</label>
              <select value={grade} onChange={(e) => setGrade(e.target.value as Grade)} className="input-field">
                {GRADES.map((g) => (
                  <option key={g.value} value={g.value}>{g.label} (Age {g.age})</option>
                ))}
              </select>
            </div>
            {gradeData && (
              <div className="bg-primary-50 rounded-xl p-3 text-sm text-primary-700">
                {gradeData.label} students typically learn:{" "}
                {["N","KG"].includes(grade) ? "counting, shapes, and number recognition" :
                 ["1","2"].includes(grade) ? "addition, subtraction, and number sense" :
                 ["3","4","5"].includes(grade) ? "multiplication, division, and fractions" :
                 ["6","7","8"].includes(grade) ? "algebra basics, geometry, and data handling" :
                 "advanced algebra, trigonometry, and exam preparation"}
              </div>
            )}
            <button onClick={() => setStep(2)} className="btn-primary w-full">Continue →</button>
            {error && <div className="bg-error-50 border border-error-500/30 text-error-600 rounded-xl p-3 text-sm text-center">{error}</div>}
          </div>
        )}
        {step === 2 && (
          <div className="card space-y-6 animate-bounce-in">
            <div className="text-center">
              <div className="text-5xl mb-4">🌐</div>
              <h2 className="text-2xl font-heading font-bold text-gray-800">Choose Language</h2>
              <p className="text-gray-500 mt-1">Learn math in your language</p>
            </div>
            <div className="space-y-3">
              {LANGUAGES.map((lang) => (
                <button key={lang.value} onClick={() => setLanguage(lang.value)}
                  className={`w-full rounded-xl px-4 py-4 text-left flex items-center gap-4 transition-colors ${language === lang.value ? "bg-primary-100 border-2 border-primary-500" : "bg-gray-50 border-2 border-transparent hover:bg-gray-100"}`}>
                  <span className="text-2xl">{lang.emoji}</span>
                  <span className="font-medium text-gray-800">{lang.label}</span>
                  {language === lang.value && <span className="ml-auto text-primary-600 text-lg">✓</span>}
                </button>
              ))}
            </div>
            <div className="flex gap-3">
              <button onClick={() => setStep(1)} className="btn-secondary flex-1">← Back</button>
              <button onClick={handleSubmit} disabled={loading} className="btn-primary flex-1">{loading ? "Setting up..." : "Start Learning! 🚀"}</button>
            </div>
            {error && <div className="bg-error-50 border border-error-500/30 text-error-600 rounded-xl p-3 text-sm text-center">{error}</div>}
          </div>
        )}
      </div>
    </div>
  );
}
