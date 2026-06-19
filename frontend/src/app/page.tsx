export default function HomePage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8">
      <div className="text-center max-w-lg animate-bounce-in">
        {/* Logo */}
        <div className="mb-8 text-7xl">🧮</div>

        <h1 className="text-4xl font-heading font-extrabold text-primary-700 mb-4">
          GanitMitra
        </h1>
        <p className="text-2xl font-heading font-semibold text-gray-600 mb-2">
          गणित मित्र · গণিত মিত্র
        </p>
        <p className="text-lg text-gray-500 mb-8">
          Your AI Math Friend — Learning in English, Hindi & Bengali
        </p>

        {/* Status — Production Ready */}
        <div className="card mb-8">
          <div className="flex items-center gap-3 justify-center">
            <span className="relative flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-success-500 opacity-75" />
              <span className="relative inline-flex rounded-full h-3 w-3 bg-success-500" />
            </span>
            <span className="text-sm text-gray-500">v1.0 — Production Ready</span>
          </div>
        </div>

        {/* Quick Links */}
        <div className="flex flex-wrap gap-3 justify-center">
          <a href="/login" className="btn-primary">
            Start Learning →
          </a>
          <a href="/signup" className="btn-secondary">
            Create Account
          </a>
        </div>

        {/* Features */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-12">
          <div className="card text-center">
            <div className="text-3xl mb-2">🧑‍🏫</div>
            <h3 className="font-semibold text-gray-700">8 AI Agents</h3>
            <p className="text-sm text-gray-500">Specialized tutoring</p>
          </div>
          <div className="card text-center">
            <div className="text-3xl mb-2">🌐</div>
            <h3 className="font-semibold text-gray-700">3 Languages</h3>
            <p className="text-sm text-gray-500">EN · हिंदी · বাংলা</p>
          </div>
          <div className="card text-center">
            <div className="text-3xl mb-2">📊</div>
            <h3 className="font-semibold text-gray-700">Nursery to 10</h3>
            <p className="text-sm text-gray-500">Full K-10 math</p>
          </div>
        </div>

        {/* More Features */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-4">
          <div className="card text-center py-3">
            <div className="text-xl mb-1">🎤</div>
            <p className="text-xs text-gray-500">Voice Ready</p>
          </div>
          <div className="card text-center py-3">
            <div className="text-xl mb-1">🔐</div>
            <p className="text-xs text-gray-500">Secure Auth</p>
          </div>
          <div className="card text-center py-3">
            <div className="text-xl mb-1">📊</div>
            <p className="text-xs text-gray-500">Progress Tracking</p>
          </div>
          <div className="card text-center py-3">
            <div className="text-xl mb-1">👨‍👩‍👧</div>
            <p className="text-xs text-gray-500">Parent Reports</p>
          </div>
        </div>

        {/* Footer */}
        <p className="text-xs text-gray-400 mt-12">
          <a href="https://github.com/rajibmahata/Math-tutor-AI-Agent" target="_blank" rel="noopener noreferrer" className="hover:text-primary-500 transition-colors">
            GitHub
          </a>
          {" · "}
          <a href="http://localhost:8000/api/docs" target="_blank" rel="noopener noreferrer" className="hover:text-primary-500 transition-colors">
            API Docs
          </a>
        </p>
      </div>
    </main>
  );
}
