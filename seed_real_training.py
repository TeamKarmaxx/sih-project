"""Idempotent seed for SIH 26041's two complete AR modules.

Place this file and SIH26041_real_training_content_pack.json in the
project root (~/Desktop/sih-project), then run:

    ./venv/bin/python seed_real_training.py

It creates/updates only matching records. It does not delete unrelated data.
"""

import json
from pathlib import Path

from app.database.session import SessionLocal
from app.main import TrainingModule, Lesson, TrainingDrill, DrillQuestion, QuizQuestion

CONTENT_FILE = Path(__file__).with_name("SIH26041_real_training_content_pack.json")


def first(query):
    return query.first()


def upsert_module(db, item):
    obj = first(db.query(TrainingModule).filter(TrainingModule.title == item["title"]))
    values = {
        "title": item["title"],
        "description": item["description"],
        "difficulty": item["difficulty"],
        "language": item["language"],
    }
    if obj:
        for k, v in values.items():
            setattr(obj, k, v)
        return obj, False
    obj = TrainingModule(**values)
    db.add(obj)
    db.flush()
    return obj, True


def upsert_lesson(db, module_id, item):
    obj = first(db.query(Lesson).filter(
        Lesson.module_id == module_id,
        Lesson.title == item["title"],
    ))
    values = {"title": item["title"], "content": item["content"], "module_id": module_id}
    if obj:
        for k, v in values.items():
            setattr(obj, k, v)
        return obj, False
    obj = Lesson(**values)
    db.add(obj)
    db.flush()
    return obj, True


def upsert_drill(db, module_id, item):
    obj = first(db.query(TrainingDrill).filter(
        TrainingDrill.module_id == module_id,
        TrainingDrill.title == item["title"],
    ))
    values = {
        "module_id": module_id,
        "title": item["title"],
        "description": item["description"],
        "instructions": item["instructions"],
        "difficulty": item["difficulty"],
        "ar_scene": item["ar_scene"],
        "equipment": item["equipment"],
        "scenario": item["scenario"],
        "hazard_type": item["hazard_type"],
        "safety_action": item["safety_action"],
    }
    if obj:
        for k, v in values.items():
            setattr(obj, k, v)
        return obj, False
    obj = TrainingDrill(**values)
    db.add(obj)
    db.flush()
    return obj, True


def upsert_drill_questions(db, drill_id, questions):
    created = 0
    for item in questions:
        obj = first(db.query(DrillQuestion).filter(
            DrillQuestion.drill_id == drill_id,
            DrillQuestion.question == item["question"],
        ))
        values = {
            "drill_id": drill_id,
            "question": item["question"],
            "option_a": item["option_a"],
            "option_b": item["option_b"],
            "option_c": item["option_c"],
            "option_d": item["option_d"],
            "correct_answer": item["correct_answer"],
        }
        if obj:
            for k, v in values.items():
                setattr(obj, k, v)
        else:
            db.add(DrillQuestion(**values))
            created += 1
    return created


def upsert_module_questions(db, module_id, questions):
    created = 0
    for item in questions:
        question, a, b, c, d, correct = item
        obj = first(db.query(QuizQuestion).filter(
            QuizQuestion.module_id == module_id,
            QuizQuestion.question == question,
        ))
        values = {
            "module_id": module_id,
            "question": question,
            "option_a": a,
            "option_b": b,
            "option_c": c,
            "option_d": d,
            "correct_answer": correct,
        }
        if obj:
            for k, v in values.items():
                setattr(obj, k, v)
        else:
            db.add(QuizQuestion(**values))
            created += 1
    return created


def main():
    if not CONTENT_FILE.exists():
        raise FileNotFoundError(f"Missing {CONTENT_FILE.name}")

    content = json.loads(CONTENT_FILE.read_text(encoding="utf-8"))
    db = SessionLocal()
    counts = {"modules": 0, "lessons": 0, "drills": 0, "drill_questions": 0, "module_questions": 0}

    try:
        for item in content["modules"]:
            module, created = upsert_module(db, item)
            counts["modules"] += int(created)

            for lesson in item["lessons"]:
                _, created = upsert_lesson(db, module.id, lesson)
                counts["lessons"] += int(created)

            drill, created = upsert_drill(db, module.id, item["drill"])
            counts["drills"] += int(created)
            counts["drill_questions"] += upsert_drill_questions(db, drill.id, item["drill"]["questions"])
            counts["module_questions"] += upsert_module_questions(db, module.id, item["module_assessment"])

        db.commit()
        print("\n=== SIH 26041 CONTENT SEED COMPLETE ===")
        for key, value in counts.items():
            print(f"{key.replace('_', ' ').title()}: {value}")
        print("\nMatching records were updated instead of duplicated.")
        print("No unrelated existing records were deleted.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
