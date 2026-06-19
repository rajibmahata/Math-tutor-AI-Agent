"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { apiRequest } from "@/lib/utils";
import type { Language, Grade } from "@/types";

const LANGUAGES: { value: Language; label: string; emoji: string }[] = [
  { value: "en", label: "English", emoji: "🇬🇧" },
  { value: "hi", label: "हिंदी", emoji: "🇮🇳" },
  { value: "bn", label: "বাংলা", emoji: "🇧🇩" },
];

const GRADES: { value: Grade; label: string }[] = [
  { value: "N", label: "Nursery (Age 3-4)" },
  { value: "KG", label: "Kindergarten (Age 4-5)" },
  { value: "1", label: "Class 1 (Age 5-6)" },
  { value: "2", label: "Class 2 (Age 6-7)" },
  { value: "3", label: "Class 3 (Age 7-8)" },
  { value: "4", label: "Class 4 (Age 8-9)" },
  { value: "5", label: "Class 5 (Age 9-10)" },
  { value: "6", label: "Class 6 (Age 10-11)" },
  { value: "7", label: "Class 7 (Age 11-12)" },
  { value: "8", label: "Class 8 (Age 12-13)" },
  { value: "9", label: "Class 9 (Age 13-14)" },
  { value: "10", label: "Class 10 (Age 14-15)" },
];

export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [age, setAge] = useState(8);
  const [grade, setGrade] = useState<Grade>("3");
  const [language, setLanguage] = useState<Language>("en");
  const [board, setBoard] = useState("ncert");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async () => {
    setLoading(true);
    setError("");
    try {
      await apiRequest("/students", {
        method: "POST",
        body: JSON.stringify({ age, grade, preferred_language: language, board }),
      });
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message || "Failed to create profile");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-primary-50 to-white">
      <div className="w-full max-w-md">
        {step === 1 && (
          <div className="card space-y-6 animate-bounce-in">
            <div className="text-center">
              <div className="text-5xl mb-4">📝</div>
              <h2 className="text-2xl font-heading font-bold text-gray-800">
                Tell us about yourself
              </h2>
              <p className="text-gray-500 mt-1">We'll personalize your learning</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                How old are you?
              </label>
              <input
                type="number"
                value={age}
                onChange={(e) => setAge(Number(e.target.value))}
                className="input-field"
                min={3}
                max={16}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Your Grade
              </label>
              <select
                value={grade}
                onChange={(e) => setGrade(e.target.value as Grade)}
                className="input-field"
              >
                {GRADES.map((g) => (
                  <option key={g.value} value={g.value}>
                    {g.label}
                  </option>
                ))}
              </select>
            </div>

            <button
              onClick={() => setStep(2)}
              disabled={!age || !grade}
              className="btn-primary w-full"
            >
              Continue →
            </button>
          </div>
        )}

        {step === 2 && (
          <div className="card space-y-6 animate-bounce-in">
            <div className="text-center">
              <div className="text-5xl mb-4">🌐</div>
              <h2 className="text-2xl font-heading font-bold text-gray-800">
                Choose your language
              </h2>
              <p className="text-gray-500 mt-1">Learn math in your preferred language</p>
            </div>

            <div className="space-y-3">
              {LANGUAGES.map((lang) => (
                <button
                  key={lang.value}
                  onClick={() => setLanguage(lang.value)}
                  className={`w-full rounded-xl px-4 py-4 text-left flex items-center gap-4 transition-colors ${
                    language === lang.value
                      ? "bg-primary-100 border-2 border-primary-500"
                      : "bg-gray-50 border-2 border-transparent hover:bg-gray-100"
                  }`}
                >
                  <span className="text-2xl">{lang.emoji}</span>
                  <span className="font-medium text-gray-800">{lang.label}</span>
                  {language === lang.value && (
                    <span className="ml-auto text-primary-600">✓</span>
                  )}
                </button>
              ))}
            </div>

            <div className="flex gap-3">
              <button onClick={() => setStep(1)} className="btn-secondary flex-1">
                ← Back
              </button>
              <button
                onClick={handleSubmit}
                disabled={loading}
                className="btn-primary flex-1"
              >
                {loading ? "Setting up..." : "Start Learning! →"}
              </button>
            </div>

            {error && (
              <div className="bg-error-50 border border-error-500/30 text-error-600 rounded-xl p-3 text-sm text-center">
                {error}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
