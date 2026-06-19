# GanitMitra — Customer Demo

> **AI-Powered Multilingual Math Learning Companion**
> Nursery to Class 10 | English · Hindi · Bengali
> Version 1.0 — Production Ready

---

## Quick Access

| Resource | URL |
|----------|-----|
| **Live Demo** | http://localhost:3000/demo |
| **App Home** | http://localhost:3000 |
| **Sign Up** | http://localhost:3000/signup |
| **API Docs** | http://localhost:8000/api/docs |
| **GitHub** | https://github.com/rajibmahata/Math-tutor-AI-Agent |

---

## What is GanitMitra?

GanitMitra (गणित मित्र / গণিত মিত্র) is an **AI-powered math tutor** that speaks every Indian student's language. It's not a chatbot — it's a **personal math teacher** that remembers each student, adapts to their learning pace, and teaches step-by-step in their preferred language.

---

## Core Features

### 🧑‍🏫 Multi-Agent AI Tutoring
- **8 specialized AI agents** work together as your child's personal math teaching team
- **Hint → Guide → Solve** methodology — never gives answers first, builds true understanding
- **Age-aware teaching**: uses stories and visuals for young children, abstract reasoning for older students

### 🌐 Truly Multilingual
- **English, Hindi (हिंदी), Bengali (বাংলা)** — full support in all 3 languages
- **Voice input**: speak math questions naturally
- **Voice output**: hear explanations in your mother tongue
- Switch languages anytime mid-session

### 📊 Adaptive Learning
- **Student Digital Twin**: a unique profile that tracks strengths, weaknesses, and progress
- **Automatic difficulty adjustment**: challenges without frustrating
- **Misconception detection**: identifies WHY a student made an error, not just THAT they made one
- **NCERT/CBSE aligned** curriculum for Nursery through Class 10

### 👨‍👩‍👧 For Parents
- **Weekly progress reports** with clear insights
- **Weak area alerts** before they become problems
- **Recommendations** for supporting learning at home
- **Streak tracking** to build consistent study habits

---

## Technology

| Component | Technology |
|-----------|-----------|
| Frontend | Next.js 15, TypeScript, Tailwind CSS |
| Backend | FastAPI (Python 3.12), WebSocket |
| AI Models | OpenAI GPT-4o + DeepSeek V4 (dual provider) |
| Database | PostgreSQL + Redis + Qdrant (vector search) |
| Voice | Whisper STT + OpenAI/ElevenLabs TTS |
| Math Engine | SymPy (deterministic answer verification) |

---

## Demo Walkthrough

### English Demo
1. Student: "What is 12 × 5?"
2. Tutor (Hint 1): "Think: 12 × 5 means adding 12 five times..."
3. Tutor (Hint 2): "12 × 10 = 120. Now try half of that..."
4. Student: "60"
5. Tutor: "⭐ Correct! 12 × 5 = 60. Excellent! +10 points!"

### Hindi Demo (हिंदी)
1. छात्र: "12 × 5 कितना होता है?"
2. टीचर: "सोचो: 12 × 5 का मतलब 12 को 5 बार जोड़ना..."
3. टीचर: "12 × 10 = 120। अब इसका आधा..."
4. छात्र: "60"
5. टीचर: "⭐ बिल्कुल सही! शाबाश!"

### Bengali Demo (বাংলা)
1. ছাত্র: "12 × 5 কত হয়?"
2. শিক্ষক: "ভাবো: 12 × 5 মানে 12 কে 5 বার যোগ করা..."
3. শিক্ষক: "12 × 10 = 120। এখন এর অর্ধেক..."
4. ছাত্র: "60"
5. শিক্ষক: "⭐ একদম সঠিক! দারুণ!"

---

## Pricing (Proposed)

| Tier | Price | Features |
|------|-------|----------|
| **Free** | ₹0/month | 5 questions/day, 1 language, basic tutoring |
| **Basic** | ₹199/month | Unlimited questions, 3 languages, progress tracking |
| **Premium** | ₹499/month | Voice, quizzes, parent reports, offline access |
| **Family** | ₹799/month | Up to 3 students, detailed analytics |

---

## Contact

- **Email:** rajibmahata143@gmail.com
- **GitHub:** https://github.com/rajibmahata

---

*Built with ❤️ for every Indian student who deserves a personal math teacher.*
