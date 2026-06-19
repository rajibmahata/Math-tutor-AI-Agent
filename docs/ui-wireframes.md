# UI/UX Design — VidyaMitra v2.0 (Multi-Role Platform)

> **Date:** 2026-06-19 | **Version:** 2.0  
> **Framework:** Next.js + Tailwind CSS | **Design System:** Role-aware, accessible

---

## 1. Design Principles (v2.0)

| Principle | Implementation |
|-----------|---------------|
| **Role-Aware** | Different color accents per role: Student (Indigo), Tutor (Teal), Principal (Amber), Admin (Slate) |
| **Child-Friendly** | Student portal: warm colors, large touch targets, playful illustrations |
| **Professional** | Tutor/Principal/Admin portals: clean, data-dense, efficient |
| **Voice-First** | Voice interaction always accessible, fallback to text |
| **Multilingual** | Language switcher persistent across all portals |
| **Accessible** | WCAG 2.1 AA, large fonts, high contrast, keyboard navigable |
| **Mobile-First** | Designed for smartphones first, tablets, then desktop |
| **Human-in-the-Loop** | Clear approval/review indicators throughout workflows |

---

## 2. Role-Based Design System

### 2.1 Color Accents by Role

```
┌─────────────────────────────────────────────────────┐
│  STUDENT                    TUTOR                    │
│  ┌──────────┐              ┌──────────┐             │
│  │ #4F46E5  │ Indigo       │ #0D9488  │ Teal        │
│  │ Primary   │              │ Primary   │             │
│  └──────────┘              └──────────┘             │
│                                                      │
│  PRINCIPAL                  ADMIN                    │
│  ┌──────────┐              ┌──────────┐             │
│  │ #D97706  │ Amber        │ #475569  │ Slate       │
│  │ Primary   │              │ Primary   │             │
│  └──────────┘              └──────────┘             │
└─────────────────────────────────────────────────────┘
```

### 2.2 Typography

| Usage | Font | Weight |
|-------|------|--------|
| Headings | Nunito | 700-800 |
| Body (Student) | Inter | 400-500 |
| Body (Tutor/Admin) | Inter | 400-600 |
| Code/Data | JetBrains Mono | 400 |
| Math | KaTeX | — |
| Hindi | Noto Sans Devanagari | 400-500 |
| Bengali | Noto Sans Bengali | 400-500 |
| Tamil | Noto Sans Tamil | 400-500 |

---

## 3. Student Portal Screens

### 3.1 Student Dashboard v2

```
┌──────────────────────────────────────────────────────┐
│  👋 Hi, Riya!                🔥 5-day streak  🌐 EN  │
│  Grade 3 · Mathematics · Mrs. Gupta                  │
├──────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────────────────────────────────────────┐   │
│  │  📊 Overall Progress                         │   │
│  │  ━━━━━━━━━━━━━━━━━━━━░░░░░  35%              │   │
│  │  ⭐ 12 mastered  📝 5 learning  🔒 28 remain  │   │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  📚 Subjects                                         │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐      │
│  │ 📐 Math    │ │ 🔬 Science │ │ 📖 English  │      │
│  │ 65% done   │ │ 15% done   │ │ Coming soon │      │
│  │ [Continue] │ │ [Start]    │ │ [Notify]    │      │
│  └────────────┘ └────────────┘ └────────────┘      │
│                                                      │
│  🎯 Today's Recommendation                           │
│  ┌──────────────────────────────────────────────┐   │
│  │ Based on your progress, practice:             │   │
│  │ Multiplication Tables (6-9) — 45% mastered   │   │
│  │ [Start Learning →]                            │   │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  🏆 Gamification                                     │
│  ┌────────┬────────┬────────┬────────┐             │
│  │ ⭐1250 │ 🔥5day │ 🏅3badg │ 🏆#15  │             │
│  │ Points │ Streak │ Badges  │ Rank   │             │
│  └────────┴────────┴────────┴────────┘             │
│                                                      │
│  [🏠 Home] [💬 Learn] [📝 Test] [📊 Progress]        │
└──────────────────────────────────────────────────────┘
```

### 3.2 Subject Learning (Chapter → Topic)

```
┌──────────────────────────────────────────────────────┐
│  ← Math              Chapter 3: Multiplication       │
├──────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────────────────────────────────────────┐   │
│  │  📖 Topics in This Chapter                    │   │
│  │                                              │   │
│  │  ✅ Tables 1-5          ━━━━━━━━━━  100%     │   │
│  │  📝 Tables 6-9          ━━━━━░░░░░   65%     │   │
│  │  ⬜ Word Problems       ░░░░░░░░░░    0%     │   │
│  │  ⬜ Multiplication Quiz ░░░░░░░░░░    0%     │   │
│  │                                              │   │
│  │  [Continue Tables 6-9 →]                     │   │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  🎥 Related Videos                                   │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐      │
│  │ 🎬 Tables  │ │ 🎬 Multiply │ │ 🎬 Word    │      │
│  │ 6-9 Trick  │ │ with Arrays │ │ Problems   │      │
│  │ 3:24 min   │ │ 4:15 min   │ │ 5:02 min   │      │
│  └────────────┘ └────────────┘ └────────────┘      │
└──────────────────────────────────────────────────────┘
```

### 3.3 Voice Learning Chat v2

```
┌──────────────────────────────────────────────────────┐
│  ← Back     🧑‍🏫 AI Tutor — Mathematics     🌐 हिंदी  │
│  Mrs. Gupta (Tutor) · Available for review           │
├──────────────────────────────────────────────────────┤
│                                                      │
│                              ┌──────────────────┐    │
│                              │ 12 × 5 kitna     │    │
│                              │ hota hai?  😊    │    │
│                              └──────────────────┘    │
│                                                      │
│  ┌────────────────────────────────────────────┐     │
│  │ 🧑‍🏫 AI Teacher                             │     │
│  │                                            │     │
│  │ सोचो: 12 × 5 का मतलब 12 को 5 बार          │     │
│  │ जोड़ना। पहले 12 × 10 करो, फिर आधा।       │     │
│  │                                            │     │
│  │ [💡 Hint 1/3]  [🔊 Play]                  │     │
│  └────────────────────────────────────────────┘     │
│                                                      │
│  ┌──────────────────────┐                            │
│  │ 60?                  │                            │
│  └──────────────────────┘                            │
│                                                      │
│  ┌────────────────────────────────────────────┐     │
│  │ 🧑‍🏫 AI Teacher                             │     │
│  │ ⭐ Bilkul sahi! 12 × 5 = 60               │     │
│  │ +10 points! 🔥 6-day streak!               │     │
│  └────────────────────────────────────────────┘     │
│                                                      │
│  ┌────────────────────────────────────────────┐     │
│  │ 👨‍🏫 Mrs. Gupta (Your Tutor) added:          │     │
│  │ "Great progress Riya! Try word problems    │     │
│  │  next — they're more fun! ⭐"              │     │
│  └────────────────────────────────────────────┘     │
│                                                      │
├──────────────────────────────────────────────────────┤
│  [🎤 Voice]  [Type...]          [💡Hint] [📖Solve]  │
└──────────────────────────────────────────────────────┘
```

### 3.4 Mock Test Interface

```
┌──────────────────────────────────────────────────────┐
│  ← Back         Mock Test — Mathematics     ⏱️ 22:15 │
│  Question 5/10                                       │
├──────────────────────────────────────────────────────┤
│  ━━━━━━━━━━━━━━░░░░░░░░░░░░  50%                    │
│                                                      │
│  Part A: MCQ (Question 5)                            │
│  ┌──────────────────────────────────────────────┐   │
│  │  What is the product of 6 and 4?             │   │
│  │                                              │   │
│  │  ○ 20    ● 24    ○ 28    ○ 30               │   │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  Part B: Subjective (Question 8)                     │
│  ┌──────────────────────────────────────────────┐   │
│  │  Explain multiplication with an example.     │   │
│  │  [5 marks]                                   │   │
│  │                                              │   │
│  │  ┌──────────────────────────────────────┐    │   │
│  │  │ Write here or upload image...        │    │   │
│  │  │                                      │    │   │
│  │  └──────────────────────────────────────┘    │   │
│  │  [📷 Upload Answer Image]                   │   │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  [← Previous]                    [Submit Answer →]   │
└──────────────────────────────────────────────────────┘
```

---

## 4. Tutor Portal Screens

### 4.1 Tutor Registration

```
┌──────────────────────────────────────────────────────┐
│  👨‍🏫 Tutor Registration                    Step 2/4    │
├──────────────────────────────────────────────────────┤
│                                                      │
│  ━━━━━━━━━━━━━━━━━━━━━━░░░░░░  75%                  │
│                                                      │
│  Professional Details                                │
│  ┌──────────────────────────────────────────────┐   │
│  │ Subjects You Teach:                           │   │
│  │ ┌──────────────────────────────────────┐      │   │
│  │ │ Mathematics  [Class 1 ▾] to [Class 8 ▾]│   │   │
│  │ │ [✕ Remove]                            │      │   │
│  │ └──────────────────────────────────────┘      │   │
│  │ [+ Add Another Subject]                       │   │
│  │                                              │   │
│  │ Experience: [5] years                        │   │
│  │ Bio: [I am an experienced math teacher...]   │   │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  Upload Documents                                    │
│  ┌──────────────────────────────────────────────┐   │
│  │ 📄 Degree Certificate    [Upload] ✅ Done     │   │
│  │ 📄 Experience Letter     [Upload] ⬜ Pending  │   │
│  │ 🆔 ID Proof              [Upload] ✅ Done     │   │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  [← Back]                          [Submit →]        │
└──────────────────────────────────────────────────────┘
```

### 4.2 Tutor Dashboard v2

```
┌──────────────────────────────────────────────────────┐
│  👨‍🏫 Mrs. Gupta · Mathematics · Verified ✅           │
│  Rating: ⭐4.7 · 24 Students                          │
├──────────────────────────────────────────────────────┤
│                                                      │
│  📊 Overview                                         │
│  ┌──────────┬──────────┬──────────┬──────────┐     │
│  │    24    │    18    │    5     │    12   │     │
│  │ Students │  Active  │ Reviews  │Assessments│    │
│  │          │          │ Pending  │ to Review │     │
│  └──────────┴──────────┴──────────┴──────────┘     │
│                                                      │
│  📚 Content to Review                                │
│  ┌──────────────────────────────────────────────┐   │
│  │ ⬜ "Introduction to Fractions" — AI Generated │   │
│  │    Created: Jun 19 · Grade 3 · Hindi         │   │
│  │    [Review →]                                 │   │
│  │                                              │   │
│  │ ⬜ "Multiplication Word Problems"             │   │
│  │    Created: Jun 18 · Grade 4 · English       │   │
│  │    [Review →]                                 │   │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  👩‍🎓 Student Performance                              │
│  ┌──────┬──────────────┬──────────┬──────────┐     │
│  │ Name │ Grade        │ Accuracy │ Status   │     │
│  ├──────┼──────────────┼──────────┼──────────┤     │
│  │ Riya │ 3 · Math     │   78%    │ ⬆️ +3%  │     │
│  │ Arjun│ 5 · Math     │   65%    │ ⬇️ -2%  │     │
│  │ Priya│ 2 · Math     │   92%    │ ⬆️ +5%  │     │
│  └──────┴──────────────┴──────────┴──────────┘     │
│                                                      │
│  [📊 Dashboard] [📚 Review] [👩‍🎓 Students] [💬 Feedback]│
└──────────────────────────────────────────────────────┘
```

### 4.3 Content Review Screen

```
┌──────────────────────────────────────────────────────┐
│  ← Reviews      Content Review — Lesson #452          │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Lesson: "Introduction to Fractions"                 │
│  Generated by: AI (GPT-4o) · Grade: 3 · Hindi        │
│                                                      │
│  ┌──────────────────────────────────────────────┐   │
│  │ 📖 Lesson Preview                            │   │
│  │                                              │   │
│  │ भिन्न (Fractions) क्या होते हैं?             │   │
│  │                                              │   │
│  │ जब हम किसी चीज़ को बराबर हिस्सों में        │   │
│  │ बाँटते हैं, तो हर हिस्सा एक भिन्न कहलाता    │   │
│  │ है। जैसे — एक पिज़्ज़ा के 4 बराबर टुकड़े... │   │
│  │                                              │   │
│  │ [Show Full Lesson ▼]                         │   │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  📊 Quality Assessment                               │
│  ┌──────────────────────────────────────────────┐   │
│  │ Accuracy:     ★★★★★  5/5                     │   │
│  │ Completeness: ★★★★☆  4/5                     │   │
│  │ Alignment:    ★★★★★  5/5                     │   │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  ✏️ Your Feedback                                    │
│  ┌──────────────────────────────────────────────┐   │
│  │ [Content is accurate and well-structured.    │   │
│  │  Add one more example with fruits.]          │   │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐            │
│  │ ✅ Approve│ │ ✏️ Modify │ │ ❌ Reject │            │
│  └──────────┘ └──────────┘ └──────────┘            │
└──────────────────────────────────────────────────────┘
```

---

## 5. Principal Portal Screens

### 5.1 Principal Dashboard

```
┌──────────────────────────────────────────────────────┐
│  👨‍💼 Principal Sharma · DAV Group · Kolkata            │
├──────────────────────────────────────────────────────┤
│                                                      │
│  📊 Institution Overview                              │
│  ┌──────────┬──────────┬──────────┬──────────┐     │
│  │   450    │   380    │    12    │    2     │     │
│  │ Students │  Active  │  Tutors  │ Pending  │     │
│  └──────────┴──────────┴──────────┴──────────┘     │
│                                                      │
│  📈 Platform Activity (This Week)                     │
│  ┌──────────────────────────────────────────────┐   │
│  │ Sessions: 1,240  ·  Assessments: 890         │   │
│  │ Avg Engagement: 76%  ·  Avg Progress: 42%    │   │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  👨‍🏫 Tutor Performance                                │
│  ┌──────────┬──────────┬────────┬──────────┐       │
│  │ Tutor    │ Students │ Rating │ Reviews  │       │
│  ├──────────┼──────────┼────────┼──────────┤       │
│  │Mrs.Gupta │    24    │ ⭐4.7  │ 92% ✅   │       │
│  │Mr.Kumar  │    18    │ ⭐4.2  │ 78% ⚠️   │       │
│  │Ms.Sharma │    30    │ ⭐4.9  │ 96% ✅   │       │
│  └──────────┴──────────┴────────┴──────────┘       │
│                                                      │
│  ⚠️ Pending Actions                                  │
│  ┌──────────────────────────────────────────────┐   │
│  │ 🔴 Content Dispute — Escalated by Mrs. Gupta  │   │
│  │    [Resolve →]                                │   │
│  │ 🟡 New Tutor Registration — Mr. Verma         │   │
│  │    [Review →]                                  │   │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  [📊 Overview] [👨‍🏫 Tutors] [📄 Reports] [⚡ Actions]  │
└──────────────────────────────────────────────────────┘
```

---

## 6. Super Admin Portal Screens

### 6.1 Admin Dashboard

```
┌──────────────────────────────────────────────────────┐
│  ⚡ Super Admin · VidyaMitra Platform                 │
│  🔔 3 New Notifications                              │
├──────────────────────────────────────────────────────┤
│                                                      │
│  🏢 Organization Overview                             │
│  ┌──────────┬──────────┬──────────┬──────────┐     │
│  │  1,500   │  1,200   │    50    │    8     │     │
│  │ Total    │ Students │  Tutors  │Principals│     │
│  └──────────┴──────────┴──────────┴──────────┘     │
│                                                      │
│  ⚡ Approval Queue                                    │
│  ┌──────────────────────────────────────────────┐   │
│  │ 🆕 New Tutor: Mr. Kumar · Mathematics        │   │
│  │    AI Verified ✅ · Principal Approved ✅    │   │
│  │    [Approve] [Reject] [Request Info]         │   │
│  │                                              │   │
│  │ 🆕 New Tutor: Ms. Das · Science              │   │
│  │    AI Verified ⚠️ · Principal Pending        │   │
│  │    [Waiting for Principal]                    │   │
│  │                                              │   │
│  │ 🔴 Escalation: Content dispute — Math Gr.3   │   │
│  │    [Review →]                                 │   │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  📈 Platform Health                                   │
│  ┌──────────┬──────────┬──────────┐                │
│  │  99.9%   │  320ms   │  0.02%   │                │
│  │  Uptime  │ API P95  │ Error Rt │                │
│  └──────────┴──────────┴──────────┘                │
│                                                      │
│  [🏠 Home] [👥 Users] [📊 Analytics] [⚙️ Settings]    │
└──────────────────────────────────────────────────────┘
```

### 6.2 User Management

```
┌──────────────────────────────────────────────────────┐
│  👥 User Management                    🔍 Search...   │
├──────────────────────────────────────────────────────┤
│                                                      │
│  [All] [Students] [Tutors] [Principals] [Pending]    │
│                                                      │
│  ┌──────┬──────────┬────────┬──────────┬────────┐   │
│  │ Name │ Role     │ Status │ Joined   │ Actions│   │
│  ├──────┼──────────┼────────┼──────────┼────────┤   │
│  │Riya  │ Student  │ Active │ Jun 15   │ [View] │   │
│  │Gupta │ Tutor    │ Active │ Jun 10   │ [View] │   │
│  │Kumar │ Tutor    │Pending │ Jun 18   │ [Apprv]│   │
│  │Sharma│Principal │ Active │ Jun 01   │ [View] │   │
│  └──────┴──────────┴────────┴──────────┴────────┘   │
│                                                      │
│  [← Prev]  Page 1 of 4  [Next →]                     │
└──────────────────────────────────────────────────────┘
```

---

## 7. Content Upload Screen (Admin/Tutor)

```
┌──────────────────────────────────────────────────────┐
│  📄 Upload Content · Generate AI Lessons              │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Step 1: Upload Source Material                       │
│  ┌──────────────────────────────────────────────┐   │
│  │                                              │   │
│  │        📁 Drag & Drop PDF Here               │   │
│  │              or click to browse               │   │
│  │                                              │   │
│  │        Supported: PDF, DOCX, TXT             │   │
│  │        Max size: 50MB                        │   │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  Step 2: Configure                                     │
│  ┌──────────────────────────────────────────────┐   │
│  │ Subject:  [Mathematics ▾]                    │   │
│  │ Grade:    [Class 3 ▾]                        │   │
│  │ Language: [Hindi ▾]                          │   │
│  │ Board:    [NCERT ▾]                          │   │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  Step 3: Generate                                     │
│  ┌──────────────────────────────────────────────┐   │
│  │ ☑ Generate lesson plans                      │   │
│  │ ☑ Create chapter summaries                   │   │
│  │ ☑ Generate practice questions                │   │
│  │ ☐ Create video explanations (takes longer)   │   │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  ┌──────────────────────────────────────┐           │
│  │       🚀 Generate AI Content          │           │
│  └──────────────────────────────────────┘           │
│                                                      │
│  ⏳ Recent Generations                                │
│  ┌──────────────────────────────────────────────┐   │
│  │ ✅ "Class 3 Math Ch.2" · 12 lessons · Jun 18 │   │
│  │ 🔄 "Science Ch.5" · Processing... · Jun 19   │   │
│  └──────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────┘
```

---

## 8. Responsive Breakpoints

```css
/* Mobile First (Default) */
/* 0-639px: Single column, bottom nav, full-width cards */

/* Tablet */
@media (min-width: 640px) {
  /* 640-1023px: Two-column layouts, side nav */
}

/* Desktop */
@media (min-width: 1024px) {
  /* 1024px+: Persistent sidebar, multi-column, data tables */
}
```

---

## 9. Micro-Interactions (v2.0)

### 9.1 Content Approval Flow
```
Tutor clicks [Approve] → ✨ Checkmark animation
→ Card slides up → Green "Approved" badge
→ Lesson moves to "Published" section
→ Notification sent: "Your lesson was approved"
```

### 9.2 Tutor Verification Complete
```
Admin clicks [Approve Tutor] → Shield ✅ animation
→ Tutor status changes to "Active"
→ Notification to Tutor: "You're verified! Start teaching."
→ Notification to Principal: "Mr. Kumar approved"
```

### 9.3 Wrong Answer with Solution
```
Student answers incorrectly → ❌ gentle shake
→ AI: "Not quite. Let me explain why..."
→ Solution card slides in from bottom
→ Step-by-step with highlighted correct answer
→ "Try again?" button appears
```

---

## 10. Accessibility Checklist

- [ ] All interactive elements ≥ 48×48px touch target
- [ ] Color contrast ratio ≥ 4.5:1 (text), ≥ 3:1 (large text)
- [ ] Role colors distinguishable by more than hue alone
- [ ] All images have alt text
- [ ] Form inputs have visible labels
- [ ] Error states identified by text + icon (not color alone)
- [ ] Keyboard navigation: Tab, Enter, Escape, Arrow keys
- [ ] Screen reader: ARIA labels on custom components
- [ ] Focus indicators visible (ring-2 per role color)
- [ ] Motion reduction: `prefers-reduced-motion` respected
- [ ] Language attribute set correctly for screen readers
- [ ] All Indian language text in proper Unicode

---

## Next: Implementation → [implementation-roadmap.md](./implementation-roadmap.md)
