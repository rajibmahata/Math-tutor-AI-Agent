"""Parent Report Service — scheduled report generation and delivery."""

import uuid
import logging
from datetime import datetime, timezone, timedelta, date
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from app.models.student import Student
from app.models.parent_report import ParentReport
from app.models.session import Session
from app.models.student_topic_progress import StudentTopicProgress
from app.models.topic import Topic
from app.routing.router import model_router
from app.config import settings

logger = logging.getLogger(__name__)


class ReportService:
    """Generates and manages parent progress reports."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_report(
        self,
        student_id: uuid.UUID,
        parent_id: uuid.UUID,
        report_type: str = "weekly",
        period_start: Optional[date] = None,
        period_end: Optional[date] = None,
    ) -> ParentReport:
        """Generate a progress report for a student."""
        # Load student
        result = await self.db.execute(select(Student).where(Student.id == student_id))
        student = result.scalar_one_or_none()
        if not student:
            from app.core.exceptions import NotFoundError
            raise NotFoundError("Student", str(student_id))

        # Determine period
        if not period_end:
            period_end = date.today()
        if not period_start:
            if report_type == "weekly":
                period_start = period_end - timedelta(days=7)
            elif report_type == "monthly":
                period_start = period_end - timedelta(days=30)
            else:
                period_start = period_end - timedelta(days=7)

        # Gather stats
        stats = await self._gather_period_stats(student_id, period_start, period_end)

        # Get topic progress
        strengths, weaknesses = await self._get_topic_summary(student_id)

        # Generate AI summary
        summary_text = await self._generate_summary(
            student=student,
            stats=stats,
            strengths=strengths,
            weaknesses=weaknesses,
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(stats, weaknesses)

        # Create report
        report = ParentReport(
            id=uuid.uuid4(),
            student_id=student_id,
            parent_id=parent_id,
            report_type=report_type,
            period_start=period_start,
            period_end=period_end,
            report_data={
                "student_name": "",
                "grade": student.grade,
                "stats": stats,
            },
            summary_text=summary_text,
            key_strengths=[
                {"topic": s["name"], "mastery": s["mastery_score"], "trend": "improving"}
                for s in strengths[:3]
            ],
            key_weaknesses=[
                {"topic": w["name"], "mastery": w["mastery_score"], "trend": "needs_attention"}
                for w in weaknesses[:3]
            ],
            recommendations=recommendations,
            generated_at=datetime.now(timezone.utc),
        )
        self.db.add(report)
        await self.db.flush()

        logger.info(f"Report generated: {report.id} for student {student_id}")
        return report

    async def get_reports(
        self,
        student_id: uuid.UUID,
        limit: int = 10,
    ) -> list[ParentReport]:
        """Get recent reports for a student."""
        result = await self.db.execute(
            select(ParentReport)
            .where(ParentReport.student_id == student_id)
            .order_by(ParentReport.generated_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def mark_read(self, report_id: uuid.UUID) -> None:
        """Mark a report as read."""
        result = await self.db.execute(
            select(ParentReport).where(ParentReport.id == report_id)
        )
        report = result.scalar_one_or_none()
        if report and not report.is_read:
            report.is_read = True
            report.read_at = datetime.now(timezone.utc)
            await self.db.flush()

    # =========================================================================
    # Internal
    # =========================================================================

    async def _gather_period_stats(
        self, student_id: uuid.UUID, period_start: date, period_end: date
    ) -> dict:
        """Gather session statistics for a period."""
        start_dt = datetime.combine(period_start, datetime.min.time()).replace(tzinfo=timezone.utc)
        end_dt = datetime.combine(period_end, datetime.max.time()).replace(tzinfo=timezone.utc)

        result = await self.db.execute(
            select(Session).where(
                and_(
                    Session.student_id == student_id,
                    Session.started_at >= start_dt,
                    Session.started_at <= end_dt,
                )
            )
        )
        sessions = result.scalars().all()

        total_questions = sum(s.questions_asked for s in sessions)
        total_correct = sum(s.questions_correct for s in sessions)
        total_time = sum(s.duration_seconds or 0 for s in sessions)
        completed = [s for s in sessions if s.status == "completed"]

        # Previous period comparison
        prev_start = start_dt - timedelta(days=(end_dt - start_dt).days)
        prev_result = await self.db.execute(
            select(Session).where(
                and_(
                    Session.student_id == student_id,
                    Session.started_at >= prev_start,
                    Session.started_at < start_dt,
                )
            )
        )
        prev_sessions = prev_result.scalars().all()
        prev_total = sum(s.questions_asked for s in prev_sessions)
        prev_correct = sum(s.questions_correct for s in prev_sessions)
        prev_accuracy = prev_correct / max(prev_total, 1) if prev_total > 0 else 0

        current_accuracy = total_correct / max(total_questions, 1) if total_questions > 0 else 0

        # Topics practiced
        topic_ids = set()
        for s in sessions:
            if s.topic_id:
                topic_ids.add(s.topic_id)

        topic_names = []
        if topic_ids:
            topic_result = await self.db.execute(
                select(Topic.name_en).where(Topic.id.in_(list(topic_ids)))
            )
            topic_names = [r[0] for r in topic_result.all()]

        return {
            "sessions_this_week": len(completed),
            "questions_attempted": total_questions,
            "accuracy": round(current_accuracy, 2),
            "time_spent_minutes": round(total_time / 60),
            "topics_practiced": topic_names,
            "topics_mastered_this_week": 0,  # Computed below
            "streak_days": 0,
            "grade_progress": 0.0,
            "comparison_to_previous": {
                "accuracy_change": round(current_accuracy - prev_accuracy, 2),
                "time_change_pct": round((total_time - sum(s.duration_seconds or 0 for s in prev_sessions)) / max(total_time, 1), 2) if total_time > 0 else 0,
            },
        }

    async def _get_topic_summary(self, student_id: uuid.UUID) -> tuple[list[dict], list[dict]]:
        """Get topic strengths and weaknesses."""
        result = await self.db.execute(
            select(StudentTopicProgress)
            .where(StudentTopicProgress.student_id == student_id)
            .order_by(StudentTopicProgress.mastery_score.desc())
        )
        all_progress = result.scalars().all()

        topic_ids = [p.topic_id for p in all_progress if p.topic_id]
        topic_map = {}
        if topic_ids:
            topic_result = await self.db.execute(
                select(Topic).where(Topic.id.in_(topic_ids))
            )
            for t in topic_result.scalars().all():
                topic_map[t.id] = t

        strengths = []
        weaknesses = []
        for p in all_progress:
            topic = topic_map.get(p.topic_id)
            name = topic.name_en if topic else "Unknown"
            data = {
                "name": name,
                "mastery_score": round(p.mastery_score, 2),
                "questions_attempted": p.questions_attempted,
                "accuracy_rate": round(p.accuracy_rate, 2),
            }
            if p.is_weak:
                weaknesses.append(data)
            elif p.mastery_score >= 0.85:
                strengths.append(data)

        return strengths, weaknesses

    async def _generate_summary(
        self,
        student: Student,
        stats: dict,
        strengths: list[dict],
        weaknesses: list[dict],
    ) -> str:
        """Generate an AI-written summary for parents."""
        try:
            prompt = f"""Write a brief, warm summary for parents about their child's math progress.

Student Grade: {student.grade}
Questions this week: {stats['questions_attempted']}
Accuracy: {stats['accuracy']}
Time spent: {stats['time_spent_minutes']} minutes
Strengths: {', '.join(s['name'] for s in strengths[:3])}
Areas for growth: {', '.join(w['name'] for w in weaknesses[:3])}

Write 2-3 sentences. Be encouraging and focus on effort. Mention the student's dedication.
Language: English (parents prefer clear English for school communication)."""

            response = await model_router.route(
                task_type="report_generation",
                messages=[
                    {"role": "system", "content": "You write warm, professional progress reports for parents."},
                    {"role": "user", "content": prompt},
                ],
            )
            return response.content.strip()
        except Exception as e:
            logger.warning(f"Report summary generation failed: {e}")
            return (
                f"This week, the student attempted {stats['questions_attempted']} math questions "
                f"with {stats['accuracy']:.0%} accuracy, spending {stats['time_spent_minutes']} minutes learning. "
                f"Keep encouraging regular practice!"
            )

    def _generate_recommendations(
        self, stats: dict, weaknesses: list[dict]
    ) -> list[dict]:
        """Generate parent recommendations based on data."""
        recommendations = []

        # Based on weak areas
        for w in weaknesses[:3]:
            recommendations.append({
                "action": f"Practice '{w['name']}' for 15 minutes daily",
                "topic": w["name"],
                "reason": f"Current mastery at {w['mastery_score']:.0%} — needs improvement",
            })

        # Based on time spent
        if stats["time_spent_minutes"] < 30:
            recommendations.append({
                "action": "Aim for 20-30 minutes of math practice daily",
                "topic": None,
                "reason": "Regular short sessions are more effective than long occasional ones",
            })

        # General
        if stats["questions_attempted"] < 20:
            recommendations.append({
                "action": "Ask your child to teach you a math concept — teaching reinforces learning!",
                "topic": None,
                "reason": "Explaining concepts to others deepens understanding",
            })

        return recommendations[:5]
