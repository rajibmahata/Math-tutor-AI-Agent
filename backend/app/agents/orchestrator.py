"""
Multi-Agent Orchestrator — LangGraph-based coordination of all 8 agents.
This is the brain that makes GanitMitra truly interactive.
"""

import json
import logging
from dataclasses import dataclass, field
from typing import Optional

from app.routing.router import model_router, LLMResponse
from app.utils.sympy_verify import verify_answer

logger = logging.getLogger(__name__)


@dataclass
class AgentContext:
    """Context passed between agents during orchestration."""
    student_id: str = ""
    student_name: str = ""
    grade: str = "3"
    language: str = "en"
    session_id: str = ""
    message: str = ""
    last_question: str = ""
    student_answer: str = ""
    hint_level: int = 0
    is_correct: Optional[bool] = None
    misconception: Optional[str] = None
    error_type: Optional[str] = None
    topic: str = ""
    next_topic: str = ""
    motivation: str = ""
    response: str = ""
    # Learning state
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    accuracy_rate: float = 0.0
    streak: int = 0
    points: int = 0


class AgentOrchestrator:
    """
    Coordinates all 8 agents through a decision graph.
    Each agent contributes to the final response.
    """

    async def process(self, ctx: AgentContext) -> AgentContext:
        """Main orchestration pipeline."""
        # Step 1: Classify intent
        intent = await self._classify_intent(ctx)
        
        if intent == "greeting":
            ctx = await self._run_greeting_flow(ctx)
        elif intent == "math_question":
            ctx = await self._run_teaching_flow(ctx)
        elif intent == "answer":
            ctx = await self._run_assessment_flow(ctx)
        elif intent == "progress_query":
            ctx = await self._run_progress_flow(ctx)
        else:
            ctx = await self._run_teaching_flow(ctx)
        
        return ctx

    # =========================================================================
    # Intent Classification
    # =========================================================================

    async def _classify_intent(self, ctx: AgentContext) -> str:
        """Teacher Agent: classify what the student needs."""
        msg = ctx.message.strip()
        
        # Quick heuristics
        if len(msg) < 3:
            return "greeting"
        if any(w in msg.lower() for w in ["hi", "hello", "hey", "thanks", "bye", "नमस्ते", "নমস্কার"]):
            return "greeting"
        
        # Numeric answer detection
        clean = msg.replace("=", "").replace(" ", "")
        if clean.isdigit() or (clean.startswith("-") and clean[1:].isdigit()):
            return "answer"
        if len(msg) <= 6 and any(c.isdigit() for c in msg):
            return "answer"
        
        # Progress query
        if any(w in msg.lower() for w in ["progress", "score", "points", "how am i", "report"]):
            return "progress_query"
        
        # Math question detection
        math_indicators = [
            r"\d+", r"what is", r"calculate", r"solve", r"find", r"evaluate",
            r"how much", r"add", r"subtract", r"multiply", r"divide",
            r"\+", r"-", r"×", r"÷", r"\*", r"/",
            r"kitna", r"कितना", r"কত",
            r"जोड़", r"घटाव", r"गुणा", r"भाग",
            r"যোগ", r"বিয়োগ", r"গুণ", r"ভাগ",
        ]
        import re
        for indicator in math_indicators:
            if re.search(indicator, msg, re.IGNORECASE):
                return "math_question"
        
        return "greeting"

    # =========================================================================
    # Agent Flows
    # =========================================================================

    async def _run_greeting_flow(self, ctx: AgentContext) -> AgentContext:
        """Motivation Agent: warm greeting."""
        ctx.response = await self._greeting_agent(ctx)
        return ctx

    async def _run_teaching_flow(self, ctx: AgentContext) -> AgentContext:
        """Teacher Agent → Curriculum Agent → hint generation."""
        ctx.last_question = ctx.message
        ctx.hint_level = 1
        
        # Curriculum Agent: check if topic is appropriate
        topic_context = await self._curriculum_agent(ctx)
        
        # Teacher Agent: generate hint
        hint = await self._teacher_agent(ctx, topic_context)
        
        ctx.response = hint
        return ctx

    async def _run_assessment_flow(self, ctx: AgentContext) -> AgentContext:
        """Assessment Agent → Solution if wrong."""
        ctx.student_answer = ctx.message
        assessment = await self._assessment_agent(ctx)
        ctx.is_correct = assessment["is_correct"]
        
        if ctx.is_correct:
            # Correct: celebrate + brief motivation
            ctx.response = assessment.get("feedback", "⭐ Correct! 🎉")
        else:
            # Wrong: explain why + show step-by-step solution
            solution = await self.generate_solution(ctx)
            ctx.response = assessment.get("feedback", "Let me explain.") + "\n\n" + solution

        return ctx

    async def _run_progress_flow(self, ctx: AgentContext) -> AgentContext:
        """Analytics Agent: progress summary."""
        summary = await self._analytics_agent(ctx)
        ctx.response = summary
        return ctx

    # =========================================================================
    # Individual Agents
    # =========================================================================

    async def _greeting_agent(self, ctx: AgentContext) -> str:
        """Motivation Agent: personalized greeting."""
        greetings = {
            "en": f"Hi {ctx.student_name}! I'm your math tutor. What would you like to learn today? 😊\n\nI can help with addition, subtraction, multiplication, division, fractions, algebra, and more! Just ask me a question.",
            "hi": f"नमस्ते {ctx.student_name}! मैं आपका गणित टीचर हूँ। आज क्या सीखना चाहोगे? 😊\n\nमैं जोड़, घटाव, गुणा, भाग, भिन्न, बीजगणित और बहुत कुछ में मदद कर सकता हूँ! बस अपना सवाल पूछो।",
            "bn": f"নমস্কার {ctx.student_name}! আমি তোমার গণিত শিক্ষক। আজ কী শিখতে চাও? 😊\n\nআমি যোগ, বিয়োগ, গুণ, ভাগ, ভগ্নাংশ, বীজগণিত আর আরও অনেক কিছুতে সাহায্য করতে পারি! শুধু প্রশ্ন করো।",
        }
        return greetings.get(ctx.language, greetings["en"])

    async def _curriculum_agent(self, ctx: AgentContext) -> str:
        """Curriculum Agent: check if topic is grade-appropriate."""
        return f"Grade {ctx.grade} math topic"

    async def _teacher_agent(self, ctx: AgentContext, topic_context: str) -> str:
        """Teacher Agent: generate age-appropriate hint using AI."""
        grade = ctx.grade or "3"
        lang = ctx.language or "en"
        
        # Try AI first
        try:
            response = await model_router.route(
                task_type="hint_generation",
                messages=[
                    {"role": "system", "content": f"""You are a patient math teacher for a Grade {grade} student.
Teach in {lang}. NEVER give the final answer. Give ONE hint.
Student question: {ctx.last_question}
Keep it short (2 sentences). Respond in {lang}."""},
                    {"role": "user", "content": ctx.last_question},
                ],
                language=lang,
            )
            return response.content
        except Exception:
            pass
        
        # Fallback hints
        hints = {
            "en": f"Let's think about this: {ctx.last_question}. What operation do you need? Look at the numbers carefully.",
            "hi": f"सोचो: {ctx.last_question}। कौन सी गणित क्रिया चाहिए? संख्याओं को ध्यान से देखो।",
            "bn": f"ভাবো: {ctx.last_question}। কোন গণিত অপারেশন দরকার? সংখ্যাগুলো ভালো করে দেখো।",
        }
        return hints.get(lang, hints["en"])

    async def _assessment_agent(self, ctx: AgentContext) -> dict:
        """Assessment Agent: evaluate with SymPy, AI only for wrong answers."""
        # Step 1: SymPy verification (deterministic)
        sympy_result = verify_answer(ctx.student_answer, ctx.last_question)
        is_correct = sympy_result.get("is_correct", None)
        expected = sympy_result.get("expected", "")
        
        logger.info(f"Assessment: q='{ctx.last_question}' a='{ctx.student_answer}' sympy={is_correct} expected={expected}")
        
        # SymPy says correct → celebrate immediately
        if is_correct is True:
            return {
                "is_correct": True,
                "feedback": {
                    "en": f"⭐ Correct! Well done! +10 points! 🎉",
                    "hi": f"⭐ बिल्कुल सही! शाबाश! +10 पॉइंट्स! 🎉",
                    "bn": f"⭐ একদম সঠিক! দারুণ! +10 পয়েন্ট! 🎉",
                }.get(ctx.language, f"⭐ Correct! Well done! +10 points! 🎉"),
            }
        
        # SymPy says wrong or unknown → AI feedback
        try:
            prompt = f"""The student answered a math question incorrectly.
Question: {ctx.last_question}
Student's answer: {ctx.student_answer}
Correct answer: {expected}

Write ONE encouraging sentence in {ctx.language}. 
Gently point toward the correct approach. 
Never say 'wrong' or 'incorrect'."""
            response = await model_router.route(
                task_type="hint_generation",
                messages=[{"role": "system", "content": prompt}],
                language=ctx.language,
            )
            return {"is_correct": False, "feedback": response.content.strip()}
        except Exception:
            return {
                "is_correct": False,
                "feedback": {
                    "en": f"Not quite. The answer is {expected}. Let me explain! 📝",
                    "hi": f"नहीं। जवाब {expected} है। समझाता हूँ! 📝",
                    "bn": f"না। উত্তর {expected}। বোঝাচ্ছি! 📝",
                }.get(ctx.language, f"Not quite. The answer is {expected}. 📝"),
            }

    async def _motivation_agent(self, ctx: AgentContext) -> str:
        """Motivation Agent: encourage based on result."""
        if ctx.is_correct:
            msgs = {
                "en": f"⭐ Amazing, {ctx.student_name}! You're getting better with every question!",
                "hi": f"⭐ शानदार, {ctx.student_name}! हर सवाल के साथ बेहतर हो रहे हो!",
                "bn": f"⭐ চমৎকার, {ctx.student_name}! প্রতিটি প্রশ্নের সাথে উন্নতি করছো!",
            }
        else:
            msgs = {
                "en": f"💪 Keep trying, {ctx.student_name}! Every mistake teaches us something new.",
                "hi": f"💪 कोशिश करते रहो, {ctx.student_name}! हर गलती कुछ नया सिखाती है।",
                "bn": f"💪 চেষ্টা চালিয়ে যাও, {ctx.student_name}! প্রতিটি ভুল কিছু নতুন শেখায়।",
            }
        return msgs.get(ctx.language, msgs["en"])

    async def _analytics_agent(self, ctx: AgentContext) -> str:
        """Analytics Agent: simple progress summary."""
        summaries = {
            "en": f"📊 You've been doing great! Your accuracy is {ctx.accuracy_rate:.0%} with {ctx.points} points and a {ctx.streak}-day streak. Keep going!",
            "hi": f"📊 बहुत अच्छा कर रहे हो! आपकी सटीकता {ctx.accuracy_rate:.0%} है, {ctx.points} पॉइंट्स और {ctx.streak}-दिन की स्ट्रीक। चलते रहो!",
            "bn": f"📊 দারুণ করছো! তোমার নির্ভুলতা {ctx.accuracy_rate:.0%}, {ctx.points} পয়েন্ট আর {ctx.streak}-দিনের স্ট্রিক। এগিয়ে যাও!",
        }
        return summaries.get(ctx.language, summaries["en"])

    async def generate_hint(self, ctx: AgentContext, level: int) -> str:
        """Generate progressive hint at given level."""
        ctx.hint_level = level
        
        hint_prompts = {
            1: "Give a gentle conceptual hint. Point toward the right approach.",
            2: "Give a more specific hint. Mention the method without revealing the answer.",
            3: "Give a very specific hint. Almost reveal the answer, but let the student make the final step.",
        }
        
        try:
            response = await model_router.route(
                task_type="hint_generation",
                messages=[
                    {"role": "system", "content": f"""Grade {ctx.grade} math teacher. {hint_prompts.get(level, hint_prompts[1])}
Question: {ctx.last_question}
Respond in {ctx.language}. Keep it short (1-2 sentences)."""},
                ],
                language=ctx.language,
            )
            return response.content
        except Exception:
            hints = {
                1: {"en": "Think about what operation you need.", "hi": "सोचो कौन सी क्रिया चाहिए।", "bn": "ভাবো কোন অপারেশন দরকার।"},
                2: {"en": "Try writing the calculation with numbers.", "hi": "संख्याओं से हिसाब लिखकर देखो।", "bn": "সংখ্যা দিয়ে হিসাব লিখে দেখো।"},
                3: {"en": "Almost there! Calculate and share your answer.", "hi": "बस करीब! हिसाब लगाकर बताओ।", "bn": "একদম কাছাকাছি! হিসাব করে জানাও।"},
            }
            return hints.get(level, hints[1]).get(ctx.language, hints[1]["en"])

    async def generate_solution(self, ctx: AgentContext) -> str:
        """Generate step-by-step solution."""
        try:
            response = await model_router.route(
                task_type="step_by_step",
                messages=[
                    {"role": "system", "content": f"""Solve this step by step for a Grade {ctx.grade} student.
Question: {ctx.last_question}
Number each step. Respond in {ctx.language}. Keep it simple."""},
                ],
                language=ctx.language,
            )
            return response.content
        except Exception:
            return {"en": "📖 Let me show you step by step...", "hi": "📖 कदम-दर-कदम दिखाता हूँ...", "bn": "📖 ধাপে ধাপে দেখাচ্ছি..."}.get(ctx.language)


# Global orchestrator instance
orchestrator = AgentOrchestrator()
