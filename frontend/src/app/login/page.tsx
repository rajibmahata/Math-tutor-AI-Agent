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
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const data = await authLogin(email, password);
      login(data.user, data.access_token, data.refresh_token);
      router.push(data.user.role === "parent" ? "/parent" : "/dashboard");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-primary-50 to-white">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="text-6xl mb-4">🧮</div>
          <h1 className="text-3xl font-heading font-extrabold text-primary-700">GanitMitra</h1>
          <p className="text-gray-500 mt-2">Your AI Math Friend</p>
        </div>
        <form onSubmit={handleSubmit} className="card space-y-4">
          {error && <div className="bg-error-50 border border-error-500/30 text-error-600 rounded-xl p-3 text-sm text-center">{error}</div>}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} className="input-field" placeholder="demo@ganitmitra.com" required />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} className="input-field" placeholder="testpass123" required minLength={8} />
          </div>
          <button type="submit" disabled={loading} className="btn-primary w-full">{loading ? "Signing in..." : "Sign In →"}</button>
          <p className="text-center text-sm text-gray-500">
            New here?{" "}<Link href="/signup" className="text-primary-600 font-medium hover:underline">Create account</Link>
          </p>
          <div className="text-center text-xs text-gray-400">
            Demo: demo@ganitmitra.com / testpass123
          </div>
        </form>
      </div>
    </div>
  );
}
