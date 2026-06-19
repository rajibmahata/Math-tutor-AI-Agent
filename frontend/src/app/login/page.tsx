"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store";
import { authLogin } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const login = useAuthStore((s) => s.login);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault(); setError(""); setLoading(true);
    try {
      const data = await authLogin(email, password);
      login(data.user, data.access_token, data.refresh_token);
      const r = data.user.role;
      if (r === "tutor") router.push("/tutor");
      else if (r === "principal") router.push("/principal");
      else if (r === "admin") router.push("/admin");
      else router.push("/dashboard");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally { setLoading(false); }
  };

  return (
    <main className="flex-1 flex flex-col items-center justify-center p-6 bg-gradient-to-b from-primary-50 to-white">
      <div className="w-full max-w-xs">
        <div className="text-center mb-8">
          <div className="text-5xl mb-3">🧮</div>
          <h1 className="text-2xl font-heading font-extrabold text-primary-700">VidyaMitra</h1>
          <p className="text-sm text-gray-400 mt-1">Welcome back!</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {error && <div className="bg-red-50 border border-red-200 text-red-600 rounded-xl p-3 text-xs text-center">{error}</div>}
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} className="input-field" placeholder="Email" required />
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} className="input-field" placeholder="Password" required minLength={8} />
          <button type="submit" disabled={loading} className="btn-primary w-full text-base py-3.5 rounded-2xl">{loading ? "Signing in..." : "Sign In →"}</button>
          <p className="text-center text-xs text-gray-400">New here?{" "}<Link href="/signup" className="text-primary-600 font-medium">Create account</Link></p>
        </form>
      </div>
    </main>
  );
}
