"use client";

import { useState } from "react";
import Link from "next/link";
import { cn } from "@/lib/utils";

type Language = "en" | "hi" | "bn";

const DEMO_CONTENT: Record<Language, {
  title: string;
  subtitle: string;
  tagline: string;
  problem: string;
  hint1: string;
  hint2: string;
  hint3: string;
  answer: string;
  celebration: string;
  features: { icon: string; title: string; desc: string }[];
  ready: string;
}> = {
  en: {
    title: "GanitMitra",
    subtitle: "गणित मित्र · গণিত মিত্র",
    tagline: "Your AI Math Friend",
    problem: "What is 12 × 5?",
    hint1: "Think: 12 × 5 means adding 12 five times. Try 12 × 10 first, then what's half? 🤔",
    hint2: "12 × 10 = 120. Now try to find half of that. What operation would you use? 💪",
    hint3: "120 ÷ 2 = ? You're almost there! Multiply 12 by 5 directly if you prefer. ✨",
    answer: "60",
    celebration: "⭐ Correct! 12 × 5 = 60. Excellent work! +10 points! 🎉",
    features: [
      { icon: "🧑‍🏫", title: "8 AI Agents", desc: "Teacher, Assessment, Curriculum, Practice, Motivation, Analytics, Reports, Voice" },
      { icon: "🌐", title: "3 Languages", desc: "English, हिंदी, বাংলা — learn in your mother tongue" },
      { icon: "📊", title: "Nursery to 10", desc: "Age 3-16, full K-10 mathematics curriculum" },
      { icon: "🎤", title: "Voice Support", desc: "Speak your questions, hear the answers" },
      { icon: "🔐", title: "Secure & Private", desc: "JWT auth, COPPA-compliant, data encrypted" },
      { icon: "👨‍👩‍👧", title: "Parent Reports", desc: "Weekly progress updates, weak area alerts" },
    ],
    ready: "v1.0 — Production Ready",
  },
  hi: {
    title: "गणित मित्र",
    subtitle: "GanitMitra · গণিত মিত্র",
    tagline: "आपका AI गणित मित्र",
    problem: "12 × 5 कितना होता है?",
    hint1: "सोचो: 12 × 5 का मतलब 12 को 5 बार जोड़ना। पहले 12 × 10 करो, फिर आधा कितना होगा? 🤔",
    hint2: "12 × 10 = 120। अब इसका आधा निकालो। कौन सी क्रिया इस्तेमाल करोगे? 💪",
    hint3: "120 ÷ 2 = ? बस करीब हो! चाहो तो सीधे 12 × 5 भी कर सकते हो। ✨",
    answer: "60",
    celebration: "⭐ बिल्कुल सही! 12 × 5 = 60. शाबाश! +10 पॉइंट्स! 🎉",
    features: [
      { icon: "🧑‍🏫", title: "8 AI एजेंट", desc: "शिक्षक, मूल्यांकन, पाठ्यक्रम, अभ्यास, प्रेरणा, विश्लेषण, रिपोर्ट, आवाज़" },
      { icon: "🌐", title: "3 भाषाएँ", desc: "English, हिंदी, বাংলা — अपनी मातृभाषा में सीखें" },
      { icon: "📊", title: "नर्सरी से 10वीं", desc: "उम्र 3-16, पूरा K-10 गणित पाठ्यक्रम" },
      { icon: "🎤", title: "आवाज़ समर्थन", desc: "अपने सवाल बोलें, जवाब सुनें" },
      { icon: "🔐", title: "सुरक्षित और निजी", desc: "JWT प्रमाणीकरण, COPPA अनुरूप, डेटा एन्क्रिप्टेड" },
      { icon: "👨‍👩‍👧", title: "अभिभावक रिपोर्ट", desc: "साप्ताहिक प्रगति अपडेट, कमज़ोर क्षेत्रों की सूचना" },
    ],
    ready: "v1.0 — उत्पादन के लिए तैयार",
  },
  bn: {
    title: "গণিত মিত্র",
    subtitle: "GanitMitra · गणित मित्र",
    tagline: "তোমার AI গণিত বন্ধু",
    problem: "12 × 5 কত হয়?",
    hint1: "ভাবো: 12 × 5 মানে 12 কে 5 বার যোগ করা। আগে 12 × 10 করো, তারপর অর্ধেক কত হবে? 🤔",
    hint2: "12 × 10 = 120। এখন এর অর্ধেক বের করো। কোন অপারেশন ব্যবহার করবে? 💪",
    hint3: "120 ÷ 2 = ? একদম কাছাকাছি! চাইলে সরাসরি 12 × 5 ও করতে পারো। ✨",
    answer: "60",
    celebration: "⭐ একদম সঠিক! 12 × 5 = 60। দারুণ! +10 পয়েন্ট! 🎉",
    features: [
      { icon: "🧑‍🏫", title: "8 AI এজেন্ট", desc: "শিক্ষক, মূল্যায়ন, পাঠ্যক্রম, অনুশীলন, অনুপ্রেরণা, বিশ্লেষণ, রিপোর্ট, ভয়েস" },
      { icon: "🌐", title: "3 ভাষা", desc: "English, हिंदी, বাংলা — নিজের মাতৃভাষায় শেখো" },
      { icon: "📊", title: "নার্সারি থেকে দশম", desc: "বয়স ৩-১৬, সম্পূর্ণ K-10 গণিত পাঠ্যক্রম" },
      { icon: "🎤", title: "ভয়েস সাপোর্ট", desc: "প্রশ্ন বলো, উত্তর শোনো" },
      { icon: "🔐", title: "নিরাপদ এবং গোপনীয়", desc: "JWT অথেনটিকেশন, COPPA অনুগামী, ডেটা এনক্রিপ্টেড" },
      { icon: "👨‍👩‍👧", title: "অভিভাবক রিপোর্ট", desc: "সাপ্তাহিক অগ্রগতি আপডেট, দুর্বল বিষয়ের সতর্কতা" },
    ],
    ready: "v1.0 — প্রোডাকশন রেডি",
  },
};

export default function DemoPage() {
  const [lang, setLang] = useState<Language>("en");
  const [step, setStep] = useState(0);
  const content = DEMO_CONTENT[lang];

  const cycleStep = () => setStep((s) => (s + 1) % 6);

  return (
    <div className="min-h-screen bg-gradient-to-b from-primary-50 to-white">
      {/* Language Switcher */}
      <div className="max-w-4xl mx-auto px-4 py-4 flex justify-center gap-2">
        {(["en", "hi", "bn"] as Language[]).map((l) => (
          <button
            key={l}
            onClick={() => { setLang(l); setStep(0); }}
            className={cn(
              "px-4 py-2 rounded-full text-sm font-medium transition-all",
              lang === l ? "bg-primary-600 text-white shadow-lg" : "bg-white text-gray-600 hover:bg-gray-100"
            )}
          >
            {l === "en" ? "🇬🇧 English" : l === "hi" ? "🇮🇳 हिंदी" : "🇧🇩 বাংলা"}
          </button>
        ))}
      </div>

      <div className="max-w-4xl mx-auto px-4 pb-16">
        {/* Hero */}
        <div className="text-center py-12">
          <div className="text-7xl mb-6">🧮</div>
          <h1 className="text-5xl font-heading font-extrabold text-primary-700 mb-3">
            {content.title}
          </h1>
          <p className="text-2xl font-heading font-semibold text-gray-600 mb-2">
            {content.subtitle}
          </p>
          <p className="text-xl text-gray-500 mb-6">{content.tagline}</p>

          {/* Status Badge */}
          <div className="inline-flex items-center gap-2 bg-white rounded-full px-4 py-2 shadow-sm border border-gray-100 mb-8">
            <span className="relative flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-success-500 opacity-75" />
              <span className="relative inline-flex rounded-full h-3 w-3 bg-success-500" />
            </span>
            <span className="text-sm font-medium text-gray-600">{content.ready}</span>
          </div>
        </div>

        {/* Interactive Demo */}
        <div className="card mb-8 max-w-2xl mx-auto">
          <h2 className="font-heading font-bold text-gray-700 text-center mb-6">
            {lang === "en" ? "📱 Live Demo — See How It Works" : lang === "hi" ? "📱 लाइव डेमो — देखें कैसे काम करता है" : "📱 লাইভ ডেমো — দেখুন কীভাবে কাজ করে"}
          </h2>

          <div className="bg-gray-50 rounded-2xl p-6 min-h-[280px] transition-all">
            {/* Step 0: Student asks */}
            {step === 0 && (
              <div className="animate-bounce-in space-y-4">
                <div className="flex items-start gap-3 flex-row-reverse">
                  <span className="text-3xl">👩‍🎓</span>
                  <div className="chat-bubble-student text-lg">{content.problem}</div>
                </div>
                <p className="text-center text-sm text-gray-400 mt-4">
                  {lang === "en" ? "Student asks a math question" : lang === "hi" ? "छात्र गणित का सवाल पूछता है" : "ছাত্র গণিত প্রশ্ন জিজ্ঞাসা করে"}
                </p>
              </div>
            )}

            {/* Step 1: Hint 1 */}
            {step === 1 && (
              <div className="animate-bounce-in space-y-4">
                <div className="flex items-start gap-3 flex-row-reverse">
                  <span className="text-3xl">👩‍🎓</span>
                  <div className="chat-bubble-student">{content.problem}</div>
                </div>
                <div className="flex items-start gap-3">
                  <span className="text-3xl">🧑‍🏫</span>
                  <div className="chat-bubble-hint">
                    <div className="text-xs text-primary-500 mb-1">💡 Hint 1 of 3</div>
                    <p>{content.hint1}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Step 2: Hint 2 */}
            {step === 2 && (
              <div className="animate-bounce-in space-y-4">
                <div className="flex items-start gap-3 flex-row-reverse">
                  <span className="text-3xl">👩‍🎓</span>
                  <div className="chat-bubble-student">{content.problem}</div>
                </div>
                <div className="flex items-start gap-3">
                  <span className="text-3xl">🧑‍🏫</span>
                  <div className="chat-bubble-hint">
                    <div className="text-xs text-primary-500 mb-1">💡 Hint 2 of 3</div>
                    <p>{content.hint2}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Step 3: Hint 3 */}
            {step === 3 && (
              <div className="animate-bounce-in space-y-4">
                <div className="flex items-start gap-3 flex-row-reverse">
                  <span className="text-3xl">👩‍🎓</span>
                  <div className="chat-bubble-student">{content.problem}</div>
                </div>
                <div className="flex items-start gap-3">
                  <span className="text-3xl">🧑‍🏫</span>
                  <div className="chat-bubble-hint">
                    <div className="text-xs text-primary-500 mb-1">💡 Hint 3 of 3</div>
                    <p>{content.hint3}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Step 4: Student answers */}
            {step === 4 && (
              <div className="animate-bounce-in space-y-4">
                <div className="flex items-start gap-3 flex-row-reverse">
                  <span className="text-3xl">👩‍🎓</span>
                  <div className="chat-bubble-student">{content.problem}</div>
                </div>
                <div className="flex items-start gap-3 flex-row-reverse">
                  <span className="text-3xl">👩‍🎓</span>
                  <div className="chat-bubble-student">{content.answer}</div>
                </div>
              </div>
            )}

            {/* Step 5: Celebration */}
            {step === 5 && (
              <div className="animate-bounce-in space-y-4">
                <div className="flex items-start gap-3 flex-row-reverse">
                  <span className="text-3xl">👩‍🎓</span>
                  <div className="chat-bubble-student">{content.answer}</div>
                </div>
                <div className="flex items-start gap-3">
                  <span className="text-3xl">🧑‍🏫</span>
                  <div className="chat-bubble-success">
                    <p>{content.celebration}</p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Demo Controls */}
          <div className="flex items-center justify-between mt-4">
            <span className="text-sm text-gray-400">Step {step + 1}/6</span>
            <div className="flex gap-2">
              <button onClick={() => setStep(Math.max(0, step - 1))} className="btn-ghost text-sm" disabled={step === 0}>← Prev</button>
              <button onClick={cycleStep} className="btn-primary text-sm">
                {step === 5 ? "🔄 Replay" : "Next →"}
              </button>
            </div>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 mb-8">
          {content.features.map((f) => (
            <div key={f.title} className="card text-center hover:shadow-md transition-all">
              <div className="text-3xl mb-2">{f.icon}</div>
              <h3 className="font-semibold text-gray-700 text-sm">{f.title}</h3>
              <p className="text-xs text-gray-500 mt-1">{f.desc}</p>
            </div>
          ))}
        </div>

        {/* CTA */}
        <div className="text-center">
          <p className="text-gray-500 mb-4">
            {lang === "en" ? "Ready to experience GanitMitra?" : lang === "hi" ? "गणित मित्र अनुभव करने के लिए तैयार?" : "গণিত মিত্র অভিজ্ঞতা করতে প্রস্তুত?"}
          </p>
          <div className="flex gap-3 justify-center">
            <Link href="/signup" className="btn-primary">Get Started Free →</Link>
            <Link href="/login" className="btn-secondary">Sign In</Link>
          </div>
          <p className="text-xs text-gray-400 mt-4">
            <Link href="/" className="hover:text-primary-500">Home</Link>
            {" · "}
            <a href="http://localhost:8000/api/docs" target="_blank" rel="noopener noreferrer" className="hover:text-primary-500">API Docs</a>
            {" · "}
            <a href="https://github.com/rajibmahata/Math-tutor-AI-Agent" target="_blank" rel="noopener noreferrer" className="hover:text-primary-500">GitHub</a>
          </p>
        </div>
      </div>
    </div>
  );
}
