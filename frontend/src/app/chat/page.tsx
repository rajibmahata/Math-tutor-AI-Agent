"use client";

import { useState, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";
import { cn } from "@/lib/utils";
import type { ChatMessage, Language } from "@/types";

// =============================================================================
// Demo Chat Component — Full real-time look and feel
// In production, this connects via WebSocket to the tutoring endpoint
// =============================================================================

interface LocalMessage {
  id: string;
  role: "student" | "teacher";
  content: string;
  type: "text" | "hint" | "solution" | "feedback" | "encouragement";
  hintLevel?: number;
  isCorrect?: boolean;
  timestamp: Date;
}

const WELCOME_MESSAGES: Record<Language, string> = {
  en: "Hi! I'm your GanitMitra math tutor. What would you like to learn today? 😊\n\nI can help you with:\n• Addition, subtraction, multiplication, division\n• Fractions and decimals\n• Algebra and geometry\n• And much more!\n\nJust ask me a question or pick a topic!",
  hi: "नमस्ते! मैं आपका GanitMitra गणित टीचर हूँ। आज क्या सीखना चाहोगे? 😊\n\nमैं आपकी मदद कर सकता हूँ:\n• जोड़, घटाव, गुणा, भाग\n• भिन्न और दशमलव\n• बीजगणित और ज्यामिति\n• और बहुत कुछ!\n\nबस अपना सवाल पूछो!",
  bn: "নমস্কার! আমি তোমার GanitMitra গণিত শিক্ষক। আজ কী শিখতে চাও? 😊\n\nআমি সাহায্য করতে পারি:\n• যোগ, বিয়োগ, গুণ, ভাগ\n• ভগ্নাংশ ও দশমিক\n• বীজগণিত ও জ্যামিতি\n• আরও অনেক কিছু!\n\nশুধু প্রশ্ন করো!",
};

export default function ChatPage() {
  const router = useRouter();
  const [messages, setMessages] = useState<LocalMessage[]>([]);
  const [input, setInput] = useState("");
  const [language, setLanguage] = useState<Language>("en");
  const [loading, setLoading] = useState(false);
  const [hintLevel, setHintLevel] = useState(1);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Welcome message
    const welcome: LocalMessage = {
      id: "welcome",
      role: "teacher",
      content: WELCOME_MESSAGES[language],
      type: "text",
      timestamp: new Date(),
    };
    setMessages([welcome]);
  }, [language]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const studentMsg: LocalMessage = {
      id: Date.now().toString(),
      role: "student",
      content: input,
      type: "text",
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, studentMsg]);
    setInput("");
    setLoading(true);

    // Simulate AI response (in production: WebSocket)
    await new Promise((r) => setTimeout(r, 800 + Math.random() * 1200));

    const isMathQuestion = /[\d+\-×÷=]|what is|how much|calculate|solve|find|kitna|कितना|কত/.test(
      input.toLowerCase()
    );

    if (isMathQuestion) {
      // Give a hint
      const hint = generateHintMessage(input, hintLevel, language);
      const teacherMsg: LocalMessage = {
        id: (Date.now() + 1).toString(),
        role: "teacher",
        content: hint,
        type: "hint",
        hintLevel,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, teacherMsg]);
      setHintLevel((h) => Math.min(h + 1, 3));
    } else {
      const teacherMsg: LocalMessage = {
        id: (Date.now() + 1).toString(),
        role: "teacher",
        content: getChatResponse(input, language),
        type: "text",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, teacherMsg]);
    }

    setLoading(false);
  };

  const requestHint = async () => {
    const nextLevel = hintLevel;
    setLoading(true);
    await new Promise((r) => setTimeout(r, 600));
    const hint = getFallbackHint(nextLevel, language);
    const msg: LocalMessage = {
      id: Date.now().toString(),
      role: "teacher",
      content: hint,
      type: "hint",
      hintLevel: nextLevel,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, msg]);
    setHintLevel((h) => Math.min(h + 1, 4));
    setLoading(false);
  };

  const requestSolution = async () => {
    setLoading(true);
    await new Promise((r) => setTimeout(r, 1000));
    const steps = getStepByStepSolution(language);
    const msg: LocalMessage = {
      id: Date.now().toString(),
      role: "teacher",
      content: steps,
      type: "solution",
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, msg]);
    setLoading(false);
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-100 safe-area-top">
        <div className="flex items-center justify-between px-4 py-3">
          <button onClick={() => router.push("/dashboard")} className="btn-ghost text-sm flex items-center gap-1">
            ← Back
          </button>
          <div className="text-center">
            <h1 className="font-heading font-bold text-gray-800">GanitMitra</h1>
            <p className="text-xs text-gray-400">Your math friend</p>
          </div>
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value as Language)}
            className="text-sm bg-gray-50 rounded-lg px-2 py-1 border-0"
          >
            <option value="en">🇬🇧 EN</option>
            <option value="hi">🇮🇳 हिंदी</option>
            <option value="bn">🇧🇩 বাংলা</option>
          </select>
        </div>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}

        {loading && (
          <div className="flex items-start gap-3">
            <span className="text-2xl">🧑‍🏫</span>
            <div className="bg-white border border-gray-200 rounded-2xl rounded-bl-md px-4 py-3">
              <div className="flex gap-1">
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
              </div>
            </div>
          </div>
        )}

        <div ref={chatEndRef} />
      </div>

      {/* Action Buttons */}
      <div className="px-4 pb-2 flex gap-2">
        <button
          onClick={requestHint}
          disabled={loading || hintLevel > 3}
          className="btn-secondary text-sm flex-1 disabled:opacity-50"
        >
          💡 Hint {hintLevel > 3 ? "(used)" : `(${hintLevel}/3)`}
        </button>
        <button
          onClick={requestSolution}
          disabled={loading}
          className="btn-secondary text-sm flex-1"
        >
          📖 Solution
        </button>
      </div>

      {/* Input */}
      <div className="px-4 pb-4 safe-area-bottom">
        <div className="flex gap-2">
          <button className="btn-ghost text-xl px-3">🎤</button>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            placeholder={
              language === "hi"
                ? "अपना सवाल पूछो..."
                : language === "bn"
                ? "তোমার প্রশ্ন জিজ্ঞাসা করো..."
                : "Ask your math question..."
            }
            className="input-field flex-1"
            disabled={loading}
          />
          <button
            onClick={sendMessage}
            disabled={loading || !input.trim()}
            className="btn-primary px-4"
          >
            ▶
          </button>
        </div>
      </div>
    </div>
  );
}

function MessageBubble({ message }: { message: LocalMessage }) {
  const isStudent = message.role === "student";

  if (isStudent) {
    return (
      <div className="flex items-start gap-3 flex-row-reverse">
        <span className="text-2xl">👩‍🎓</span>
        <div className="chat-bubble-student">{message.content}</div>
      </div>
    );
  }

  const typeStyles = {
    text: "chat-bubble-teacher",
    hint: "chat-bubble-hint",
    solution: "chat-bubble-teacher",
    feedback: message.isCorrect ? "chat-bubble-success" : "chat-bubble-teacher",
    encouragement: "chat-bubble-success",
  };

  return (
    <div className="flex items-start gap-3">
      <span className="text-2xl">🧑‍🏫</span>
      <div className={cn(typeStyles[message.type] || "chat-bubble-teacher")}>
        {message.type === "hint" && (
          <div className="flex items-center gap-1 text-xs text-primary-500 mb-1">
            <span>💡</span>
            <span>Hint {message.hintLevel} of 3</span>
          </div>
        )}
        {message.type === "solution" && (
          <div className="flex items-center gap-1 text-xs text-primary-500 mb-1">
            <span>📖</span>
            <span>Step-by-Step Solution</span>
          </div>
        )}
        <p className="whitespace-pre-wrap text-sm leading-relaxed">{message.content}</p>
      </div>
    </div>
  );
}

// =============================================================================
// Response generation helpers (simulated — in production these are LLM calls)
// =============================================================================

function generateHintMessage(question: string, level: number, lang: Language): string {
  const hints: Record<number, Record<Language, string>> = {
    1: {
      en: "Let me help you think about this. First, identify what operation you need — are you adding, subtracting, multiplying, or dividing? Look at the numbers and the question carefully. What do you think is the first step? 🤔",
      hi: "चलो इसके बारे में सोचते हैं। सबसे पहले पहचानो कि कौन सी गणित क्रिया चाहिए — जोड़, घटाव, गुणा या भाग? संख्याओं और सवाल को ध्यान से देखो। पहला कदम क्या होगा? 🤔",
      bn: "চলো এটা নিয়ে ভাবি। প্রথমে চিহ্নিত করো কোন গণিত অপারেশন দরকার — যোগ, বিয়োগ, গুণ না ভাগ? সংখ্যা আর প্রশ্ন ভালো করে দেখো। প্রথম ধাপ কী হবে? 🤔",
    },
    2: {
      en: "Great thinking! Now, try breaking this down. If you're multiplying, think of it as repeated addition. If dividing, think of equal sharing. Can you try writing out the first calculation? You're getting closer! 💪",
      hi: "बहुत अच्छा! अब इसे छोटे हिस्सों में तोड़ो। गुणा है तो बार-बार जोड़ के रूप में सोचो। भाग है तो बराबर बाँटने के रूप में। पहला हिसाब लिखकर देखो। करीब हो! 💪",
      bn: "দারুণ! এখন এটাকে ছোট অংশে ভাগ করো। গুণ হলে বারবার যোগ হিসেবে ভাবো। ভাগ হলে সমান ভাগ হিসেবে ভাবো। প্রথম হিসাবটা লিখে দেখো। একদম কাছাকাছি! 💪",
    },
    3: {
      en: "You're almost there! Here's the key insight: when you see this pattern, the answer should be around ___. Try to work it out now — I believe you can do it! Share your answer and I'll check it. ✨",
      hi: "बस करीब हो! यहाँ मुख्य बात है: जब ऐसा पैटर्न दिखे, तो जवाब लगभग ___ होना चाहिए। अब खुद निकालकर देखो — मुझे विश्वास है तुम कर सकते हो! अपना जवाब बताओ, मैं जाँचूँगा। ✨",
      bn: "একদম কাছাকাছি! মূল বিষয়টা হলো: যখন এরকম প্যাটার্ন দেখবে, উত্তর প্রায় ___ হওয়া উচিত। এখন নিজে বের করো — আমার বিশ্বাস তুমি পারবে! উত্তর জানাও, আমি চেক করবো। ✨",
    },
  };

  return hints[level]?.[lang] || hints[1].en;
}

function getFallbackHint(level: number, lang: Language): string {
  // If no prior question context, use generic hints
  const generic: Record<number, Record<Language, string>> = {
    1: {
      en: "Think about what mathematical operation you need. Are you combining numbers (addition), taking away (subtraction), grouping (multiplication), or sharing (division)?",
      hi: "सोचो कि कौन सी गणित क्रिया चाहिए। संख्याओं को जोड़ना है, घटाना है, गुणा करना है, या बाँटना है?",
      bn: "ভাবো কোন গণিত অপারেশন দরকার। সংখ্যা যোগ করবে, বিয়োগ করবে, গুণ করবে, না ভাগ করবে?",
    },
    2: {
      en: "Try writing down what you know. What information is given? What are you being asked to find? Break it into smaller parts.",
      hi: "जो जानते हो उसे लिखो। क्या जानकारी दी गई है? क्या पूछा जा रहा है? छोटे-छोटे हिस्सों में तोड़ो।",
      bn: "যা জানো তা লিখে ফেলো। কী তথ্য দেওয়া আছে? কী জানতে চাওয়া হচ্ছে? ছোট ছোট অংশে ভাগ করো।",
    },
    3: {
      en: "Nearly there! The answer involves using the operation you identified. Try calculating step by step and share your answer with me!",
      hi: "बस करीब हो! जवाब में वही क्रिया लगेगी जो तुमने पहचानी। कदम-दर-कदम हिसाब लगाओ और मुझे बताओ!",
      bn: "একদম শেষ ধাপে! যে অপারেশন চিহ্নিত করেছো সেটাই ব্যবহার করো। ধাপে ধাপে হিসাব করো আর আমাকে জানাও!",
    },
  };

  return generic[level]?.[lang] || generic[1].en;
}

function getStepByStepSolution(lang: Language): string {
  const solutions: Record<Language, string> = {
    en: `Let me show you how to solve this step by step:

**Step 1:** Read the problem carefully and identify what's given.
**Step 2:** Choose the right operation (+, -, ×, ÷).
**Step 3:** Set up the problem: write the numbers in the correct order.
**Step 4:** Calculate carefully, checking each step.
**Step 5:** Verify your answer by working backwards.

This is the general approach for any math problem. If you share a specific problem, I can show you the exact steps! 📝`,
    hi: `चलो कदम-दर-कदम हल करते हैं:

**कदम 1:** सवाल को ध्यान से पढ़ो और समझो कि क्या दिया गया है।
**कदम 2:** सही गणित क्रिया चुनो (+, -, ×, ÷)।
**कदम 3:** सवाल को व्यवस्थित करो: संख्याओं को सही क्रम में लिखो।
**कदम 4:** ध्यान से हिसाब लगाओ, हर कदम जाँचते हुए।
**कदम 5:** उल्टा करके जवाब की जाँच करो।

किसी खास सवाल के लिए सटीक हल चाहिए तो मुझे बताओ! 📝`,
    bn: `চলো ধাপে ধাপে সমাধান করি:

**ধাপ ১:** সমস্যাটি ভালো করে পড়ো আর বোঝো কী দেওয়া আছে।
**ধাপ ২:** সঠিক অপারেশন বেছে নাও (+, -, ×, ÷)।
**ধাপ ৩:** সমস্যাটি সাজাও: সংখ্যাগুলো সঠিক ক্রমে লেখো।
**ধাপ ৪:** সাবধানে হিসাব করো, প্রতিটি ধাপ চেক করে।
**ধাপ ৫:** উল্টো দিক থেকে যাচাই করো।

নির্দিষ্ট কোনো সমস্যার সমাধান চাইলে আমাকে জানাও! 📝`,
  };

  return solutions[lang] || solutions.en;
}

function getChatResponse(input: string, lang: Language): string {
  const greetings: Record<Language, string> = {
    en: "Hello! Ready to do some math? What grade are you in and what topic would you like to practice?",
    hi: "नमस्ते! गणित करने के लिए तैयार? तुम कौन सी कक्षा में हो और कौन सा विषय पढ़ना चाहोगे?",
    bn: "নমস্কার! গণিত করার জন্য প্রস্তুত? তুমি কোন ক্লাসে পড়ো আর কোন বিষয় অনুশীলন করতে চাও?",
  };

  if (/hi|hello|hey|नमस्ते|নমস্কার/i.test(input)) {
    return greetings[lang] || greetings.en;
  }

  if (/thank|thanks|धन्यवाद|শুভকামনা/i.test(input)) {
    return {
      en: "You're welcome! Happy to help. Keep practicing! 😊",
      hi: "कोई बात नहीं! मदद करके खुशी हुई। अभ्यास करते रहो! 😊",
      bn: "কোনো ব্যাপার না! সাহায্য করতে পেরে খুশি। অনুশীলন চালিয়ে যাও! 😊",
    }[lang] || "You're welcome! 😊";
  }

  return {
    en: "Let's work on a math problem together! What topic are you studying? I can help with addition, subtraction, multiplication, division, fractions, and more.",
    hi: "चलो मिलकर गणित का सवाल हल करें! तुम कौन सा विषय पढ़ रहे हो? मैं जोड़, घटाव, गुणा, भाग, भिन्न और बहुत कुछ में मदद कर सकता हूँ।",
    bn: "চলো একসাথে গণিতের সমস্যা সমাধান করি! তুমি কোন বিষয় পড়ছো? আমি যোগ, বিয়োগ, গুণ, ভাগ, ভগ্নাংশ আর আরও অনেক কিছুতে সাহায্য করতে পারি।",
  }[lang] || "Let's work on math together! What topic are you studying?";
}
