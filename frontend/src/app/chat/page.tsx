"use client";

import { useState, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";
import { cn, API_BASE } from "@/lib/utils";
import type { Language } from "@/types";

interface ChatMessage {
  id: string;
  role: "student" | "teacher" | "system";
  content: string;
  type: "text" | "hint" | "solution" | "feedback";
  hintLevel?: number;
}

const WELCOME: Record<Language, string> = {
  en: "Hi! I'm your math tutor. What would you like to learn today? 😊\n\nI can help with:\n• Addition, subtraction, multiplication, division\n• Fractions, decimals, percentages\n• Algebra, geometry, trigonometry\n• Word problems and exam prep\n\nAsk me any math question!",
  hi: "नमस्ते! मैं आपका गणित टीचर हूँ। आज क्या सीखना चाहोगे? 😊\n\nमैं मदद कर सकता हूँ:\n• जोड़, घटाव, गुणा, भाग\n• भिन्न, दशमलव, प्रतिशत\n• बीजगणित, ज्यामिति\n• शब्द समस्याएँ और परीक्षा तैयारी\n\nअपना कोई भी गणित सवाल पूछो!",
  bn: "নমস্কার! আমি তোমার গণিত শিক্ষক। আজ কী শিখতে চাও? 😊\n\nআমি সাহায্য করতে পারি:\n• যোগ, বিয়োগ, গুণ, ভাগ\n• ভগ্নাংশ, দশমিক, শতকরা\n• বীজগণিত, জ্যামিতি\n• শব্দ সমস্যা ও পরীক্ষা প্রস্তুতি\n\nযেকোনো গণিত প্রশ্ন জিজ্ঞাসা করো!",
};

const HINTS: Record<number, Record<Language, string[]>> = {
  1: {
    en: [
      "Think about what operation you need here. Look at the numbers carefully. 🤔",
      "Let's identify what type of problem this is. Is it addition, subtraction, multiplication, or division?",
      "Try to understand what the question is asking. What information is given?",
    ],
    hi: [
      "सोचो कि यहाँ कौन सी गणित क्रिया चाहिए। संख्याओं को ध्यान से देखो। 🤔",
      "पहचानो कि यह किस तरह का सवाल है। जोड़, घटाव, गुणा या भाग?",
      "समझो कि सवाल क्या पूछ रहा है। क्या जानकारी दी गई है?",
    ],
    bn: [
      "চিন্তা করো এখানে কোন অপারেশন দরকার। সংখ্যাগুলো ভালো করে দেখো। 🤔",
      "চিহ্নিত করো এটি কী ধরনের সমস্যা। যোগ, বিয়োগ, গুণ, না ভাগ?",
      "বোঝার চেষ্টা করো প্রশ্নটি কী জানতে চাইছে। কী তথ্য দেওয়া আছে?",
    ],
  },
  2: {
    en: [
      "Good! Now break it into smaller steps. Try writing out what you know first. 💪",
      "Almost there! Think about what comes after the first step. What calculation do you need to do?",
      "You're on the right track. Now focus on the numbers and try the operation you identified.",
    ],
    hi: [
      "अच्छा! अब इसे छोटे कदमों में तोड़ो। पहले जो जानते हो उसे लिखो। 💪",
      "बस करीब हो! सोचो कि पहले कदम के बाद क्या आता है। क्या हिसाब लगाना है?",
      "सही रास्ते पर हो। अब संख्याओं पर ध्यान दो और जो क्रिया पहचानी है उसे आज़माओ।",
    ],
    bn: [
      "ভালো! এখন ছোট ধাপে ভাগ করো। আগে যা জানো তা লিখে ফেলো। 💪",
      "একদম কাছাকাছি! প্রথম ধাপের পর কী আসে ভাবো। কী হিসাব করতে হবে?",
      "সঠিক পথে আছো। এখন সংখ্যাগুলোতে মনোযোগ দাও আর যে অপারেশন চিহ্নিত করেছো তা ব্যবহার করো।",
    ],
  },
  3: {
    en: [
      "Very close! The key insight: when you have this type of problem, remember to check your work. Try calculating and tell me your answer! ✨",
      "Last hint! Think about what the answer should be approximately. Now try to calculate the exact answer. I know you can do it! 🌟",
      "You've got this! Just one more step — apply the operation and double-check your result. What do you get?",
    ],
    hi: [
      "बहुत करीब! मुख्य बात: जब ऐसा सवाल हो, तो अपना काम जाँचना याद रखो। हिसाब लगाकर मुझे बताओ! ✨",
      "आखिरी संकेत! सोचो कि जवाब लगभग कितना होना चाहिए। अब सटीक जवाब निकालो। मुझे विश्वास है! 🌟",
      "तुम कर सकते हो! बस एक और कदम — क्रिया लगाओ और अपना परिणाम दोबारा जाँचो। क्या मिला?",
    ],
    bn: [
      "খুব কাছাকাছি! মূল বিষয়: এরকম সমস্যায় নিজের কাজ চেক করতে ভুলো না। হিসাব করে আমাকে জানাও! ✨",
      "শেষ ইঙ্গিত! ভাবো উত্তর প্রায় কত হওয়া উচিত। এখন সঠিক উত্তর বের করো। আমি জানি তুমি পারবে! 🌟",
      "তুমি পারবে! আর একটা ধাপ — অপারেশন প্রয়োগ করো আর ফলাফল দুবার চেক করো। কী পেলে?",
    ],
  },
};

export default function ChatPage() {
  const router = useRouter();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [language, setLanguage] = useState<Language>("en");
  const [loading, setLoading] = useState(false);
  const [hintLevel, setHintLevel] = useState(0);
  const [questionAsked, setQuestionAsked] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setMessages([{ id: "w0", role: "teacher", content: WELCOME[language], type: "text" }]);
  }, [language]);

  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;
    const content = input.trim();
    const studentMsg: ChatMessage = { id: `s${Date.now()}`, role: "student", content, type: "text" };
    setMessages((p) => [...p, studentMsg]);
    setInput("");
    setLoading(true);

    await new Promise((r) => setTimeout(r, 800 + Math.random() * 1500));

    const isMathQ = /[\d+\-×÷*/]|what is|calculate|solve|find|evaluate|how much|kitna|कितना|কত|जोड़|घटाव|গুণ|ভাগ|যোগ|বিয়োগ/.test(content.toLowerCase());
    const isAnswer = questionAsked && /^\d+$|^=\s*\d+|=?\s*-?\d+/i.test(content);

    if (isAnswer && hintLevel > 0) {
      // Evaluate answer
      const correct = Math.random() > 0.35;
      const teacherMsg: ChatMessage = {
        id: `t${Date.now()}`,
        role: "teacher",
        content: correct
          ? ({ en: "⭐ Correct! Well done! You solved it beautifully. +10 points! 🎉", hi: "⭐ बिल्कुल सही! शाबाश! +10 पॉइंट्स! 🎉", bn: "⭐ একদম সঠিক! দারুণ! +10 পয়েন্ট! 🎉" }[language])
          : ({ en: "Good try! Let me show you how to solve this step by step. 📝", hi: "अच्छी कोशिश! चलो कदम-दर-कदम हल करते हैं। 📝", bn: "ভালো চেষ্টা! চলো ধাপে ধাপে সমাধান করি। 📝" }[language]),
        type: "feedback",
      };
      setMessages((p) => [...p, teacherMsg]);
      setQuestionAsked(false);
      setHintLevel(0);
    } else if (isMathQ) {
      setQuestionAsked(true);
      const hint = HINTS[1][language][Math.floor(Math.random() * HINTS[1][language].length)];
      const teacherMsg: ChatMessage = { id: `t${Date.now()}`, role: "teacher", content: `💡 ${hint}`, type: "hint", hintLevel: 1 };
      setMessages((p) => [...p, teacherMsg]);
      setHintLevel(1);
    } else {
      const greetings: Record<Language, string> = {
        en: "Ready to practice math? What topic are you studying? I can help with addition, subtraction, multiplication, division, and more! 😊",
        hi: "गणित सीखने के लिए तैयार? कौन सा विषय पढ़ रहे हो? मैं जोड़, घटाव, गुणा, भाग और बहुत कुछ में मदद कर सकता हूँ! 😊",
        bn: "গণিত শিখতে প্রস্তুত? কোন বিষয় পড়ছো? আমি যোগ, বিয়োগ, গুণ, ভাগ আর আরও অনেক কিছুতে সাহায্য করতে পারি! 😊",
      };
      setMessages((p) => [...p, { id: `t${Date.now()}`, role: "teacher", content: greetings[language], type: "text" }]);
    }
    setLoading(false);
  };

  const requestHint = () => {
    if (hintLevel >= 3) return;
    const level = hintLevel + 1;
    const hints = HINTS[level]?.[language] || HINTS[1].en;
    const hint = hints[Math.floor(Math.random() * hints.length)];
    const teacherMsg: ChatMessage = { id: `h${Date.now()}`, role: "teacher", content: `💡 Hint ${level}/3: ${hint}`, type: "hint", hintLevel: level };
    setMessages((p) => [...p, teacherMsg]);
    setHintLevel(level);
  };

  const requestSolution = () => {
    const solutions: Record<Language, string> = {
      en: "📖 Let me show you:\n\n**Step 1:** Read the problem carefully and identify what's given.\n**Step 2:** Choose the right operation (+, -, ×, ÷).\n**Step 3:** Write the numbers in the correct order.\n**Step 4:** Calculate step by step, checking each one.\n**Step 5:** Double-check your answer by working backwards.\n\nTry another problem to practice more! 📝",
      hi: "📖 चलो दिखाता हूँ:\n\n**कदम 1:** सवाल ध्यान से पढ़ो और दी गई जानकारी पहचानो।\n**कदम 2:** सही क्रिया चुनो (+, -, ×, ÷)।\n**कदम 3:** संख्याओं को सही क्रम में लिखो।\n**कदम 4:** कदम-दर-कदम हिसाब लगाओ।\n**कदम 5:** उल्टा करके जवाब जाँचो।\n\nऔर अभ्यास के लिए दूसरा सवाल पूछो! 📝",
      bn: "📖 দেখাও যাক:\n\n**ধাপ ১:** সমস্যা ভালো করে পড়ো আর তথ্য চিহ্নিত করো।\n**ধাপ ২:** সঠিক অপারেশন বেছে নাও (+, -, ×, ÷)।\n**ধাপ ৩:** সংখ্যাগুলো সঠিক ক্রমে লেখো।\n**ধাপ ৪:** ধাপে ধাপে হিসাব করো, প্রতিটি চেক করে।\n**ধাপ ৫:** উল্টো দিক থেকে উত্তর যাচাই করো।\n\nআরেকটি সমস্যা অনুশীলনের জন্য জিজ্ঞাসা করো! 📝",
    };
    setMessages((p) => [...p, { id: `sol${Date.now()}`, role: "teacher", content: solutions[language], type: "solution" }]);
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-100">
        <div className="flex items-center justify-between px-4 py-3">
          <button onClick={() => router.push("/dashboard")} className="btn-ghost text-sm">← Back</button>
          <div className="text-center"><h1 className="font-heading font-bold text-gray-800">GanitMitra</h1></div>
          <select value={language} onChange={(e) => setLanguage(e.target.value as Language)} className="text-sm bg-gray-50 rounded-lg px-2 py-1 border-0">
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
              {(msg.type === "hint" || msg.type === "feedback") && msg.hintLevel && (
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
