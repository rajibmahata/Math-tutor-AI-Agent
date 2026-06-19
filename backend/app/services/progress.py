"""Progress & Analytics Service."""

import uuid
import logging
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.models.student import Student
from app.models.student_topic_progress import StudentTopicProgress
from app.models.topic import Topic
from app.models.session import Session
from app.models.assessment import Assessment

logger = logging.getLogger(__name__)


class ProgressService:
    """Progress computation and analytics."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_progress(self, student_id: uuid.UUID) -> dict:
        """Get comprehensive progress for a student."""
        # Load student
        student_result = await self.db.execute(
            select(Student).where(Student.id == student_id)
        )
        student = student_result.scalar_one_or_none()
        if not student:
            from app.core.exceptions import NotFoundError
            raise NotFoundError("Student", str(student_id))

        # Load topic progress with topics
        progress_result = await self.db.execute(
            select(StudentTopicProgress)
            .where(StudentTopicProgress.student_id == student_id)
            .order_by(StudentTopicProgress.mastery_score.desc())
        )
        all_progress = progress_result.scalars().all()

        # Load topic names
        topic_ids = [p.topic_id for p in all_progress if p.topic_id]
        topics_map = {}
        if topic_ids:
            topics_result = await self.db.execute(
                select(Topic).where(Topic.id.in_(topic_ids))
            )
            for t in topics_result.scalars().all():
                topics_map[t.id] = t

        # Categorize by topic category
        by_category = {}
        mastered_count = 0
        in_progress_count = 0

        for p in all_progress:
            topic = topics_map.get(p.topic_id)
            cat = topic.category if topic else "other"
            if cat not in by_category:
                by_category[cat] = {
                    "mastered": 0, "in_progress": 0,
                    "not_started": 0, "total_mastery": 0, "count": 0,
                }
            by_category[cat]["total_mastery"] += p.mastery_score
            by_category[cat]["count"] += 1

            if p.mastery_score >= 0.85:
                by_category[cat]["mastered"] += 1
                mastered_count += 1
            elif p.mastery_score > 0:
                by_category[cat]["in_progress"] += 1
                in_progress_count += 1

        # Compute category averages
        topics_by_category = {}
        for cat, data in by_category.items():
            topics_by_category[cat] = {
                "mastered": data["mastered"],
                "in_progress": data["in_progress"],
                "not_started": data["not_started"],
                "avg_mastery": round(data["total_mastery"] / max(data["count"], 1), 2),
            }

        # Weekly activity
        weekly = await self._get_weekly_activity(student_id)

        # Weak areas
        weak_areas = []
        strong_areas = []
        for p in all_progress:
            topic = topics_map.get(p.topic_id)
            if not topic:
                continue
            summary = {
                "topic_id": str(topic.id),
                "name": topic.name_en,
                "mastery_score": p.mastery_score,
                "questions_attempted": p.questions_attempted,
                "accuracy": p.accuracy_rate,
                "common_error": p.common_error_type,
            }
            if p.is_weak:
                weak_areas.append(summary)
            elif p.mastery_score >= 0.85:
                strong_areas.append(summary)

        # Learning velocity: topics mastered in last 30 days
        velocity = self._compute_learning_velocity(all_progress)

        # Total topics
        total_topics_result = await self.db.execute(
            select(func.count(Topic.id)).where(Topic.grade_start <= student.grade)
        )
        total_topics = total_topics_result.scalar() or 0
        remaining = max(0, total_topics - mastered_count - in_progress_count)
        grade_pct = round(mastered_count / max(total_topics, 1), 2)

        # Confidence trend (last 7 data points)
        confidence_trend = [student.confidence_score] * 7  # Simplified

        return {
            "student_id": str(student.id),
            "grade": student.grade,
            "grade_progress_pct": grade_pct,
            "topics_by_category": topics_by_category,
            "learning_velocity": velocity,
            "weekly_activity": weekly,
            "weak_areas": weak_areas[:5],
            "strong_areas": strong_areas[:5],
            "confidence_trend": confidence_trend,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

    async def get_topic_progress(
        self, student_id: uuid.UUID, topic_id: uuid.UUID
    ) -> dict:
        """Get detailed progress for a specific topic."""
        result = await self.db.execute(
            select(StudentTopicProgress)
            .where(
                and_(
                    StudentTopicProgress.student_id == student_id,
                    StudentTopicProgress.topic_id == topic_id,
                )
            )
        )
        progress = result.scalar_one_or_none()

        if not progress:
            from app.core.exceptions import NotFoundError
            raise NotFoundError("TopicProgress", f"{student_id}/{topic_id}")

        # Get topic info
        topic_result = await self.db.execute(
            select(Topic).where(Topic.id == topic_id)
        )
        topic = topic_result.scalar_one_or_none()

        # Get prerequisite topics
        from app.models.topic_prerequisite import TopicPrerequisite
        prereq_result = await self.db.execute(
            select(TopicPrerequisite).where(TopicPrerequisite.topic_id == topic_id)
        )
        prereqs = prereq_result.scalars().all()

        prerequisites = []
        for pr in prereqs:
            prereq_topic_result = await self.db.execute(
                select(Topic).where(Topic.id == pr.prerequisite_id)
            )
            prereq_topic = prereq_topic_result.scalar_one_or_none()
            if prereq_topic:
                prerequisites.append({
                    "topic_id": str(prereq_topic.id),
                    "name": prereq_topic.name_en,
                    "mastery": 0.0,  # Would load student's mastery in real implementation
                })

        # Recent assessments
        assess_result = await self.db.execute(
            select(Assessment)
            .where(
                and_(
                    Assessment.student_id == student_id,
                    Assessment.topic_id == topic_id,
                )
            )
            .order_by(Assessment.created_at.desc())
            .limit(10)
        )
        recent = assess_result.scalars().all()

        recent_accuracy = 0.0
        if recent:
            recent_correct = sum(1 for a in recent if a.is_correct)
            recent_accuracy = recent_correct / len(recent)

        # Common errors
        from collections import Counter
        error_counts = Counter(a.error_type for a in recent if a.error_type)
        common_errors = [
            {"type": etype, "count": count,
             "example": "Check your calculation"}
            for etype, count in error_counts.most_common(3)
        ]

        # Recommendations
        recommendations = []
        if progress.accuracy_rate < 0.5:
            recommendations.append({
                "action": f"Review the basics of {topic.name_en if topic else 'this topic'}",
                "topic": topic.name_en if topic else None,
            })
        if progress.hints_used > progress.questions_attempted * 0.5:
            recommendations.append({
                "action": "Try solving without hints for confidence building",
                "topic": topic.name_en if topic else None,
            })

        return {
            "topic_id": str(topic_id),
            "name": topic.name_en if topic else "Unknown",
            "category": topic.category if topic else "other",
            "grade_introduced": topic.grade_start if topic else "1",
            "mastery_score": progress.mastery_score,
            "questions_attempted": progress.questions_attempted,
            "questions_correct": progress.questions_correct,
            "accuracy_rate": progress.accuracy_rate,
            "recent_accuracy": round(recent_accuracy, 2),
            "time_spent_minutes": 0,
            "last_attempted": progress.last_attempted_at.isoformat() if progress.last_attempted_at else None,
            "is_weak": progress.is_weak,
            "common_errors": common_errors,
            "prerequisites": prerequisites,
            "recommended_actions": [r["action"] for r in recommendations],
        }

    async def _get_weekly_activity(self, student_id: uuid.UUID) -> list[dict]:
        """Get daily activity for the last 7 days."""
        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)

        result = await self.db.execute(
            select(Session)
            .where(
                and_(
                    Session.student_id == student_id,
                    Session.started_at >= seven_days_ago,
                    Session.status == "completed",
                )
            )
        )
        sessions = result.scalars().all()

        # Group by day
        daily = {}
        for s in sessions:
            day_key = s.started_at.strftime("%Y-%m-%d") if s.started_at else None
            if not day_key:
                continue
            if day_key not in daily:
                daily[day_key] = {"questions": 0, "correct": 0, "time": 0}
            daily[day_key]["questions"] += s.questions_asked
            daily[day_key]["correct"] += s.questions_correct
            daily[day_key]["time"] += s.duration_seconds or 0

        # Fill in all 7 days
        activity = []
        for i in range(6, -1, -1):
            day = (datetime.now(timezone.utc) - timedelta(days=i)).strftime("%Y-%m-%d")
            data = daily.get(day, {"questions": 0, "correct": 0, "time": 0})
            accuracy = data["correct"] / max(data["questions"], 1) if data["questions"] > 0 else 0.0
            activity.append({
                "date": day,
                "questions": data["questions"],
                "accuracy": round(accuracy, 2),
                "time_spent": data["time"],
            })

        return activity

    def _compute_learning_velocity(self, progress_list: list[StudentTopicProgress]) -> float:
        """Compute topics mastered per week."""
        mastered = sum(1 for p in progress_list if p.mastery_score >= 0.85)
        # Assume data covers ~4 weeks
        return round(mastered / 4, 1)

    async def get_topic_tree(self, grade: str, board: str = "ncert") -> dict:
        """Get the full topic tree for a grade."""
        result = await self.db.execute(
            select(Topic)
            .where(
                and_(
                    Topic.grade_start <= grade,
                    Topic.board == board,
                )
            )
            .order_by(Topic.category, Topic.topic_order)
        )
        topics = result.scalars().all()

        by_category = {}
        for t in topics:
            cat = t.category or "other"
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append({
                "id": str(t.id),
                "name_en": t.name_en,
                "name_hi": t.name_hi,
                "name_bn": t.name_bn,
                "description_en": t.description_en,
                "grade_start": t.grade_start,
                "topic_order": t.topic_order,
            })

        return {
            "grade": grade,
            "board": board,
            "categories": [
                {"category": cat, "name": cat.replace("_", " ").title(), "topics": tps}
                for cat, tps in by_category.items()
            ],
        }
