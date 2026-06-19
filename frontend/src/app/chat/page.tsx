"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { cn } from "@/lib/utils";
import type { Language } from "@/types";

const API = "http://localhost:8000/api/v1";

const WELCOME: Record<Language, string> = {
  en: "Hi {name}! I'm your math tutor. What would you like to learn today? 😊",
  hi: "नमस्ते {name}! मैं आपका गणित टीचर हूँ। आज क्या सीखना चाहोगे? 😊",
  bn: "নমস্কার {name}! আমি তোমার গণিত শিক্ষক। আজ কী শিখতে চাও? 😊",
};

interface ChatMsg {
  id: string;
  role: "student" | "teacher";
  content: string;
  type: "text" | "hint" | "solution" | "feedback" | "greeting";
  hintLevel?: number;
}

export default function ChatPage() {
  const router = useRouter();
  const [messages, setMessages] = useState<ChatMsg[]>([]);
  const [input, setInput] = useState("");
  const [language, setLanguage] = useState<Language>("en");
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [hintLevel, setHintLevel] = useState(0);
  const [lastQuestion, setLastQuestion] = useState("");
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Get token + student info on mount
  useEffect(() => {
    const t = localStorage.getItem("access_token");
    const name = localStorage.getItem("student_name") || "";
    setToken(t);
    const welcome = WELCOME[language];
    setMessages([{ id: "w0", role: "teacher", content: name ? welcome.replace("{name}", name) : welcome.replace("{name}, ", "").replace(" {name}!", "!"), type: "greeting" }]);
    
    // Load student name from API if not cached
    if (t && !name) {
      (async () => {
        try {
          const res = await fetch(`${API}/auth/me`, { headers: { Authorization: `Bearer ${t}` } });
          if (res.ok) {
            const user = await res.json();
            localStorage.setItem("student_name", user.full_name);
          }
        } catch {}
      })();
    }
  }, []);

  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

  // Start session when token available
  useEffect(() => {
    if (!token) return;
    (async () => {
      try {
        const res = await fetch(`${API}/tutoring/sessions`, {
          method: "POST",
          headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
          body: JSON.stringify({ session_type: "tutoring", language }),
        });
        if (res.ok) {
          const data = await res.json();
          setSessionId(data.id);
        }
      } catch {}
    })();
  }, [token]);

  const apiCall = useCallback(async (endpoint: string, body: unknown) => {
    const headers: Record<string, string> = { "Content-Type": "application/json" };
    if (token) headers["Authorization"] = `Bearer ${token}`;
    const res = await fetch(`${API}${endpoint}`, { method: "POST", headers, body: JSON.stringify(body) });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  }, [token]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;
    const content = input.trim();
    const studentMsg: ChatMsg = { id: `s${Date.now()}`, role: "student", content, type: "text" };
    setMessages((p) => [...p, studentMsg]);
    setInput("");
    setLoading(true);

    // Detect if this looks like a math answer (number/numeric response to a previous question)
    const isNumericAnswer = /^-?\d+\.?\d*$/.test(content) || /^=\s*-?\d+/.test(content);
    const isMathQuestion = /[\d+\-×÷*/()]|what is|calculate|solve|find|evaluate|how much|kitna|कितना|কত/.test(content.toLowerCase())
      || /\b(add|subtract|multiply|divide|addition|subtraction|multiplication|division|fraction|algebra|geometry|जोड़|घटाव|गुणा|भाग|যোগ|বিয়োগ|গুণ|ভাগ)\b/.test(content.toLowerCase());

    if (isNumericAnswer && hintLevel > 0) {
      // This is likely an answer to a previous question — evaluate it
      await handleAnswer(content);
    } else if (isMathQuestion) {
      // This is a new math question — get AI hint
      await handleMathQuestion(content);
    } else {
      // Greeting or general chat — get AI greeting
      await handleGreeting(content);
    }
    setLoading(false);
  };

  const handleMathQuestion = async (content: string) => {
    setLastQuestion(content);
    setHintLevel(1);

    if (sessionId && token) {
      try {
        const data = await apiCall("/tutoring/chat", {
          session_id: sessionId,
          message: content,
          language,
          action: "hint",
          hint_level: 1,
        });
        setMessages((p) => [...p, { id: `t${Date.now()}`, role: "teacher", content: data.content, type: "hint", hintLevel: 1 }]);
        return;
      } catch { /* fall through to local */ }
    }

    // Local fallback hints with real math
    const hints = generateRealHint(content, 1, language);
    setMessages((p) => [...p, { id: `t${Date.now()}`, role: "teacher", content: `💡 ${hints}`, type: "hint", hintLevel: 1 }]);
  };

  const handleAnswer = async (content: string) => {
    if (sessionId && token) {
      try {
        const data = await apiCall("/tutoring/chat", {
          session_id: sessionId,
          message: content,
          language,
          action: "evaluate",
        });
        setMessages((p) => [...p, { id: `t${Date.now()}`, role: "teacher", content: data.content, type: "feedback" }]);
        setHintLevel(0);
        return;
      } catch { /* fall through */ }
    }

    // Local evaluation
    const evaluation = evaluateAnswer(lastQuestion, content, language);
    setMessages((p) => [...p, { id: `t${Date.now()}`, role: "teacher", content: evaluation, type: "feedback" }]);
    setHintLevel(0);
  };

  const handleGreeting = async (content: string) => {
    if (sessionId && token) {
      try {
        const data = await apiCall("/tutoring/chat", {
          session_id: sessionId,
          message: content,
          language,
          action: "greeting",
        });
        setMessages((p) => [...p, { id: `t${Date.now()}`, role: "teacher", content: data.content, type: "greeting" }]);
        return;
      } catch { /* fall through */ }
    }
    setMessages((p) => [...p, { id: `t${Date.now()}`, role: "teacher", content: getLocalGreeting(language), type: "greeting" }]);
  };

  const requestHint = async () => {
    if (hintLevel >= 3) return;
    const level = hintLevel + 1;

    if (sessionId && token) {
      try {
        const data = await apiCall("/tutoring/chat", { session_id: sessionId, message: lastQuestion, language, action: "hint", hint_level: level });
        setMessages((p) => [...p, { id: `h${Date.now()}`, role: "teacher", content: data.content, type: "hint", hintLevel: level }]);
        setHintLevel(level);
        return;
      } catch {}
    }

    const hint = generateRealHint(lastQuestion, level, language);
    setMessages((p) => [...p, { id: `h${Date.now()}`, role: "teacher", content: `💡 Hint ${level}/3: ${hint}`, type: "hint", hintLevel: level }]);
    setHintLevel(level);
  };

  const requestSolution = async () => {
    if (sessionId && token) {
      try {
        const data = await apiCall("/tutoring/chat", { session_id: sessionId, message: lastQuestion, language, action: "solution" });
        setMessages((p) => [...p, { id: `sol${Date.now()}`, role: "teacher", content: data.content, type: "solution" }]);
        return;
      } catch {}
    }
    const steps = generateSolution(lastQuestion, language);
    setMessages((p) => [...p, { id: `sol${Date.now()}`, role: "teacher", content: steps, type: "solution" }]);
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-100">
        <div className="flex items-center justify-between px-4 py-3">
          <button onClick={() => router.push("/dashboard")} className="btn-ghost text-sm">← Back</button>
          <div className="text-center"><h1 className="font-heading font-bold text-gray-800">GanitMitra</h1></div>
          <select value={language} onChange={(e) => { const lang = e.target.value as Language; setLanguage(lang); const name = localStorage.getItem("student_name") || ""; const w = WELCOME[lang]; setMessages([{ id: "w0", role: "teacher", content: name ? w.replace("{name}", name) : w.replace("{name}, ", "").replace(" {name}!", "!"), type: "greeting" }]); }} className="text-sm bg-gray-50 rounded-lg px-2 py-1 border-0">
            <option value="en">🇬🇧 EN</option><option value="hi">🇮🇳 हिंदी</option><option value="bn">🇧🇩 বাংলা</option>
          </select>
        </div>
      </header>

      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
        {messages.map((msg) => (
          <div key={msg.id} className={`flex items-start gap-3 ${msg.role === "student" ? "flex-row-reverse" : ""}`}>
            <span className="text-2xl">{msg.role === "student" ? "👩‍🎓" : "🧑‍🏫"}</span>
            <div className={cn(
              msg.role === "student" ? "chat-bubble-student" : msg.type === "hint" ? "chat-bubble-hint" : msg.type === "feedback" ? "chat-bubble-success" : "chat-bubble-teacher",
              "max-w-[80%]"
            )}>
              {(msg.type === "hint") && msg.hintLevel && (
                <div className="text-xs text-primary-500 mb-1">💡 Hint {msg.hintLevel} of 3</div>
              )}
              <p className="whitespace-pre-wrap text-sm leading-relaxed">{msg.content}</p>
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex items-start gap-3">
            <span className="text-2xl">🧑‍🏫</span>
            <div className="bg-white border border-gray-200 rounded-2xl rounded-bl-md px-4 py-3">
              <div className="flex gap-1">
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:0ms]" />
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:150ms]" />
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:300ms]" />
              </div>
            </div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      <div className="px-4 pb-2 flex gap-2">
        <button onClick={requestHint} disabled={hintLevel >= 3 || loading} className="btn-secondary text-sm flex-1 disabled:opacity-40">
          💡 Hint {hintLevel >= 3 ? "(used)" : `(${3 - hintLevel} left)`}
        </button>
        <button onClick={requestSolution} disabled={loading} className="btn-secondary text-sm flex-1">📖 Solution</button>
      </div>

      <div className="px-4 pb-4">
        <div className="flex gap-2">
          <button className="btn-ghost text-xl px-3" title="Voice input">🎤</button>
          <input type="text" value={input} onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            placeholder={language === "hi" ? "सवाल पूछो..." : language === "bn" ? "প্রশ্ন জিজ্ঞাসা করো..." : "Ask a math question..."}
            className="input-field flex-1" disabled={loading} />
          <button onClick={sendMessage} disabled={loading || !input.trim()} className="btn-primary px-4">▶</button>
        </div>
      </div>
    </div>
  );
}

// =============================================================================
// Smart local answer evaluation (when API unavailable)
// =============================================================================

function evaluateAnswer(question: string, answer: string, lang: Language): string {
  const cleanAnswer = answer.replace(/^=\s*/, "").trim();
  
  // Try to compute the expected answer
  const expected = computeExpected(question);
  
  if (expected !== null) {
    const userNum = parseFloat(cleanAnswer);
    if (!isNaN(userNum) && Math.abs(userNum - expected) < 0.001) {
      return lang === "en" ? `⭐ Correct! ${question.replace(/[?]/g, "")} = ${expected}. Well done! +10 points! 🎉`
        : lang === "hi" ? `⭐ बिल्कुल सही! ${expected}. शाबाश! +10 पॉइंट्स! 🎉`
        : `⭐ একদম সঠিক! ${expected}. দারুণ! +10 পয়েন্ট! 🎉`;
    }
    // Close but not exact
    if (!isNaN(userNum) && Math.abs(userNum - expected) < expected * 0.15) {
      return lang === "en" ? `Almost! You said ${cleanAnswer} but the answer is ${expected}. Let me show you how. 📝`
        : lang === "hi" ? `करीब! आपने ${cleanAnswer} कहा लेकिन जवाब ${expected} है। चलो दिखाता हूँ। 📝`
        : `কাছাকাছি! তুমি ${cleanAnswer} বলেছো কিন্তু উত্তর ${expected}। দেখাও যাক। 📝`;
    }
  }

  return lang === "en" ? "Good try! Let me show you the step-by-step solution. 📝"
    : lang === "hi" ? "अच्छी कोशिश! चलो कदम-दर-कदम हल दिखाता हूँ। 📝"
    : "ভালো চেষ্টা! চলো ধাপে ধাপে সমাধান দেখাই। 📝";
}

function computeExpected(question: string): number | null {
  // Extract math expression from question
  const clean = question.replace(/\?/g, "").replace(/what is|calculate|find|solve|evaluate|kitna|कितना|কত/gi, "").trim();
  
  // Direct arithmetic: "12 × 5" or "12 * 5" or "12 + 5" etc.
  const arithMatch = clean.match(/(-?\d+\.?\d*)\s*([+\-×*/x])\s*(-?\d+\.?\d*)/i);
  if (arithMatch) {
    const a = parseFloat(arithMatch[1]);
    const op = arithMatch[2].replace(/×|x/i, "*");
    const b = parseFloat(arithMatch[3]);
    switch (op) {
      case "+": return a + b;
      case "-": return a - b;
      case "*": return a * b;
      case "/": return b !== 0 ? a / b : null;
    }
  }

  // Word problems: "6 bags with 9 apples" → 6 * 9
  const wordMatch = clean.match(/(\d+).*?(\d+)/);
  if (wordMatch && /bag|group|each|total|apple|book/.test(clean.toLowerCase())) {
    return parseFloat(wordMatch[1]) * parseFloat(wordMatch[2]);
  }

  return null;
}

function generateRealHint(question: string, level: number, lang: Language): string {
  const expected = computeExpected(question);
  
  if (expected !== null) {
    const hints: Record<number, Record<Language, string>> = {
      1: {
        en: `Let's break this down. Look at the numbers and think about what operation connects them. What type of math problem is this?`,
        hi: `चलो इसे समझते हैं। संख्याओं को देखो और सोचो कि कौन सी क्रिया इन्हें जोड़ती है।`,
        bn: `চলো এটা বুঝি। সংখ্যাগুলো দেখো আর ভাবো কোন অপারেশন এদের সংযুক্ত করে।`,
      },
      2: {
        en: `Try writing the calculation in numbers. What numbers do you need to work with? What operation should you use?`,
        hi: `गणना को संख्याओं में लिखकर देखो। किन संख्याओं के साथ काम करना है? कौन सी क्रिया इस्तेमाल करोगे?`,
        bn: `হিসাবটা সংখ্যায় লিখে দেখো। কোন সংখ্যাগুলো নিয়ে কাজ করতে হবে? কোন অপারেশন ব্যবহার করবে?`,
      },
      3: {
        en: `You're almost there! The answer is around ${Math.round(expected * 0.9)}-${Math.round(expected * 1.1)}. Try calculating it and share your answer! 🌟`,
        hi: `बस करीब हो! जवाब लगभग ${Math.round(expected * 0.9)}-${Math.round(expected * 1.1)} के आसपास है। हिसाब लगाकर बताओ! 🌟`,
        bn: `একদম কাছাকাছি! উত্তর প্রায় ${Math.round(expected * 0.9)}-${Math.round(expected * 1.1)} এর আশেপাশে। হিসাব করে জানাও! 🌟`,
      },
    };
    return (hints[level]?.[lang] || hints[1].en);
  }

  return lang === "en" ? `Think about what mathematical concept applies here. What do you know about this topic?`
    : lang === "hi" ? `सोचो कि यहाँ कौन सी गणित अवधारणा लागू होती है। इस विषय के बारे में क्या जानते हो?`
    : `ভাবো এখানে কোন গণিত ধারণা প্রযোজ্য। এই বিষয় সম্পর্কে কী জানো?`;
}

function generateSolution(question: string, lang: Language): string {
  const expected = computeExpected(question);
  
  if (expected !== null) {
    const arithMatch = question.match(/(-?\d+\.?\d*)\s*([+\-×*/x])\s*(-?\d+\.?\d*)/i);
    if (arithMatch) {
      const a = parseFloat(arithMatch[1]);
      const op = arithMatch[2];
      const b = parseFloat(arithMatch[3]);
      const opName = op === "+" ? "addition" : op === "-" ? "subtraction" : op === "×" || op === "x" || op === "*" ? "multiplication" : "division";
      
      return lang === "en"
        ? `📖 Step-by-Step Solution:\n\n**Step 1:** Identify the operation — this is ${opName}.\n**Step 2:** Write the problem: ${a} ${op} ${b}\n**Step 3:** Calculate: ${a} ${op} ${b} = ${expected}\n**Step 4:** Verify: the answer is ${expected}.\n\nTry another problem to practice more! 📝`
        : lang === "hi"
        ? `📖 कदम-दर-कदम हल:\n\n**कदम 1:** क्रिया पहचानो — यह ${opName} है।\n**कदम 2:** सवाल लिखो: ${a} ${op} ${b}\n**कदम 3:** हिसाब लगाओ: ${a} ${op} ${b} = ${expected}\n**कदम 4:** जाँच: जवाब ${expected} है।\n\nऔर अभ्यास के लिए दूसरा सवाल पूछो! 📝`
        : `📖 ধাপে ধাপে সমাধান:\n\n**ধাপ ১:** অপারেশন চিহ্নিত করো — এটি ${opName}।\n**ধাপ ২:** সমস্যা লেখো: ${a} ${op} ${b}\n**ধাপ ৩:** হিসাব করো: ${a} ${op} ${b} = ${expected}\n**ধাপ ৪:** যাচাই: উত্তর ${expected}।\n\nআরেকটি সমস্যা অনুশীলনের জন্য জিজ্ঞাসা করো! 📝`;
    }
  }

  return lang === "en"
    ? "📖 Let me show you the general approach:\n\n**Step 1:** Read the problem carefully.\n**Step 2:** Identify what's given and what's asked.\n**Step 3:** Choose the right operation (+, −, ×, ÷).\n**Step 4:** Calculate step by step.\n**Step 5:** Check your answer by working backwards.\n\nShare a specific problem and I'll show you the exact steps! 📝"
    : lang === "hi"
    ? "📖 सामान्य तरीका:\n\n**कदम 1:** सवाल ध्यान से पढ़ो।\n**कदम 2:** क्या दिया है और क्या पूछा है, पहचानो।\n**कदम 3:** सही क्रिया चुनो (+, −, ×, ÷)।\n**कदम 4:** कदम-दर-कदम हिसाब लगाओ।\n**कदम 5:** उल्टा करके जवाब जाँचो।\n\nकोई खास सवाल बताओ, मैं सटीक हल दिखाऊँगा! 📝"
    : "📖 সাধারণ পদ্ধতি:\n\n**ধাপ ১:** সমস্যা ভালো করে পড়ো।\n**ধাপ ২:** কী দেওয়া আছে আর কী চাওয়া হয়েছে চিহ্নিত করো।\n**ধাপ ৩:** সঠিক অপারেশন বেছে নাও (+, −, ×, ÷)।\n**ধাপ ৪:** ধাপে ধাপে হিসাব করো।\n**ধাপ ৫:** উল্টো দিক থেকে উত্তর যাচাই করো।\n\nনির্দিষ্ট কোনো সমস্যা জানাও, আমি সঠিক সমাধান দেখাবো! 📝";
}

function getLocalGreeting(lang: Language): string {
  const greetings: Record<Language, string> = {
    en: "Ready to practice math? Ask me any question — addition, subtraction, multiplication, division, fractions, or anything else! What would you like to work on? 😊",
    hi: "गणित सीखने के लिए तैयार? मुझसे कोई भी सवाल पूछो — जोड़, घटाव, गुणा, भाग, भिन्न, या कुछ और! क्या सीखना चाहोगे? 😊",
    bn: "গণিত শিখতে প্রস্তুত? যেকোনো প্রশ্ন জিজ্ঞাসা করো — যোগ, বিয়োগ, গুণ, ভাগ, ভগ্নাংশ, বা অন্য কিছু! কী শিখতে চাও? 😊",
  };
  return greetings[lang] || greetings.en;
}
