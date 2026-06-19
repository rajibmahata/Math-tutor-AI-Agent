"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store";
import { authSignup } from "@/lib/api";

export default function SignupPage() {
  const router = useRouter();
  const login = useAuthStore((s) => s.login);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<"student" | "tutor" | "principal" | "parent">("student");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const data = await authSignup(email, password, name, role);
      login(data.user, data.access_token, data.refresh_token);
      if (role === "tutor") router.push("/tutor");
      else if (role === "principal") router.push("/principal");
      else if (role === "student") router.push("/onboarding");
      else router.push("/parent");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Signup failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-primary-50 to-white">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="text-6xl mb-4">🧮</div>
          <h1 className="text-3xl font-heading font-extrabold text-primary-700">Join GanitMitra</h1>
          <p className="text-gray-500 mt-2">Your personal math tutor</p>
        </div>
        <form onSubmit={handleSubmit} className="card space-y-4">
          {error && <div className="bg-error-50 border border-error-500/30 text-error-600 rounded-xl p-3 text-sm text-center">{error}</div>}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">I am a...</label>
            <div className="grid grid-cols-2 gap-2">
              {(["student", "tutor", "principal", "parent"] as const).map((r) => (
                <button key={r} type="button" onClick={() => setRole(r)}
                  className={`rounded-xl px-3 py-3 text-center text-sm font-medium transition-colors ${role === r ? "bg-primary-600 text-white" : "bg-gray-100 text-gray-600 hover:bg-gray-200"}`}>
                  {r === "student" ? "👩‍🎓 Student" : r === "tutor" ? "👨‍🏫 Tutor" : r === "principal" ? "👨‍💼 Principal" : "👨‍👩‍👧 Parent"}
                </button>
              ))}
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
            <input type="text" value={name} onChange={(e) => setName(e.target.value)} className="input-field" placeholder="Riya Sharma" required />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} className="input-field" placeholder="riya@example.com" required />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} className="input-field" placeholder="Min 8 characters" required minLength={8} />
          </div>
          <button type="submit" disabled={loading} className="btn-primary w-full">{loading ? "Creating account..." : "Create Account →"}</button>
          <p className="text-center text-sm text-gray-500">Already learning?{" "}<Link href="/login" className="text-primary-600 font-medium hover:underline">Sign in</Link></p>
        </form>
      </div>
    </div>
  );
}
