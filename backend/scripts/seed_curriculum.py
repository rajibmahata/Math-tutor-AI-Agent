"""
Seed Curriculum Data — NCERT Mathematics Topics for Class 1-10
Run once: python scripts/seed_curriculum.py
"""

import asyncio
import uuid
from sqlalchemy import text
from app.core.database import async_session, engine
from app.models.topic import Topic
from app.models.topic_prerequisite import TopicPrerequisite

# =============================================================================
# Curriculum Data: NCERT Mathematics by Grade
# =============================================================================

NCERT_CURRICULUM = {
    "1": {
        "number_sense": [
            {
                "name_en": "Numbers 1 to 20",
                "name_hi": "संख्या 1 से 20",
                "name_bn": "সংখ্যা ১ থেকে ২০",
                "description_en": "Recognizing, counting, and writing numbers from 1 to 20.",
                "order": 1,
            },
            {
                "name_en": "Numbers 21 to 100",
                "name_hi": "संख्या 21 से 100",
                "name_bn": "সংখ্যা ২১ থেকে ১০০",
                "description_en": "Place value, counting forward/backward, number names.",
                "order": 2,
            },
        ],
        "arithmetic": [
            {
                "name_en": "Addition (1-digit)",
                "name_hi": "जोड़ (1-अंकीय)",
                "name_bn": "যোগ (১-অঙ্ক)",
                "description_en": "Adding single-digit numbers with and without pictures.",
                "order": 3,
            },
            {
                "name_en": "Subtraction (1-digit)",
                "name_hi": "घटाव (1-अंकीय)",
                "name_bn": "বিয়োগ (১-অঙ্ক)",
                "description_en": "Subtracting single-digit numbers using objects and number line.",
                "order": 4,
            },
        ],
        "measurement": [
            {
                "name_en": "Length and Weight",
                "name_hi": "लंबाई और वजन",
                "name_bn": "দৈর্ঘ্য ও ওজন",
                "description_en": "Comparing objects by length and weight (longer/shorter, heavier/lighter).",
                "order": 5,
            },
            {
                "name_en": "Time",
                "name_hi": "समय",
                "name_bn": "সময়",
                "description_en": "Reading time on an analog clock (hour hand), days of the week.",
                "order": 6,
            },
        ],
        "geometry": [
            {
                "name_en": "Shapes and Space",
                "name_hi": "आकृतियाँ और स्थान",
                "name_bn": "আকৃতি ও স্থান",
                "description_en": "Identifying basic 2D shapes: circle, square, triangle, rectangle.",
                "order": 7,
            },
        ],
        "data_handling": [
            {
                "name_en": "Data Handling (Pictographs)",
                "name_hi": "आँकड़ों का प्रबंधन",
                "name_bn": "তথ্য ব্যবস্থাপনা",
                "description_en": "Reading and creating simple pictographs.",
                "order": 8,
            },
        ],
    },
    "2": {
        "number_sense": [
            {
                "name_en": "Numbers up to 200",
                "name_hi": "200 तक की संख्याएँ",
                "name_bn": "২০০ পর্যন্ত সংখ্যা",
                "description_en": "Place value (hundreds, tens, ones), ordering, comparison.",
                "order": 1,
            },
        ],
        "arithmetic": [
            {
                "name_en": "Addition (2-digit)",
                "name_hi": "जोड़ (2-अंकीय)",
                "name_bn": "যোগ (২-অঙ্ক)",
                "description_en": "Adding two-digit numbers with and without carry-over.",
                "order": 2,
            },
            {
                "name_en": "Subtraction (2-digit)",
                "name_hi": "घटाव (2-अंकीय)",
                "name_bn": "বিয়োগ (২-অঙ্ক)",
                "description_en": "Subtracting two-digit numbers with and without borrowing.",
                "order": 3,
            },
            {
                "name_en": "Multiplication Concepts",
                "name_hi": "गुणा की अवधारणा",
                "name_bn": "গুণের ধারণা",
                "description_en": "Introduction to multiplication as repeated addition.",
                "order": 4,
            },
        ],
        "measurement": [
            {
                "name_en": "Money",
                "name_hi": "पैसे",
                "name_bn": "টাকা-পয়সা",
                "description_en": "Recognizing coins and notes, simple transactions.",
                "order": 5,
            },
        ],
        "geometry": [
            {
                "name_en": "Lines and Shapes",
                "name_hi": "रेखाएँ और आकृतियाँ",
                "name_bn": "রেখা ও আকৃতি",
                "description_en": "Straight and curved lines, 3D shapes introduction.",
                "order": 6,
            },
        ],
    },
    "3": {
        "number_sense": [
            {
                "name_en": "Numbers up to 1000",
                "name_hi": "1000 तक की संख्याएँ",
                "name_bn": "১০০০ পর্যন্ত সংখ্যা",
                "description_en": "Place value up to thousands, Roman numerals (I, V, X, L, C).",
                "order": 1,
            },
        ],
        "arithmetic": [
            {
                "name_en": "Addition (3-digit)",
                "name_hi": "जोड़ (3-अंकीय)",
                "name_bn": "যোগ (৩-অঙ্ক)",
                "description_en": "Adding three-digit numbers with carry-over.",
                "order": 2,
            },
            {
                "name_en": "Subtraction (3-digit)",
                "name_hi": "घटाव (3-अंकीय)",
                "name_bn": "বিয়োগ (৩-অঙ্ক)",
                "description_en": "Subtracting three-digit numbers with borrowing.",
                "order": 3,
            },
            {
                "name_en": "Multiplication Tables (1-5)",
                "name_hi": "पहाड़े (1-5)",
                "name_bn": "নামতা (১-৫)",
                "description_en": "Memorizing and applying multiplication tables 1 through 5.",
                "order": 4,
            },
            {
                "name_en": "Division Concepts",
                "name_hi": "भाग की अवधारणा",
                "name_bn": "ভাগের ধারণা",
                "description_en": "Introduction to division as equal sharing and repeated subtraction.",
                "order": 5,
            },
        ],
        "fractions": [
            {
                "name_en": "Fractions (Basic)",
                "name_hi": "भिन्न (बुनियादी)",
                "name_bn": "ভগ্নাংশ (মৌলিক)",
                "description_en": "Understanding half, quarter, three-quarters using shapes.",
                "order": 6,
            },
        ],
        "measurement": [
            {
                "name_en": "Length (m, cm)",
                "name_hi": "लंबाई (मी, सेमी)",
                "name_bn": "দৈর্ঘ্য (মি, সেমি)",
                "description_en": "Measuring length in meters and centimeters.",
                "order": 7,
            },
            {
                "name_en": "Weight (kg, g)",
                "name_hi": "वजन (किग्रा, ग्राम)",
                "name_bn": "ওজন (কেজি, গ্রাম)",
                "description_en": "Measuring weight in kilograms and grams.",
                "order": 8,
            },
        ],
        "geometry": [
            {
                "name_en": "2D Shapes (Properties)",
                "name_hi": "2D आकृतियाँ (गुण)",
                "name_bn": "2D আকৃতি (বৈশিষ্ট্য)",
                "description_en": "Sides, corners of squares, rectangles, triangles, circles.",
                "order": 9,
            },
        ],
    },
}

# Additional grades (4-10) follow the same pattern — refer to docs/database-schema.md
# Full curriculum seeding would include all grades


# =============================================================================
# Seed Runner
# =============================================================================

async def seed_curriculum():
    """Seed the topics table with NCERT curriculum data."""
    async with async_session() as session:
        count = 0
        for grade, categories in NCERT_CURRICULUM.items():
            for category, topics in categories.items():
                for topic_data in topics:
                    topic = Topic(
                        id=uuid.uuid4(),
                        name_en=topic_data["name_en"],
                        name_hi=topic_data.get("name_hi"),
                        name_bn=topic_data.get("name_bn"),
                        description_en=topic_data.get("description_en"),
                        grade_start=grade,
                        board="ncert",
                        topic_order=topic_data["order"],
                        category=category,
                        difficulty_base=0.3,
                    )
                    session.add(topic)
                    count += 1

        await session.commit()
        print(f"✅ Seeded {count} curriculum topics across {len(NCERT_CURRICULUM)} grades.")


async def main():
    print("🌱 Seeding GanitMitra curriculum data...")
    await seed_curriculum()
    print("✅ Curriculum seed complete.")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
