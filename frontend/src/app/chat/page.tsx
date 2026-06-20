"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { cn } from "@/lib/utils";
import type { Language } from "@/types";

const API = "http://localhost:8000/api";

// =============================================================================
// Multi-language content
// =============================================================================

const CONTENT: Record<Language, {
  welcome: string;
  thinking: string;
  listening: string;
  speakNow: string;
  hintLabel: string;
  solutionLabel: string;
  voiceTitle: string;
  logoutLabel: string;
  askPlaceholder: string;
  gradeTopic: string;
}> = {
  en: {
    welcome: "Hi {name}! I'm your math tutor. What would you like to learn today? 😊",
    thinking: "Thinking...",
    listening: "Listening...",
    speakNow: "Speak now...",
    hintLabel: "Hint",
    solutionLabel: "Solution",
    voiceTitle: "Voice input",
    logoutLabel: "Logout",
    askPlaceholder: "Ask a math question...",
    gradeTopic: "Ready to practice? Ask me any math question!",
  },
  hi: {
    welcome: "नमस्ते {name}! मैं आपका गणित टीचर हूँ। आज क्या सीखना चाहोगे? 😊",
    thinking: "सोच रहा हूँ...",
    listening: "सुन रहा हूँ...",
    speakNow: "अब बोलो...",
    hintLabel: "संकेत",
    solutionLabel: "हल",
    voiceTitle: "आवाज़ इनपुट",
    logoutLabel: "लॉग आउट",
    askPlaceholder: "सवाल पूछो...",
    gradeTopic: "अभ्यास के लिए तैयार? मुझसे कोई भी गणित सवाल पूछो!",
  },
  bn: {
    welcome: "নমস্কার {name}! আমি তোমার গণিত শিক্ষক। আজ কী শিখতে চাও? 😊",
    thinking: "ভাবছি...",
    listening: "শুনছি...",
    speakNow: "এখন বলো...",
    hintLabel: "ইঙ্গিত",
    solutionLabel: "সমাধান",
    voiceTitle: "ভয়েস ইনপুট",
    logoutLabel: "লগ আউট",
    askPlaceholder: "প্রশ্ন জিজ্ঞাসা করো...",
    gradeTopic: "অনুশীলনের জন্য প্রস্তুত? যেকোনো গণিত প্রশ্ন জিজ্ঞাসা করো!",
  },
};

// =============================================================================
// Chat Message type
// =============================================================================

interface ChatMsg {
  id: string;
  role: "student" | "teacher" | "system";
  content: string;
  type: "text" | "hint" | "solution" | "feedback" | "greeting" | "celebration";
  hintLevel?: number;
}

// =============================================================================
// Component
// =============================================================================

export default function ChatPage() {
  const router = useRouter();
  const [messages, setMessages] = useState<ChatMsg[]>([]);
  const [input, setInput] = useState("");
  const [language, setLanguage] = useState<Language>("en");
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [studentName, setStudentName] = useState("");
  const [hintLevel, setHintLevel] = useState(0);
  const [lastQuestion, setLastQuestion] = useState("");
  const [score, setScore] = useState(0);
  const [streak, setStreak] = useState(0);

  // Voice state
  const [isRecording, setIsRecording] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);
  const t = CONTENT[language];

  // Init
  useEffect(() => {
    const tkn = localStorage.getItem("access_token");
    const fullName = localStorage.getItem("student_name") || "";
    const firstName = fullName.split(" ")[0];
    setToken(tkn);
    setStudentName(firstName);
    addMessage("teacher", t.welcome.replace("{name}", name || ""), "greeting");
    if (tkn) initSession(tkn);
    
    // Check for pending question from dashboard
    const pending = localStorage.getItem("pending_question");
    if (pending) {
      localStorage.removeItem("pending_question");
      setTimeout(() => processMessage(pending), 1000);
    }
  }, []);

  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

  const addMessage = (role: ChatMsg["role"], content: string, type: ChatMsg["type"], hintLevel?: number) => {
    setMessages((p) => [...p, { id: `${role}${Date.now()}${Math.random()}`, role, content, type, hintLevel }]);
  };

  const initSession = async (tkn: string) => {
    try {
      const res = await fetch(`${API}/tutoring/sessions`, {
        method: "POST", headers: { "Content-Type": "application/json", Authorization: `Bearer ${tkn}` },
        body: JSON.stringify({ session_type: "tutoring", language }),
      });
      if (res.ok) { const d = await res.json(); setSessionId(d.id); }
    } catch {}
  };

  const apiCall = useCallback(async (endpoint: string, body: unknown) => {
    const headers: Record<string, string> = { "Content-Type": "application/json" };
    if (token) headers["Authorization"] = `Bearer ${token}`;
    const res = await fetch(`${API}${endpoint}`, { method: "POST", headers, body: JSON.stringify(body) });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  }, [token]);

  // =========================================================================
  // Logout
  // =========================================================================
  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("student_name");
    router.push("/login");
  };

  // =========================================================================
  // Voice: Speech-to-Text
  // =========================================================================
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream, { mimeType: "audio/webm" });
      mediaRecorderRef.current = recorder;
      audioChunksRef.current = [];

      recorder.ondataavailable = (e) => { if (e.data.size > 0) audioChunksRef.current.push(e.data); };
      recorder.onstop = async () => {
        stream.getTracks().forEach((t) => t.stop());
        setIsRecording(false);
        const blob = new Blob(audioChunksRef.current, { type: "audio/webm" });
        await transcribeAudio(blob);
      };
      recorder.start();
      setIsRecording(true);
    } catch (err) {
      alert("Microphone access needed for voice input");
    }
  };

  const stopRecording = () => {
    mediaRecorderRef.current?.stop();
  };

  const transcribeAudio = async (blob: Blob) => {
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append("audio", blob, "recording.webm");
      formData.append("language", language);
      const headers: Record<string, string> = {};
      if (token) headers["Authorization"] = `Bearer ${token}`;
      const res = await fetch(`${API}/voice/stt`, { method: "POST", headers, body: formData });
      if (res.ok) {
        const data = await res.json();
        setInput(data.text);
        // Auto-send after transcription
        setTimeout(() => processMessage(data.text), 500);
      } else {
        addMessage("system", "Voice not recognized. Please type instead.", "text");
      }
    } catch {
      addMessage("system", "Voice service unavailable. Please type.", "text");
    }
    setLoading(false);
  };

  // =========================================================================
  // Voice: Text-to-Speech
  // =========================================================================
  const speakText = async (text: string) => {
    try {
      const headers: Record<string, string> = { "Content-Type": "application/json" };
      if (token) headers["Authorization"] = `Bearer ${token}`;
      const res = await fetch(`${API}/voice/tts`, {
        method: "POST", headers,
        body: JSON.stringify({ text, language, voice_style: "natural" }),
      });
      if (res.ok) {
        const audioBlob = await res.blob();
        const url = URL.createObjectURL(audioBlob);
        if (!audioRef.current) {
          audioRef.current = new Audio();
          audioRef.current.onended = () => setIsSpeaking(false);
        }
        audioRef.current.src = url;
        setIsSpeaking(true);
        audioRef.current.play();
      }
    } catch {}
  };

  // =========================================================================
  // Message Processing
  // =========================================================================
  const sendMessage = () => {
    if (!input.trim() || loading) return;
    processMessage(input.trim());
    setInput("");
  };

  const processMessage = async (content: string) => {
    addMessage("student", content, "text");
    setLoading(true);

    // Detect math question or answer
    const isNumericAnswer = /^-?\d+\.?\d*$/.test(content) || /^=\s*-?\d+/.test(content);
    const isMathQuestion = /[\d+\-×÷*/()]|what is|calculate|solve|find|evaluate|how much|kitna|कितना|কত/.test(content.toLowerCase())
      || /\b(add|subtract|multiply|divide|addition|subtraction|multiplication|division|fraction|algebra|geometry|जोड़|घटाव|गुणा|भाग|যোগ|বিয়োগ|গুণ|ভাগ)\b/.test(content.toLowerCase());

    if (isNumericAnswer && hintLevel > 0) {
      await handleAnswer(content);
    } else if (isMathQuestion) {
      await handleMathQuestion(content);
    } else {
      await handleGreeting(content);
    }
    setLoading(false);
  };

  const handleMathQuestion = async (content: string) => {
    setLastQuestion(content);
    setHintLevel(1);

    // Try API first
    if (sessionId && token) {
      try {
        const data = await apiCall("/tutoring/chat", { session_id: sessionId, message: content, language, action: "hint", hint_level: 1 });
        const hintText = data.content;
        addMessage("teacher", hintText, "hint", 1);
        if (!isSpeaking) speakText(hintText);
        return;
      } catch {}
    }
    // Local smart fallback
    const hint = generateSmartHint(content, 1, language);
    addMessage("teacher", `💡 ${hint}`, "hint", 1);
  };

  const handleAnswer = async (content: string) => {
    if (sessionId && token) {
      try {
        const data = await apiCall("/tutoring/chat", { session_id: sessionId, message: content, language, action: "evaluate", question: lastQuestion });
        addMessage("teacher", data.content, "feedback");
        setHintLevel(0);
        return;
      } catch {}
    }
    const evaluation = evaluateAnswerSmart(lastQuestion, content, language);
    addMessage("teacher", evaluation.text, evaluation.correct ? "celebration" : "feedback");
    if (evaluation.correct) {
      setScore((s) => s + 10);
      setStreak((s) => s + 1);
      if (streak + 1 >= 3) addMessage("system", `🔥 ${streak + 1}-question streak! Amazing!`, "celebration");
    } else {
      setStreak(0);
    }
    setHintLevel(0);
  };

  const handleGreeting = async (content: string) => {
    if (sessionId && token) {
      try {
        const data = await apiCall("/tutoring/chat", { session_id: sessionId, message: content, language, action: "greeting" });
        addMessage("teacher", data.content, "greeting");
        return;
      } catch {}
    }
    addMessage("teacher", t.gradeTopic, "greeting");
  };

  const requestHint = async () => {
    if (hintLevel >= 3 || !lastQuestion) return;
    const level = hintLevel + 1;
    if (sessionId && token) {
      try {
        const data = await apiCall("/tutoring/chat", { session_id: sessionId, message: lastQuestion, language, action: "hint", hint_level: level });
        addMessage("teacher", data.content, "hint", level);
        setHintLevel(level);
        return;
      } catch {}
    }
    const hint = generateSmartHint(lastQuestion, level, language);
    addMessage("teacher", `💡 ${t.hintLabel} ${level}/3: ${hint}`, "hint", level);
    setHintLevel(level);
  };

  const requestSolution = async () => {
    if (sessionId && token) {
      try {
        const data = await apiCall("/tutoring/chat", { session_id: sessionId, message: lastQuestion, language, action: "solution" });
        addMessage("teacher", data.content, "solution");
        return;
      } catch {}
    }
    const steps = generateSolutionSmart(lastQuestion, language);
    addMessage("teacher", steps, "solution");
  };

  // =========================================================================
  // Render
  // =========================================================================

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-100">
        <div className="flex items-center justify-between px-4 py-3">
          <button onClick={() => router.push("/dashboard")} className="btn-ghost text-sm">← Back</button>
          <div className="text-center flex items-center gap-2">
            <span className="text-xl">🧮</span>
            <h1 className="font-heading font-bold text-gray-800 text-sm">GanitMitra</h1>
          </div>
          <div className="flex items-center gap-1">
            <select value={language} onChange={(e) => {
              const lang = e.target.value as Language;
              setLanguage(lang);
              addMessage("teacher", CONTENT[lang].welcome.replace("{name}", studentName || ""), "greeting");
            }} className="text-xs bg-gray-50 rounded-lg px-1.5 py-1 border-0">
              <option value="en">EN</option><option value="hi">हिं</option><option value="bn">বাং</option>
            </select>
            <button onClick={logout} className="btn-ghost text-xs text-error-500">{t.logoutLabel}</button>
          </div>
        </div>
        {/* Score bar */}
        <div className="px-4 pb-2 flex items-center gap-3 text-xs text-gray-500">
          <span>⭐ {score} pts</span>
          {streak > 0 && <span className="text-warning-500">🔥 {streak} streak</span>}
        </div>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
        {messages.map((msg) => (
          <div key={msg.id} className={`flex items-start gap-3 ${msg.role === "student" ? "flex-row-reverse" : ""}`}>
            <span className="text-2xl">{msg.role === "student" ? "👩‍🎓" : msg.role === "system" ? "🎯" : "🧑‍🏫"}</span>
            <div className={cn(
              msg.role === "student" ? "chat-bubble-student" :
              msg.type === "hint" ? "chat-bubble-hint" :
              msg.type === "celebration" ? "chat-bubble-success animate-bounce-in" :
              msg.type === "feedback" ? "chat-bubble-teacher" : "chat-bubble-teacher",
              "max-w-[80%]"
            )}>
              {msg.type === "hint" && msg.hintLevel && (
                <div className="text-xs text-primary-500 mb-1">💡 {t.hintLabel} {msg.hintLevel}/3</div>
              )}
              <p className="whitespace-pre-wrap text-sm leading-relaxed">{msg.content}</p>
              {/* Speak button on teacher messages */}
              {msg.role === "teacher" && (
                <button onClick={() => speakText(msg.content)} className="mt-1 text-xs text-gray-400 hover:text-primary-500" title="Read aloud">
                  {isSpeaking ? "🔊" : "🔈"}
                </button>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex items-start gap-3">
            <span className="text-2xl">🧑‍🏫</span>
            <div className="bg-white border border-gray-200 rounded-2xl rounded-bl-md px-4 py-3">
              <div className="flex items-center gap-2 text-sm text-gray-400">
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:0ms]" />
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:150ms]" />
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:300ms]" />
                <span className="ml-1">{t.thinking}</span>
              </div>
            </div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      {/* Action buttons */}
      <div className="px-4 pb-2 flex gap-2">
        <button onClick={requestHint} disabled={hintLevel >= 3 || loading || !lastQuestion} className="btn-secondary text-xs flex-1 disabled:opacity-40">
          💡 {t.hintLabel} {hintLevel >= 3 ? "(used)" : `(${3 - hintLevel} left)`}
        </button>
        <button onClick={requestSolution} disabled={loading || !lastQuestion} className="btn-secondary text-xs flex-1">📖 {t.solutionLabel}</button>
      </div>

      {/* Input bar */}
      <div className="px-4 pb-4">
        <div className="flex gap-2 items-center">
          {/* Voice button */}
          <button
            onClick={isRecording ? stopRecording : startRecording}
            className={cn("btn-ghost text-xl px-3 py-3 rounded-full transition-all", isRecording && "bg-error-100 text-error-500 animate-pulse")}
            title={t.voiceTitle}
          >
            {isRecording ? "⏹️" : "🎤"}
          </button>
          {isRecording && <span className="text-xs text-error-500 animate-pulse">{t.listening}</span>}
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            placeholder={isRecording ? t.speakNow : t.askPlaceholder}
            className="input-field flex-1 text-sm"
            disabled={loading || isRecording}
          />
          <button onClick={sendMessage} disabled={loading || isRecording || !input.trim()} className="btn-primary px-4 rounded-full">▶</button>
        </div>
      </div>
    </div>
  );
}

// =============================================================================
// Smart math evaluation (client-side for offline/fallback)
// =============================================================================

function computeExpected(question: string): number | null {
  const clean = question.replace(/\?/g, "").replace(/what is|calculate|find|solve|evaluate|kitna|कितना|কত/gi, "").trim();
  const arithMatch = clean.match(/(-?\d+\.?\d*)\s*([+\-×*/x])\s*(-?\d+\.?\d*)/i);
  if (arithMatch) {
    const a = parseFloat(arithMatch[1]), b = parseFloat(arithMatch[3]);
    const op = arithMatch[2].replace(/×|x/i, "*");
    switch (op) {
      case "+": return a + b;
      case "-": return a - b;
      case "*": return Math.round(a * b * 100) / 100;
      case "/": return b !== 0 ? Math.round((a / b) * 100) / 100 : null;
    }
  }
  const wordMatch = clean.match(/(\d+).*?(\d+)/);
  if (wordMatch && /bag|group|each|total|apple|book|candy/.test(clean.toLowerCase())) {
    return parseFloat(wordMatch[1]) * parseFloat(wordMatch[2]);
  }
  return null;
}

function evaluateAnswerSmart(question: string, answer: string, lang: Language) {
  const clean = answer.replace(/^=\s*/, "").trim();
  const expected = computeExpected(question);

  if (expected !== null) {
    const userNum = parseFloat(clean);
    if (!isNaN(userNum) && Math.abs(userNum - expected) < 0.001) {
      return { correct: true, text: lang === "en" ? `⭐ Correct! ${expected}. Brilliant! +10 points! 🎉` : lang === "hi" ? `⭐ सही! ${expected}. शानदार! +10 पॉइंट्स! 🎉` : `⭐ সঠিক! ${expected}. চমৎকার! +10 পয়েন্ট! 🎉` };
    }
    if (!isNaN(userNum) && Math.abs(userNum - expected) < expected * 0.2) {
      return { correct: false, text: lang === "en" ? `Close! You said ${clean} but the answer is ${expected}. Almost there! 💪` : lang === "hi" ? `करीब! आपने ${clean} कहा, जवाब ${expected} है। बस थोड़ा और! 💪` : `কাছাকাছি! তুমি ${clean} বলেছো, উত্তর ${expected}। আরেকটু! 💪` };
    }
  }
  return { correct: false, text: lang === "en" ? "Good effort! Let me show you the solution. 📝" : lang === "hi" ? "अच्छी कोशिश! चलो हल दिखाता हूँ। 📝" : "ভালো প্রচেষ্টা! সমাধান দেখাচ্ছি। 📝" };
}

function generateSmartHint(question: string, level: number, lang: Language): string {
  const expected = computeExpected(question);
  const hints: Record<number, Record<Language, string>> = {
    1: { en: "Let's identify the operation. Look at the numbers — what math do we need?",
         hi: "क्रिया पहचानो। संख्याओं को देखो — कौन सा गणित चाहिए?",
         bn: "অপারেশন চিহ্নিত করো। সংখ্যাগুলো দেখো — কোন গণিত দরকার?" },
    2: { en: expected ? `Try writing the calculation. The answer will be around ${Math.round(expected * 0.8)} to ${Math.round(expected * 1.2)}.` : "Break it into smaller steps. What's the first thing to calculate?",
         hi: expected ? `हिसाब लिखकर देखो। जवाब लगभग ${Math.round(expected * 0.8)} से ${Math.round(expected * 1.2)} के बीच होगा।` : "छोटे कदमों में तोड़ो। सबसे पहले क्या निकालोगे?",
         bn: expected ? `হিসাব লিখে দেখো। উত্তর প্রায় ${Math.round(expected * 0.8)} থেকে ${Math.round(expected * 1.2)} এর মধ্যে হবে।` : "ছোট ধাপে ভাগ করো। প্রথমে কী বের করবে?" },
    3: { en: expected ? `You're almost there! Try it now — what do you get? 🌟` : "Last hint — apply the operation and share your answer! ✨",
         hi: expected ? `बस करीब हो! अभी कोशिश करो — क्या मिला? 🌟` : "आखिरी संकेत — क्रिया लगाओ और जवाब बताओ! ✨",
         bn: expected ? `একদম কাছাকাছি! এখন চেষ্টা করো — কী পেলে? 🌟` : "শেষ ইঙ্গিত — অপারেশন প্রয়োগ করো আর উত্তর জানাও! ✨" },
  };
  return hints[level]?.[lang] || hints[1].en;
}

function generateSolutionSmart(question: string, lang: Language): string {
  const expected = computeExpected(question);
  if (expected !== null) {
    const match = question.match(/(-?\d+\.?\d*)\s*([+\-×*/x])\s*(-?\d+\.?\d*)/i);
    if (match) {
      const a = match[1], op = match[2], b = match[3];
      const opNames: Record<string, Record<string, string>> = {
        en: { "+": "addition", "-": "subtraction", "*": "multiplication", "×": "multiplication", "/": "division" },
        hi: { "+": "जोड़", "-": "घटाव", "*": "गुणा", "×": "गुणा", "/": "भाग" },
        bn: { "+": "যোগ", "-": "বিয়োগ", "*": "গুণ", "×": "গুণ", "/": "ভাগ" },
      };
      const opName = (opNames[lang] || opNames.en)[op] || "operation";
      return lang === "en"
        ? `📖 **Step 1:** Identify — this is ${opName}.\n**Step 2:** Write — ${a} ${op} ${b}\n**Step 3:** Calculate — ${a} ${op} ${b} = ${expected}\n**Step 4:** Answer — ${expected} ✅`
        : lang === "hi"
        ? `📖 **कदम 1:** पहचान — यह ${opName} है।\n**कदम 2:** लिखो — ${a} ${op} ${b}\n**कदम 3:** हिसाब — ${a} ${op} ${b} = ${expected}\n**कदम 4:** जवाब — ${expected} ✅`
        : `📖 **ধাপ ১:** চিহ্নিত — এটি ${opName}।\n**ধাপ ২:** লেখো — ${a} ${op} ${b}\n**ধাপ ৩:** হিসাব — ${a} ${op} ${b} = ${expected}\n**ধাপ ৪:** উত্তর — ${expected} ✅`;
    }
  }
  return lang === "en" ? "📖 **Step 1:** Read carefully.\n**Step 2:** Choose operation (+, −, ×, ÷).\n**Step 3:** Calculate step by step.\n**Step 4:** Check backwards.\n\nShare a specific problem for exact steps! 📝"
    : lang === "hi" ? "📖 **कदम 1:** ध्यान से पढ़ो।\n**कदम 2:** क्रिया चुनो (+, −, ×, ÷)।\n**कदम 3:** कदम-दर-कदम हिसाब।\n**कदम 4:** उल्टा जाँचो।\n\nसटीक हल के लिए कोई खास सवाल बताओ! 📝"
    : "📖 **ধাপ ১:** ভালো করে পড়ো।\n**ধাপ ২:** অপারেশন বেছে নাও (+, −, ×, ÷)।\n**ধাপ ৩:** ধাপে ধাপে হিসাব।\n**ধাপ ৪:** উল্টো দিক থেকে যাচাই।\n\nসঠিক সমাধানের জন্য নির্দিষ্ট সমস্যা জানাও! 📝";
}
