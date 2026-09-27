import json
from pathlib import Path

from app.database.session import SessionLocal

from app.models.lesson import Lesson
from app.models.lesson_translation import LessonTranslation

from app.models.question import QuizQuestion
from app.models.question_translation import QuestionTranslation

from app.models.drill_question import DrillQuestion
from app.models.drill_question_translation import DrillQuestionTranslation


OUTPUT = Path(
    "/Users/aliyapatel/Desktop/sih-safety-app/src/locales/backendTranslations.json"
)

db = SessionLocal()

result = {
    "hi": {},
    "sa": {}
}


def add_translation(language, english, translated):
    if not english or not translated:
        return

    english = str(english)
    translated = str(translated)

    # Don't export untranslated database values.
    if english == translated:
        return

    result[language][english] = translated


try:

    # =========================================================
    # LESSONS
    # =========================================================

    lessons = {
        lesson.id: lesson
        for lesson in db.query(Lesson).all()
    }

    lesson_translations = db.query(LessonTranslation).all()

    for row in lesson_translations:

        language = row.language.lower()

        if language not in result:
            continue

        lesson = lessons.get(row.lesson_id)

        if not lesson:
            continue

        # English title -> translated title
        add_translation(
            language,
            lesson.title,
            row.title
        )

        # English content -> translated content
        add_translation(
            language,
            lesson.content,
            row.content
        )


    # =========================================================
    # MODULE QUIZ QUESTIONS
    # =========================================================

    questions = {
        question.id: question
        for question in db.query(QuizQuestion).all()
    }

    question_translations = db.query(
        QuestionTranslation
    ).all()

    for row in question_translations:

        language = row.language.lower()

        if language not in result:
            continue

        question = questions.get(row.question_id)

        if not question:
            continue

        fields = [
            "question",
            "option_a",
            "option_b",
            "option_c",
            "option_d"
        ]

        for field in fields:

            english = getattr(question, field, None)
            translated = getattr(row, field, None)

            add_translation(
                language,
                english,
                translated
            )


    # =========================================================
    # DRILL QUESTIONS
    # =========================================================

    drills = {
        drill.id: drill
        for drill in db.query(DrillQuestion).all()
    }

    drill_translations = db.query(
        DrillQuestionTranslation
    ).all()

    for row in drill_translations:

        language = row.language.lower()

        if language not in result:
            continue

        drill = drills.get(row.question_id)

        if not drill:
            continue

        fields = [
            "question",
            "option_a",
            "option_b",
            "option_c",
            "option_d"
        ]

        for field in fields:

            english = getattr(drill, field, None)
            translated = getattr(row, field, None)

            add_translation(
                language,
                english,
                translated
            )


    # =========================================================
    # SAVE
    # =========================================================

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            result,
            f,
            ensure_ascii=False,
            indent=2
        )


    print()
    print("======================================")
    print("CORRECT TRANSLATION EXPORT COMPLETE")
    print("======================================")
    print("Hindi translations:", len(result["hi"]))
    print("Santali translations:", len(result["sa"]))
    print()
    print("Saved to:")
    print(OUTPUT)
    print("======================================")


finally:
    db.close()
