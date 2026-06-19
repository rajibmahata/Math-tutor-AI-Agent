"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { cn } from "@/lib/utils";

interface QuizQuestion {
  question_number: number;
  question_text: string;
  hints: string[];
  difficulty: number;
}

// Demo quiz for UI — in production this comes from /api/v1/practice/generate
const DEMO_QUIZ: QuizQuestion[] = [
  { question_number: 1, question_text: "What is 8 × 7?", hints: ["Think of repeated addition", "8 + 8 + 8... 7 times", "Count by 8s: 8, 16, 24..."], difficulty: 0.4 },
  { question_number: 2, question_text: "A shopkeeper has 6 bags with 9 apples each. How many apples total?", hints: ["This is a multiplication problem", "6 groups of 9 apples", "6 × 9 = ?"], difficulty: 0.5 },
  { question_number: 3, question_text: "What is 56 ÷ 8?", hints: ["Think about sharing equally", "How many groups of 8 make 56?", "Count by 8s until you reach 56"], difficulty: 0.5 },
  { question_number: 4, question_text: "What is 45 + 38?", hints: ["Add the ones first: 5 + 8 = 13", "Carry the 1 to tens place", "Then add tens: 4 + 3 + 1"], difficulty: 0.35 },
  { question_number: 5, question_text: "What is 7 × 6?", hints: ["7 groups of 6", "6 × 7 is the same as 7 × 6", "Try skip-counting by 6"], difficulty: 0.4 },
  { question_number: 6, question_text: "If you have ₹50 and buy a notebook for ₹32, how much is left?", hints: ["This is subtraction", "50 - 32 = ?", "Subtract ones then tens"], difficulty: 0.4 },
  { question_number: 7, question_text: "What is 9 × 8?", hints: ["9 groups of 8", "10 × 8 = 80, subtract 8", "72 is close"], difficulty: 0.45 },
  { question_number: 8, question_text: "What is 100 - 67?", hints: ["Subtract 60 first: 100 - 60 = 40", "Then subtract 7: 40 - 7 = ?", "Check your tens and ones"], difficulty: 0.4 },
  { question_number: 9, question_text: "What is 12 × 5?", hints: ["12 × 10 = 120, half is?", "5 groups of 12", "12 + 12 + 12 + 12 + 12"], difficulty: 0.3 },
  { question_number: 10, question_text: "What is 84 ÷ 12?", hints: ["How many 12s in 84?", "12 × 7 = ?", "Count by 12s"], difficulty: 0.55 },
];

export default function PracticePage() {
  const router = useRouter();
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answer, setAnswer] = useState("");
  const [answers, setAnswers] = useState<(string | null)[]>(new Array(10).fill(null));
  const [results, setResults] = useState<(boolean | null)[]>(new Array(10).fill(null));
  const [hintsShown, setHintsShown] = useState<number[]>([]);
  const [quizComplete, setQuizComplete] = useState(false);
  const [hintUsed, setHintUsed] = useState(0);
  const [loading, setLoading] = useState(false);

  const question = DEMO_QUIZ[currentQuestion];
  const progress = ((currentQuestion + (answer ? 0.5 : 0)) / DEMO_QUIZ.length) * 100;

  const handleSubmit = () => {
    if (!answer.trim()) return;
    setLoading(true);

    // Simulate evaluation
    setTimeout(() => {
      const isCorrect = checkAnswer(currentQuestion, answer);
      const newAnswers = [...answers];
      const newResults = [...results];
      newAnswers[currentQuestion] = answer;
      newResults[currentQuestion] = isCorrect;
      setAnswers(newAnswers);
      setResults(newResults);

      if (currentQuestion < DEMO_QUIZ.length - 1) {
        setCurrentQuestion(currentQuestion + 1);
        setAnswer("");
        setHintsShown([]);
        setHintUsed(0);
      } else {
        setQuizComplete(true);
      }
      setLoading(false);
    }, 600);
  };

  const showHint = () => {
    if (hintUsed < 3 && question) {
      setHintsShown([...hintsShown, hintUsed]);
      setHintUsed(hintUsed + 1);
    }
  };

  const score = results.filter((r) => r === true).length;

  if (quizComplete) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-primary-50 to-white">
        <div className="w-full max-w-md text-center card animate-bounce-in">
          <div className="text-6xl mb-4">
            {score >= 8 ? "🎉" : score >= 5 ? "👍" : "💪"}
          </div>
          <h1 className="text-2xl font-heading font-bold text-gray-800 mb-2">
            Practice Complete!
          </h1>
          <div className="text-5xl font-extrabold text-primary-600 my-4">
            {score} / 10
          </div>
          <div className="w-full bg-gray-100 rounded-full h-4 mb-4">
            <div
              className={cn(
                "h-4 rounded-full transition-all duration-1000",
                score >= 8 ? "bg-success-500" : score >= 5 ? "bg-warning-500" : "bg-error-500"
              )}
              style={{ width: `${score * 10}%` }}
            />
          </div>
          <p className="text-gray-500 mb-2">{score * 10}% Accuracy</p>
          <p className="text-gray-500 mb-6">
            {score >= 8
              ? "Excellent work! You're mastering this! ⭐"
              : score >= 5
              ? "Good effort! Keep practicing! 📝"
              : "Keep trying! Every mistake is a learning opportunity! 💪"}
          </p>

          <div className="space-y-3 mb-6">
            <h3 className="font-semibold text-gray-700 text-left">Review:</h3>
            {DEMO_QUIZ.map((q, i) => (
              <div key={i} className="flex items-center gap-3 text-left">
                <span>{results[i] ? "✅" : "❌"}</span>
                <span className="text-sm text-gray-600">
                  Q{i + 1}: {answers[i] || "—"} {!results[i] && answers[i] && `(correct: ${getCorrectAnswer(i)})`}
                </span>
              </div>
            ))}
          </div>

          <div className="flex gap-3">
            <button onClick={() => router.push("/dashboard")} className="btn-secondary flex-1">
              Dashboard
            </button>
            <button
              onClick={() => {
                setCurrentQuestion(0);
                setAnswer("");
                setAnswers(new Array(10).fill(null));
                setResults(new Array(10).fill(null));
                setQuizComplete(false);
              }}
              className="btn-primary flex-1"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-100">
        <div className="flex items-center justify-between px-4 py-3">
          <button onClick={() => router.push("/dashboard")} className="btn-ghost text-sm">
            ← Back
          </button>
          <h1 className="font-heading font-bold text-gray-800">Practice Quiz</h1>
          <span className="text-sm text-gray-400">
            {currentQuestion + 1}/{DEMO_QUIZ.length}
          </span>
        </div>
        <div className="w-full bg-gray-100 h-1">
          <div
            className="bg-primary-500 h-1 transition-all duration-500"
            style={{ width: `${progress}%` }}
          />
        </div>
      </header>

      {/* Question */}
      <main className="flex-1 flex flex-col items-center justify-center p-6">
        <div className="w-full max-w-lg">
          <div className="card mb-6">
            <p className="text-xs text-gray-400 mb-2">
              Question {currentQuestion + 1} • Difficulty: {"⭐".repeat(Math.ceil(question.difficulty * 3))}
            </p>
            <h2 className="text-xl font-heading font-bold text-gray-800 mb-4">
              {question.question_text}
            </h2>

            {/* Hints */}
            {hintsShown.map((hintIdx) => (
              <div
                key={hintIdx}
                className="bg-primary-50 border border-primary-200 rounded-xl p-3 mb-2 animate-bounce-in"
              >
                <p className="text-sm text-primary-700">
                  💡 <span className="font-medium">Hint {hintIdx + 1}:</span>{" "}
                  {question.hints[hintIdx]}
                </p>
              </div>
            ))}
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Your Answer:
            </label>
            <input
              type="text"
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
              className="input-field text-lg"
              placeholder="Type your answer..."
              autoFocus
              disabled={loading}
            />
          </div>

          <div className="flex gap-3">
            <button
              onClick={showHint}
              disabled={hintUsed >= 3 || loading}
              className="btn-secondary flex-1 text-sm disabled:opacity-40"
            >
              💡 Hint {hintUsed >= 3 ? "(used)" : `(${3 - hintUsed} left)`}
            </button>
            <button
              onClick={handleSubmit}
              disabled={!answer.trim() || loading}
              className="btn-primary flex-1"
            >
              {loading ? "Checking..." : "Submit →"}
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}

function checkAnswer(qIdx: number, answer: string): boolean {
  const correctAnswers = ["56", "54", "7", "83", "42", "18", "72", "33", "60", "7"];
  const userAnswer = answer.trim().replace(/\s+/g, "");
  const correct = correctAnswers[qIdx];

  // Fuzzy match: accept equivalent forms
  if (userAnswer === correct) return true;
  if (parseInt(userAnswer) === parseInt(correct)) return true;

  // Check for "= answer" pattern
  const eqMatch = userAnswer.match(/=\s*(\d+)/);
  if (eqMatch && eqMatch[1] === correct) return true;

  return false;
}

function getCorrectAnswer(qIdx: number): string {
  return ["56", "54", "7", "83", "42", "18", "72", "33", "60", "7"][qIdx];
}
