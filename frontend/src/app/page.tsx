export default function HomePage() {
  return (
    <main className="flex-1 flex flex-col items-center justify-center p-6 bg-gradient-to-b from-primary-50 to-white">
      <div className="text-center animate-bounce-in">
        <div className="text-6xl mb-6">🧮</div>
        <h1 className="text-3xl font-heading font-extrabold text-primary-700 mb-2">VidyaMitra</h1>
        <p className="text-base font-heading font-semibold text-gray-500 mb-1">विद्या मित्र · বিদ্যা মিত্র</p>
        <p className="text-sm text-gray-400 mb-8">AI Student Tutor Platform</p>

        {/* Status */}
        <div className="inline-flex items-center gap-2 bg-white rounded-full px-4 py-2 shadow-sm border border-gray-100 mb-8">
          <span className="relative flex h-2.5 w-2.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-500 opacity-75" />
            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-green-500" />
          </span>
          <span className="text-xs font-medium text-gray-500">v2.0 — Production Ready</span>
        </div>

        <div className="flex flex-col gap-3 w-full max-w-xs mx-auto">
          <a href="/signup" className="btn-primary text-base py-3.5">Get Started Free →</a>
          <a href="/login" className="btn-secondary text-base py-3.5">Sign In</a>
        </div>

        {/* Features */}
        <div className="grid grid-cols-2 gap-3 mt-8 w-full max-w-xs mx-auto">
          {[
            { icon: "🧑‍🏫", title: "12 AI Agents" },
            { icon: "👨‍🏫", title: "Tutor Verified" },
            { icon: "🌐", title: "4 Languages" },
            { icon: "🎤", title: "Voice Ready" },
          ].map((f) => (
            <div key={f.title} className="bg-white rounded-2xl p-3 shadow-sm border border-gray-100 text-center">
              <div className="text-2xl mb-1">{f.icon}</div>
              <p className="text-xs font-medium text-gray-600">{f.title}</p>
            </div>
          ))}
        </div>

        <div className="flex gap-4 justify-center mt-6">
          <a href="/demo" className="text-xs text-primary-500 hover:underline">📱 Demo</a>
          <a href="/tutor" className="text-xs text-teal-600 hover:underline">👨‍🏫 Tutor</a>
          <a href="/admin" className="text-xs text-slate-600 hover:underline">⚡ Admin</a>
        </div>
      </div>
    </main>
  );
}
