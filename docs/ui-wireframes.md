# UI/UX Design — GanitMitra Math Tutor

> **Date:** 2026-06-19
> **Version:** 1.0
> **Framework:** Next.js + Tailwind CSS + shadcn/ui
> **Design System:** Student-friendly, colorful, accessible

---

## 1. Design Principles

### 1.1 Core Philosophy

| Principle | Implementation |
|-----------|---------------|
| **Child-Friendly** | Warm colors, rounded corners, large touch targets, playful illustrations |
| **Minimal Cognitive Load** | One primary action per screen, progressive disclosure |
| **Multilingual First** | Language switcher always visible, no hardcoded text |
| **Encouragement-Focused** | Positive reinforcement, celebration animations, gentle error states |
| **Accessible** | WCAG 2.1 AA, large fonts, high contrast, keyboard navigable |
| **Mobile-First** | Designed for smartphones first (primary device for Indian students) |
| **Offline-Ready** | PWA with cached UI, graceful degradation |

### 1.2 Target Devices

| Device | Priority | Resolution |
|--------|----------|------------|
| Smartphone | P0 | 360×800 (small Android) |
| Tablet | P1 | 768×1024 (iPad) |
| Desktop | P2 | 1366×768+ |

---

## 2. Design System

### 2.1 Color Palette

```
┌─────────────────────────────────────────────────────┐
│  PRIMARY                    ACCENTS                  │
│  ┌──────────┐              ┌──────────┐             │
│  │ #4F46E5  │ Indigo       │ #10B981  │ Emerald     │
│  │ Primary  │              │ Success   │             │
│  └──────────┘              └──────────┘             │
│  ┌──────────┐              ┌──────────┐             │
│  │ #6366F1  │ Indigo Light │ #F59E0B  │ Amber       │
│  │ Hover    │              │ Warning   │             │
│  └──────────┘              └──────────┘             │
│  ┌──────────┐              ┌──────────┐             │
│  │ #3730A3  │ Indigo Dark  │ #EF4444  │ Red         │
│  │ Pressed  │              │ Error     │             │
│  └──────────┘              └──────────┘             │
│                                                      │
│  NEUTRALS                  BACKGROUNDS               │
│  ┌──────────┐              ┌──────────┐             │
│  │ #F8FAFC  │ Gray 50      │ #FFFFFF  │ Surface     │
│  │ #F1F5F9  │ Gray 100     │ #F8FAFC  │ Background  │
│  │ #E2E8F0  │ Gray 200     │ #EEF2FF  │ Indigo Tint │
│  │ #94A3B8  │ Gray 400     └──────────┘             │
│  │ #475569  │ Gray 600                               │
│  │ #1E293B  │ Gray 800                               │
│  └──────────┘                                         │
└─────────────────────────────────────────────────────┘
```

### 2.2 Typography

| Usage | Font | Weight | Size |
|-------|------|--------|------|
| Headings | Nunito (Google Fonts) | 700-800 | 24-32px |
| Subheadings | Nunito | 600 | 18-20px |
| Body | Inter | 400-500 | 16px |
| Small/Caption | Inter | 400 | 14px |
| Math Expressions | KaTeX | — | inherits |
| Hindi/Bengali Text | Noto Sans Devanagari / Noto Sans Bengali | 400-500 | 16px |

### 2.3 Components

Using **shadcn/ui** as base, customized:
- `Button` — Large (min 48px touch target), rounded-xl, colorful
- `Card` — Rounded-2xl, subtle shadow, hover elevation
- `Input` — Rounded-xl, large text, clear labels
- `Badge` — Pill shape, emoji-friendly
- `Dialog` — Centered, animated, overlay
- `Toast` — Bottom-positioned on mobile
- `Progress` — Animated, gradient fill

---

## 3. Screen Wireframes

### 3.1 Onboarding Flow

```
┌────────────────────┐    ┌────────────────────┐    ┌────────────────────┐
│                    │    │                    │    │                    │
│   🌟 GanitMitra    │    │   📝 Your Profile  │    │   🎯 Quick Test   │
│                    │    │                    │    │                    │
│  "Your Math        │    │  Name: [______]   │    │  Question 1 of 5   │
│   Friend!"         │    │                    │    │                    │
│                    │    │  Age:  [___]       │    │  What is 15 + 7?   │
│  [Illustration]    │    │                    │    │                    │
│   Kid with         │    │  Grade: [▼ 3rd]   │    │  [___________]     │
│   math symbols     │    │                    │    │                    │
│                    │    │  Language:         │    │  🟡⚪⚪⚪⚪          │
│                    │    │  [🇬🇧 EN]         │    │                    │
│  ┌──────────────┐  │    │  [🇮🇳 हिंदी]    │    │                    │
│  │  Get Started  │  │    │  [🇧🇩 বাংলা]   │    │  ┌──────────────┐  │
│  └──────────────┘  │    │                    │    │  │   Submit     │  │
│                    │    │  ┌──────────────┐  │    │  └──────────────┘  │
│  Already learning? │    │  │   Continue    │  │    │                    │
│  [Sign In]         │    │  └──────────────┘  │    │  [Skip for now]    │
└────────────────────┘    └────────────────────┘    └────────────────────┘

     SCREEN 1                   SCREEN 2                  SCREEN 3
   (Welcome)                (Profile Setup)          (Placement Quiz)
```

### 3.2 Student Dashboard (Home)

```
┌──────────────────────────────────────────────┐
│  👋 Hi, Riya!              🔥 5-day streak   │
│  Grade 3 • हिंदी  [🌐]                       │
├──────────────────────────────────────────────┤
│                                              │
│  ┌──────────────────────────────────────┐   │
│  │  📊 Your Progress                    │   │
│  │  ━━━━━━━━━━━━━━━━━━━━░░░░░  35%      │   │
│  │  Grade 3 Math                        │   │
│  │                                      │   │
│  │  ⭐ 12 mastered  📝 5 learning  🔒 28 │   │
│  └──────────────────────────────────────┘   │
│                                              │
│  ┌──────────────────┐ ┌──────────────────┐  │
│  │  📚 Continue      │ │  ✏️ Practice     │  │
│  │  Learning         │ │  Quiz            │  │
│  │                  │ │                  │  │
│  │  Multiplication  │ │  10 Questions    │  │
│  │  Tables (6-9)    │ │  Adaptive        │  │
│  │  ━━━━━━━━░░░ 65% │ │                  │  │
│  │  [Resume →]      │ │  [Start Quiz →]  │  │
│  └──────────────────┘ └──────────────────┘  │
│                                              │
│  📌 Topics to Improve                        │
│  ┌──────────────────────────────────────┐   │
│  │ 🔴 Division (Basic)     ━━━░░░░ 38%  │   │
│  │ 🟡 Multiplication(6-9)  ━━━━━░░░ 45% │   │
│  └──────────────────────────────────────┘   │
│                                              │
│  🏆 Recent Achievements                      │
│  ┌────┐ ┌────┐ ┌────┐                       │
│  │ 🔥 │ │ 💯 │ │ ⭐ │                       │
│  │7day│ │100Q│ │Mas │                       │
│  └────┘ └────┘ └────┘                       │
│                                              │
│  [🏠 Home] [💬 Learn] [✏️ Practice] [📊 Progress] │
└──────────────────────────────────────────────┘
```

### 3.3 Tutoring Chat Interface

```
┌──────────────────────────────────────────────┐
│  ← Back          GanitMitra          🌐 हिंदी │
├──────────────────────────────────────────────┤
│  📍 Topic: Multiplication Tables (6-9)       │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                              │
│                              ┌────────────┐  │
│                              │ 12 × 5      │  │
│                              │ kitna hota  │  │
│                              │ hai?  😊    │  │
│                              └────────────┘  │
│                                              │
│  ┌────────────────────────────────────┐      │
│  │ 🧑‍🏫 Teacher                        │      │
│  │                                    │      │
│  │ Socho: 12 × 5 ka matlab 12 ko     │      │
│  │ 5 baar jodna hai.                  │      │
│  │                                    │      │
│  │ Pehle 12 × 10 karke dekho —        │      │
│  │ usse aadha kitna hoga?             │      │
│  │                                    │      │
│  │ [💡 Hint 1 of 3]                   │      │
│  └────────────────────────────────────┘      │
│                                              │
│  ┌──────────────────────┐                    │
│  │ 60?                  │                    │
│  └──────────────────────┘                    │
│                                              │
│  ┌────────────────────────────────────┐      │
│  │ 🧑‍🏫 Teacher                        │      │
│  │                                    │      │
│  │ ⭐ Bilkul sahi! 12 × 5 = 60       │      │
│  │ Bahut achhe, Riya!                 │      │
│  │ +10 points! 🎉                     │      │
│  └────────────────────────────────────┘      │
│                                              │
├──────────────────────────────────────────────┤
│  [🎤 Voice]  [Type message...]      [📎] [▶] │
│  [💡 Hint]   [📖 Solution]  [🔚 End Session] │
└──────────────────────────────────────────────┘
```

### 3.4 Practice Quiz Interface

```
┌──────────────────────────────────────────────┐
│  ← Back     Practice Quiz          ⏱️ 04:32  │
│  Multiplication Tables                          │
├──────────────────────────────────────────────┤
│  ━━━━━━━━━━━━░░░░░░░░░░  5/10               │
│                                              │
│  Question 5                                  │
│  ┌──────────────────────────────────────┐   │
│  │                                      │   │
│  │   एक दुकानदार के पास 8 थैले हैं।     │   │
│  │   हर थैले में 7 सेब हैं।             │   │
│  │   कुल कितने सेब हैं?                 │   │
│  │                                      │   │
│  └──────────────────────────────────────┘   │
│                                              │
│  Your Answer:                                │
│  ┌──────────────────────────────────────┐   │
│  │  [___________________________]       │   │
│  └──────────────────────────────────────┘   │
│                                              │
│  ┌──────────────┐  ┌──────────────┐         │
│  │  💡 Hint     │  │  ✅ Submit   │         │
│  └──────────────┘  └──────────────┘         │
│                                              │
│  Hint used: 0/3                              │
└──────────────────────────────────────────────┘
```

### 3.5 Quiz Result Screen

```
┌──────────────────────────────────────────────┐
│                                              │
│           🎉 Great Job, Riya!                 │
│                                              │
│              ┌────────────┐                   │
│              │   8 / 10   │                   │
│              │    80%     │                   │
│              └────────────┘                   │
│                                              │
│  ━━━━━━━━━━━━━━━━━━━━━━░░░░░                │
│                                              │
│  ⏱️ 7 min 15 sec    💡 3 hints used          │
│  ⭐ +80 points      🔥 5 day streak          │
│                                              │
│  ┌──────────────────────────────────────┐   │
│  │  📊 Question Breakdown               │   │
│  │  ✅✅✅❌✅ ✅✅❌✅✅                 │   │
│  │                                      │   │
│  │  ❌ Q4: 6×8 (said 46, correct: 48)   │   │
│  │  ❌ Q8: Word problem misread          │   │
│  └──────────────────────────────────────┘   │
│                                              │
│  📌 Next Focus: 7× and 8× tables             │
│                                              │
│  ┌──────────────┐  ┌──────────────┐         │
│  │ 🔄 Try Again │  │ 🏠 Dashboard │         │
│  └──────────────┘  └──────────────┘         │
└──────────────────────────────────────────────┘
```

### 3.6 Progress Dashboard

```
┌──────────────────────────────────────────────┐
│  📊 My Progress                  🌐 हिंदी    │
├──────────────────────────────────────────────┤
│                                              │
│  ┌──────────────────────────────────────┐   │
│  │  Grade 3 Math Progress               │   │
│  │  ━━━━━━━━━━━━━━━░░░░░░░░  35%        │   │
│  │  ⭐ 12 Mastered  📝 5 Learning  🔒 28 │   │
│  └──────────────────────────────────────┘   │
│                                              │
│  📈 Weekly Activity                           │
│  ┌──────────────────────────────────────┐   │
│  │  [Bar Chart: Questions per day]       │   │
│  │   M  T  W  T  F  S  S               │   │
│  │   ▆  ▄  ▇  ▅  █  ▃  ▁               │   │
│  └──────────────────────────────────────┘   │
│                                              │
│  🧠 Topic Mastery Map                         │
│  ┌──────────────────────────────────────┐   │
│  │  अंकगणित (Arithmetic)                │   │
│  │  ├─ ✅ जोड़ (Addition)         95%    │   │
│  │  ├─ ✅ घटाव (Subtraction)      92%    │   │
│  │  ├─ 📝 गुणा (Multiplication)   65%    │   │
│  │  └─ 🔴 भाग (Division)          38%    │   │
│  │                                      │   │
│  │  संख्या ज्ञान (Number Sense)         │   │
│  │  ├─ ✅ Place Value            90%    │   │
│  │  └─ 📝 Roman Numerals         55%    │   │
│  └──────────────────────────────────────┘   │
│                                              │
│  🎯 Confidence Trend                          │
│  ┌──────────────────────────────────────┐   │
│  │  [Line chart: 0.5 → 0.72 rising]     │   │
│  └──────────────────────────────────────┘   │
└──────────────────────────────────────────────┘
```

### 3.7 Parent Dashboard

```
┌──────────────────────────────────────────────┐
│  👨‍👩‍👧 Parent Dashboard       Riya • Grade 3  │
├──────────────────────────────────────────────┤
│                                              │
│  📊 This Week (Jun 12 - Jun 19)              │
│  ┌──────────┬──────────┬──────────┐         │
│  │    5     │    85    │   78%    │         │
│  │ Sessions │Questions │ Accuracy │         │
│  └──────────┴──────────┴──────────┘         │
│  ┌──────────┬──────────┐                     │
│  │  145 min │   35%    │                     │
│  │  Spent   │  Progress│                     │
│  └──────────┴──────────┘                     │
│                                              │
│  📈 Progress Trend                            │
│  ┌──────────────────────────────────────┐   │
│  │  [Accuracy line chart: Week over week]│   │
│  │  Week 1: 72%  Week 2: 75%  W3: 78%  │   │
│  └──────────────────────────────────────┘   │
│                                              │
│  🌟 Strengths                                │
│  ✅ Addition (3-digit) — 95% mastery         │
│  ✅ Subtraction (2-digit) — 92% mastery      │
│                                              │
│  ⚠️ Needs Attention                          │
│  🔴 Division (Basic) — 38% mastery           │
│     "Riya reverses dividend and divisor"     │
│  🟡 Multiplication (6-9) — 45% mastery       │
│     "Struggles with 7× and 8× tables"        │
│                                              │
│  💡 Recommendations                          │
│  • Practice division 15 min/day              │
│  • Use real-life sharing examples            │
│  • Try skip-counting for multiplication      │
│                                              │
│  📄 Latest Report (Jun 19)              [→]  │
└──────────────────────────────────────────────┘
```

### 3.8 Voice Interaction Mode

```
┌──────────────────────────────────────────────┐
│  🎤 Voice Mode                              │
├──────────────────────────────────────────────┤
│                                              │
│                                              │
│              ┌────────────┐                   │
│              │            │                   │
│              │  🎤 🔊     │                   │
│              │            │                   │
│              │ Listening  │                   │
│              │   ...      │                   │
│              │            │                   │
│              └────────────┘                   │
│                                              │
│         "अपना सवाल बोलो..."                   │
│                                              │
│                                              │
│  ┌────────────────────────────────────┐      │
│  │ आपने पूछा: "12 गुना 5 कितना होता है?"│      │
│  └────────────────────────────────────┘      │
│                                              │
│  ┌────────────────────────────────────┐      │
│  │ 🧑‍🏫 "12 × 5 = 60. शाबाश!"          │      │
│  │                                    │      │
│  │ [🔊 Playing response...]           │      │
│  └────────────────────────────────────┘      │
│                                              │
│              ┌────────────┐                   │
│              │  Tap to    │                   │
│              │  Speak     │                   │
│              └────────────┘                   │
│                                              │
│  [⌨️ Switch to Text]                         │
└──────────────────────────────────────────────┘
```

---

## 4. Micro-Interactions

### 4.1 Correct Answer Celebration

```
┌──────────────────────────────────────┐
│  Student answers correctly           │
│                                      │
│  ⭐ +10 points  →  particle burst    │
│  (confetti animation, 500ms)         │
│                                      │
│  Progress bar animates forward       │
│  Sound: subtle "ding" (optional)     │
└──────────────────────────────────────┘
```

### 4.2 Hint Reveal

```
┌──────────────────────────────────────┐
│  [💡 Hint] button pressed            │
│                                      │
│  → Button transforms: 💡→💡(1)       │
│  → Hint card slides in from top      │
│  → "Hint 1 of 3" indicator updates   │
│                                      │
│  After Hint 3, button becomes:       │
│  [📖 Show Solution]                  │
└──────────────────────────────────────┘
```

### 4.3 Streak Milestone

```
┌──────────────────────────────────────┐
│  7-day streak achieved!              │
│                                      │
│  → Full-screen overlay (2s)          │
│  → 🔥🔥🔥 animation                  │
│  → "7-Day Streak!" badge awarded     │
│  → Sound: celebration chime          │
│  → Auto-dismiss                       │
└──────────────────────────────────────┘
```

### 4.4 Loading States

```
┌──────────────────────────────────────┐
│  Teacher is "thinking"...             │
│                                      │
│  → Animated dots (···) in chat       │
│  → Fun math-themed skeleton:          │
│    "Crunching numbers..." 🔢         │
│    "Drawing on the board..." 📝      │
│    "Brewing chai for the teacher ☕"  │
│                                      │
│  After 5s: "Still working..."        │
│  After 10s: "This is a tricky one!"  │
└──────────────────────────────────────┘
```

---

## 5. Responsive Breakpoints

```css
/* Mobile First (Default) */
/* 0-639px: Single column, bottom nav, full-width cards */

/* Tablet */
@media (min-width: 640px) {
  /* 640-1023px: Two-column layout where beneficial */
}

/* Desktop */
@media (min-width: 1024px) {
  /* 1024px+: Sidebar navigation, multi-column, larger math display */
}
```

---

## 6. Accessibility Checklist

- [ ] All interactive elements ≥ 48×48px touch target
- [ ] Color contrast ratio ≥ 4.5:1 (text), ≥ 3:1 (large text)
- [ ] All images have alt text
- [ ] Form inputs have visible labels
- [ ] Error states identified by more than color alone
- [ ] Keyboard navigation: Tab, Enter, Escape
- [ ] Screen reader: ARIA labels on custom components
- [ ] Focus indicators visible (ring-2 ring-indigo-500)
- [ ] Motion reduction: `prefers-reduced-motion` respected
- [ ] Language attribute set correctly for screen readers
- [ ] Hindi/Bengali text in proper Unicode, not transliterated

---

## 7. PWA Considerations

- Service worker for offline caching
- App manifest with icons
- Splash screen for mobile
- Install prompt
- Offline: cached UI, queued messages, sync on reconnect

---

## Next: Implementation Roadmap → [implementation-roadmap.md](./implementation-roadmap.md)
