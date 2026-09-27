"""
Seed the existing Hindi/Santali training translations into the SIH 26041 SQLite DB.

Run from the backend project root:
    ./venv/bin/python seed_training_translations.py

Expected files:
    seed_training_translations.py
    trainingTranslations.json

This script only inserts/updates translation rows. It does not modify
English training content, users, progress, quizzes, or AR data.

IMPORTANT:
- Hindi rows are seeded only where the translation file contains a genuine
  Hindi value.
- Santali is intentionally NOT fabricated. Existing genuine Santali values
  are seeded and the script reports the remaining gaps for native review.
"""

import json
from pathlib import Path

from app.database.session import SessionLocal
from app.models.lesson import Lesson
from app.models.lesson_translation import LessonTranslation
from app.models.question import QuizQuestion
from app.models.question_translation import QuestionTranslation
from app.models.drill_question import DrillQuestion
from app.models.drill_question_translation import DrillQuestionTranslation

TRANSLATIONS_FILE = Path(__file__).with_name("trainingTranslations.json")


def translated(mapping, key):
    value = mapping.get(key)
    if not value or value == key:
        return None
    return value


def upsert_lesson(db, lesson, language, mapping):
    title = translated(mapping, lesson.title)
    content = translated(mapping, lesson.content)

    # Only create a row when we have both translated fields.
    if not title or not content:
        return False

    row = (
        db.query(LessonTranslation)
        .filter(
            LessonTranslation.lesson_id == lesson.id,
            LessonTranslation.language.ilike(language),
        )
        .first()
    )

    if row:
        row.title = title
        row.content = content
    else:
        db.add(
            LessonTranslation(
                lesson_id=lesson.id,
                language=language,
                title=title,
                content=content,
            )
        )
    return True


def upsert_question(db, question, language, mapping, model_cls):
    values = {
        "question": translated(mapping, question.question),
        "option_a": translated(mapping, question.option_a),
        "option_b": translated(mapping, question.option_b),
        "option_c": translated(mapping, question.option_c),
        "option_d": translated(mapping, question.option_d),
    }

    if not all(values.values()):
        return False

    row = (
        db.query(model_cls)
        .filter(
            model_cls.question_id == question.id,
            model_cls.language.ilike(language),
        )
        .first()
    )

    if row:
        for key, value in values.items():
            setattr(row, key, value)
    else:
        db.add(
            model_cls(
                question_id=question.id,
                language=language,
                **values,
            )
        )
    return True


def seed_language(db, language, mapping):
    lesson_rows = 0
    module_question_rows = 0
    drill_question_rows = 0
    lesson_gaps = []
    module_question_gaps = []
    drill_question_gaps = []

    for lesson in db.query(Lesson).all():
        if upsert_lesson(db, lesson, language, mapping):
            lesson_rows += 1
        else:
            lesson_gaps.append(lesson.title)

    for question in db.query(QuizQuestion).all():
        if upsert_question(db, question, language, mapping, QuestionTranslation):
            module_question_rows += 1
        else:
            module_question_gaps.append(question.question)

    for question in db.query(DrillQuestion).all():
        if upsert_question(
            db, question, language, mapping, DrillQuestionTranslation
        ):
            drill_question_rows += 1
        else:
            drill_question_gaps.append(question.question)

    return {
        "lessons_seeded": lesson_rows,
        "module_questions_seeded": module_question_rows,
        "drill_questions_seeded": drill_question_rows,
        "lesson_gaps": lesson_gaps,
        "module_question_gaps": module_question_gaps,
        "drill_question_gaps": drill_question_gaps,
    }


def main():
    if not TRANSLATIONS_FILE.exists():
        raise FileNotFoundError(
            f"Missing {TRANSLATIONS_FILE}. Copy trainingTranslations.json "
            "next to this script."
        )

    data = json.loads(TRANSLATIONS_FILE.read_text(encoding="utf-8"))
    db = SessionLocal()

    try:
        for language in ("hi", "sa"):
            mapping = data.get(language, {})
            result = seed_language(db, language, mapping)

            print(f"\n=== {language.upper()} TRAINING TRANSLATIONS ===")
            print(f"Lessons seeded: {result['lessons_seeded']}")
            print(f"Module questions seeded: {result['module_questions_seeded']}")
            print(f"Drill questions seeded: {result['drill_questions_seeded']}")
            print(f"Lesson gaps: {len(result['lesson_gaps'])}")
            print(f"Module-question gaps: {len(result['module_question_gaps'])}")
            print(f"Drill-question gaps: {len(result['drill_question_gaps'])}")
            for gap in result["drill_question_gaps"]:
                 

                 print("  -", gap)

            if language == "sa" and (
                result["lesson_gaps"]
                or result["module_question_gaps"]
                or result["drill_question_gaps"]
            ):
                print(
                    "NOTE: Santali gaps were left untranslated intentionally; "
                    "do not present English fallback as official Santali."
                )

        db.commit()
        print("\n=== TRANSLATION SEED COMPLETE ===")
        print("English data and AR records were not changed.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
