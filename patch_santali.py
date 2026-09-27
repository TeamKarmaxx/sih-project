from app.database.session import SessionLocal
from app.models.lesson import Lesson
from app.models.question_translation import QuestionTranslation
from app.models.drill_question_translation import DrillQuestionTranslation
from app.models.lesson_translation import LessonTranslation
from app.models.drill_question import DrillQuestion
from app.models.question import QuizQuestion 


LANG = "sa"


def upsert_lesson(db, english_title, sa_title, sa_content):
    lesson = db.query(Lesson).filter(Lesson.title == english_title).first()

    if not lesson:
        print("Lesson not found:", english_title)
        return

    existing = (
        db.query(LessonTranslation)
        .filter(
            LessonTranslation.lesson_id == lesson.id,
            LessonTranslation.language == LANG,
        )
        .first()
    )

    if existing:
        existing.title = sa_title
        existing.content = sa_content
    else:
        db.add(
            LessonTranslation(
                lesson_id=lesson.id,
                language=LANG,
                title=sa_title,
                content=sa_content,
            )
        )


def upsert_question(db, english_question, values, model):
    question = db.query(model).filter(model.question == english_question).first()

    if not question:
        print("Question not found:", english_question)
        return

    existing = (
        db.query(
            QuestionTranslation
            if model == QuizQuestion
            else DrillQuestionTranslation
        )
        .filter(
            (
                QuestionTranslation.question_id == question.id
                if model == QuizQuestion
                else DrillQuestionTranslation.question_id == question.id
            ),
            (
                QuestionTranslation.language == LANG
                if model == QuizQuestion
                else DrillQuestionTranslation.language == LANG
            ),
        )
        .first()
    )

    TranslationModel = (
        QuestionTranslation
        if model == QuizQuestion
        else DrillQuestionTranslation
    )

    q, a, b, c, d = values

    if existing:
        existing.question = q
        existing.option_a = a
        existing.option_b = b
        existing.option_c = c
        existing.option_d = d
    else:
        db.add(
            TranslationModel(
                question_id=question.id,
                language=LANG,
                question=q,
                option_a=a,
                option_b=b,
                option_c=c,
                option_d=d,
            )
        )


db = SessionLocal()

try:

    # =========================================================
    # LESSONS
    # =========================================================

    lessons = {

        "Introduction to Mining Safety": (
            "ᱢᱟᱭᱤᱱᱤᱝ ᱥᱟᱯᱷᱟᱹᱭ ᱥᱩᱨᱚᱠᱷᱟ ᱪᱮᱫᱟ",
            """ᱢᱟᱭᱤᱱᱤᱝ ᱡᱟᱭᱜᱟᱨᱮ ᱠᱟᱹᱢᱤ ᱠᱚ ᱞᱟᱹᱜᱤᱫ ᱢᱩᱞ ᱥᱩᱨᱚᱠᱷᱟ ᱱᱤᱭᱚᱢ ᱟᱨ ᱥᱟᱹᱵᱫᱷᱟᱱᱤ ᱡᱟᱹᱨᱩᱨᱤ ᱠᱟᱱᱟ᱾

ᱠᱟᱹᱢᱤ ᱥᱮᱫ ᱡᱟᱭᱜᱟᱨᱮ ᱥᱩᱨᱚᱠᱷᱟ ᱱᱤᱭᱚᱢ ᱢᱟᱱᱟᱣ ᱟᱨ ᱡᱚᱛᱚ ᱵᱤᱯᱚᱫ ᱠᱚ ᱵᱩᱡᱷᱟᱹᱣ ᱡᱟᱹᱨᱩᱨᱤ ᱠᱟᱱᱟ᱾"""
        ),

        "Recognizing an Industrial Emergency": (
            "ᱤᱱᱰᱟᱥᱴᱨᱤ ᱵᱤᱯᱚᱫ ᱵᱩᱡᱷᱟᱹᱣ",
            """ᱤᱱᱰᱟᱥᱴᱨᱤ ᱵᱤᱯᱚᱫ ᱨᱮ ᱥᱮᱫ ᱞᱟᱹᱴᱷᱟ, ᱫᱷᱩᱣᱟᱹ, ᱢᱮᱥᱤᱱ ᱵᱤᱜᱟᱹᱨ, ᱡᱚᱢᱤᱱ ᱥᱮ ᱪᱷᱟᱛ ᱵᱤᱯᱚᱫ, ᱵᱮᱞᱮᱱᱴᱤᱞᱮᱥᱚᱱ ᱵᱟᱝ ᱞᱮᱠᱟ ᱜᱚᱴᱟ ᱵᱤᱯᱚᱫ ᱦᱚᱭᱚᱜᱼᱟ᱾

ᱡᱷᱟᱹᱞᱟᱹ ᱥᱮ ᱵᱤᱯᱚᱫ ᱥᱚᱫᱚᱨ ᱠᱷᱚᱱ ᱯᱷᱚᱨᱚᱢ ᱠᱚ ᱵᱩᱡᱷᱟᱹᱣ ᱢᱮ, ᱠᱟᱹᱢᱤ ᱵᱚᱸᱫ ᱢᱮ ᱟᱨ ᱥᱟᱹᱯᱷᱟᱹᱭ ᱡᱟᱭᱜᱟ ᱫᱮ ᱪᱟᱞᱟᱣ ᱢᱮ᱾

ᱡᱟᱭᱜᱟᱭᱟᱜ ᱵᱤᱯᱚᱫ ᱯᱚᱨᱤᱠᱟᱞᱯᱚᱱᱟ, ᱯᱟᱞᱟᱣ ᱨᱚᱥᱛᱟ ᱟᱨ ᱡᱚᱢᱟᱣ ᱡᱟᱭᱜᱟ ᱵᱟᱵᱚᱫ ᱥᱤᱠᱷᱟᱹᱣ ᱡᱟᱹᱨᱩᱨᱤ ᱠᱟᱱᱟ᱾"""
        ),

        "Safe Evacuation Awareness": (
            "ᱥᱟᱯᱷᱟᱹᱭ ᱯᱟᱞᱟᱣ ᱵᱟᱵᱚᱫ ᱵᱩᱡᱷᱟᱹᱣ",
            """ᱯᱟᱞᱟᱣ ᱠᱟᱹᱢᱤ ᱥᱟᱹᱯᱷᱟᱹᱭ ᱨᱚᱥᱛᱟ ᱟᱨ ᱡᱟᱭᱜᱟᱭᱟᱜ ᱵᱤᱯᱚᱫ ᱱᱤᱭᱚᱢ ᱞᱮᱠᱟ ᱦᱚᱭᱚᱜ ᱠᱟᱱᱟ᱾

ᱠᱟᱹᱢᱤ ᱠᱚ ᱟᱡᱟᱜ ᱪᱟᱨᱤᱫ ᱯᱟᱥᱮ ᱧᱮᱞ ᱫᱟᱲᱮ, ᱵᱟᱹᱝ ᱞᱟᱹᱜᱤᱫ ᱫᱷᱤᱞ ᱵᱟᱝ ᱢᱮ ᱟᱨ ᱡᱚᱢᱟᱣ ᱥᱮ ᱥᱟᱯᱷᱟᱹᱭ ᱡᱟᱭᱜᱟ ᱨᱮ ᱥᱮᱫ ᱢᱮ᱾

ᱡᱤᱱᱤᱥ ᱥᱮ ᱥᱟᱢᱟᱱ ᱞᱟᱹᱜᱤᱫ ᱵᱤᱯᱚᱫ ᱡᱟᱭᱜᱟ ᱫᱮ ᱵᱟᱝ ᱨᱩᱦᱟᱹᱲ ᱢᱮ᱾

ᱡᱟᱭᱜᱟ ᱠᱷᱟᱹᱴᱤᱨ ᱯᱟᱞᱟᱣ ᱨᱚᱥᱛᱟ, ᱡᱚᱢᱟᱣ ᱡᱟᱭᱜᱟ, ᱡᱷᱟᱹᱞᱟᱹ ᱥᱟᱹᱱᱫᱮᱥ ᱟᱨ ᱵᱤᱯᱚᱫ ᱥᱚᱢᱯᱚᱨᱠᱚ ᱥᱤᱠᱷᱟᱹᱣ ᱨᱮ ᱥᱮᱫ ᱠᱟᱛᱮ ᱵᱩᱡᱷᱟᱹᱣ ᱢᱮ᱾"""
        ),

        "Fire Hazard Awareness": (
            "ᱥᱮᱫ ᱵᱤᱯᱚᱫ ᱵᱟᱵᱚᱫ ᱵᱩᱡᱷᱟᱹᱣ",
            """ᱥᱮᱫ ᱵᱤᱯᱚᱫ ᱯᱨᱟᱛᱤᱨᱚᱫᱷ ᱞᱟᱹᱜᱤᱫ ᱵᱤᱯᱚᱫ ᱵᱩᱡᱷᱟᱹᱣ ᱟᱨ ᱵᱟᱝ ᱥᱟᱹᱯᱷᱟᱹᱭ ᱠᱟᱹᱢᱤ ᱨᱤᱯᱚᱨᱴ ᱢᱮ᱾

ᱠᱷᱟᱨᱟᱯ ᱤᱞᱮᱠᱴᱨᱤᱠ ᱥᱟᱢᱟᱱ, ᱡᱟᱹᱞᱟᱣ ᱢᱮᱥᱤᱱ, ᱡᱟᱹᱞᱟᱣ ᱡᱤᱱᱤᱥ ᱞᱮᱠᱟ ᱵᱤᱯᱚᱫ ᱠᱚ ᱵᱩᱡᱷᱟᱹᱣ ᱢᱮ᱾

ᱵᱤᱯᱚᱫ ᱵᱮᱞᱟ ᱨᱮ ᱱᱤᱡᱟᱜ ᱥᱤᱠᱷᱟᱹᱣ ᱟᱨ ᱟᱹᱲᱤ ᱛᱮ ᱢᱚᱱᱡᱩᱨ ᱠᱟᱹᱢᱤ ᱠᱟᱛᱮ ᱯᱟᱞᱟᱣ ᱟᱨ ᱥᱚᱫᱚᱨ ᱠᱟᱹᱢᱤ ᱫᱚ ᱯᱷᱚᱞᱟᱣ ᱢᱮ᱾"""
        ),

        "Underground Tunnel Hazards": (
            "ᱡᱚᱢᱤᱱ ᱵᱷᱟᱜ ᱛᱩᱱᱮᱞ ᱵᱤᱯᱚᱫ",
            """ᱡᱚᱢᱤᱱ ᱛᱟᱞᱟ ᱠᱟᱹᱢᱤ ᱨᱮ ᱵᱮᱞᱮᱱᱴᱤᱞᱮᱥᱚᱱ, ᱡᱚᱢᱤᱱ ᱠᱚᱱᱰᱤᱥᱚᱱ, ᱥᱮᱫ, ᱢᱮᱥᱤᱱ ᱟᱨ ᱵᱤᱯᱚᱫᱡᱚᱱᱟ ᱵᱟᱭᱩ ᱞᱮᱠᱟ ᱠᱟᱹᱢᱤ ᱠᱚ ᱯᱚᱱᱛᱮ ᱠᱟᱱᱟ᱾

ᱢᱟᱭᱤᱱ ᱨᱮ ᱢᱚᱱᱡᱩᱨ ᱠᱟᱹᱢᱤ ᱱᱤᱭᱚᱢ ᱟᱨ ᱵᱤᱯᱚᱫ ᱵᱮᱵᱥᱛᱟ ᱢᱟᱱᱟᱣ ᱢᱮ᱾

ᱵᱮᱞᱮᱱᱴᱤᱞᱮᱥᱚᱱ ᱨᱮ ᱠᱷᱟᱹᱴᱤ ᱦᱚᱭᱚᱜ ᱞᱮ ᱟᱥᱟᱱ ᱠᱟᱹᱢᱤ ᱥᱟᱯᱷᱟᱹᱭ ᱟᱨ ᱵᱟᱹᱭᱩ ᱵᱟᱵᱚᱫ ᱵᱤᱯᱚᱫ ᱦᱚᱭᱚᱜᱼᱟ᱾ ᱵᱮᱞᱮᱱᱴᱤᱞᱮᱥᱚᱱ ᱠᱚᱱᱴᱨᱚᱞ ᱵᱟᱝ ᱡᱟᱹᱛᱤ ᱛᱮ ᱵᱟᱝ ᱵᱚᱫᱞᱟᱣ ᱢᱮ᱾"""
        ),

        "Hazardous Atmosphere Awareness": (
            "ᱵᱤᱯᱚᱫᱡᱚᱱᱟ ᱵᱟᱭᱩ ᱵᱟᱵᱚᱫ ᱵᱩᱡᱷᱟᱹᱣ",
            """ᱵᱤᱯᱚᱫᱡᱚᱱᱟ ᱵᱟᱭᱩ ᱫᱚ ᱦᱟᱹᱞᱤ ᱛᱮ ᱥᱚᱫᱚᱨ ᱵᱟᱝ ᱦᱚᱭᱚᱜ ᱥᱟᱢᱵᱷᱟᱵᱱᱟ ᱢᱮᱱᱟᱜᱼᱟ᱾ ᱟᱹᱭᱟᱹᱛ ᱜᱮᱥ ᱢᱚᱱᱤᱴᱚᱨᱤᱝ ᱟᱨ ᱵᱮᱞᱮᱱᱴᱤᱞᱮᱥᱚᱱ ᱥᱤᱥᱴᱮᱢ ᱡᱚᱢᱤᱱ ᱛᱟᱞᱟ ᱥᱩᱨᱚᱠᱷᱟ ᱞᱟᱹᱜᱤᱫ ᱡᱟᱹᱨᱩᱨᱤ ᱠᱟᱱᱟ᱾

ᱟᱞᱟᱨᱢ ᱟᱨ ᱵᱟᱝ ᱥᱟᱢᱟᱱᱭ ᱨᱤᱰᱤᱝ ᱠᱚ ᱜᱚᱱᱚᱝ ᱢᱮ, ᱡᱟᱭᱜᱟᱭᱟᱜ ᱱᱤᱭᱚᱢ ᱢᱟᱱᱟᱣ ᱢᱮ ᱟᱨ ᱡᱟᱦᱟᱸ ᱟᱫᱮᱥ ᱦᱚᱭᱚᱜ ᱛᱟᱦᱟᱸ ᱥᱟᱯᱷᱟᱹᱭ ᱡᱟᱭᱜᱟ ᱫᱮ ᱪᱟᱞᱟᱣ ᱢᱮ᱾

ᱢᱤᱫ ᱵᱤᱯᱚᱫᱡᱚᱱᱟ ᱡᱟᱭᱜᱟ ᱨᱮ ᱵᱟᱝ ᱥᱮᱫ ᱟᱨ ᱵᱟᱝ ᱛᱟᱦᱟᱸ ᱢᱮ᱾"""
        ),

        "Ventilation and Emergency Response": (
            "ᱵᱮᱞᱮᱱᱴᱤᱞᱮᱥᱚᱱ ᱟᱨ ᱵᱤᱯᱚᱫ ᱯᱟᱹᱞᱟᱣ",
            """ᱵᱮᱞᱮᱱᱴᱤᱞᱮᱥᱚᱱ ᱫᱚ ᱡᱚᱢᱤᱱ ᱛᱟᱞᱟ ᱵᱟᱭᱩ ᱥᱟᱯᱷᱟᱹ ᱛᱟᱦᱟᱸ ᱟᱨ ᱥᱩᱨᱚᱠᱷᱤᱛ ᱠᱟᱹᱢᱤ ᱞᱟᱹᱜᱤᱫ ᱜᱚᱲᱚ ᱠᱟᱱᱟ᱾

ᱵᱮᱞᱮᱱᱴᱤᱞᱮᱥᱚᱱ ᱵᱟᱝ ᱪᱟᱞᱟᱣ ᱥᱮ ᱵᱟᱭᱩ ᱟᱞᱟᱨᱢ ᱦᱚᱭᱚᱜ ᱠᱷᱟᱱ ᱢᱟᱭᱤᱱ ᱵᱤᱯᱚᱫ ᱱᱤᱭᱚᱢ ᱢᱟᱱᱟᱣ ᱢᱮ, ᱵᱤᱯᱚᱫ ᱵᱟᱵᱚᱫ ᱥᱚᱫᱚᱨ ᱢᱮ ᱟᱨ ᱡᱟᱦᱟᱸ ᱟᱫᱮᱥ ᱦᱚᱭᱚᱜ ᱛᱟᱦᱟᱸ ᱥᱟᱯᱷᱟᱹᱭ ᱡᱟᱭᱜᱟ ᱫᱮ ᱪᱟᱞᱟᱣ ᱢᱮ᱾

ᱵᱮᱞᱮᱱᱴᱤᱞᱮᱥᱚᱱ ᱨᱮ ᱴᱮᱠᱱᱤᱠᱟᱞ ᱵᱚᱫᱞᱟᱣ ᱫᱚ ᱥᱤᱯᱷᱟᱹᱭ ᱟᱨ ᱟᱹᱲᱤ ᱛᱮ ᱛᱟᱹᱲᱟᱣ ᱠᱟᱹᱢᱤ ᱠᱚ ᱮᱢ ᱢᱮ᱾"""
        ),
    }

    for title, (sa_title, sa_content) in lessons.items():
        upsert_lesson(db, title, sa_title, sa_content)


    # =========================================================
    # DRILL QUESTIONS
    # =========================================================

    drill = {

        "When an authorized emergency warning is received, what should be the first priority?": (
            "ᱢᱤᱫ ᱢᱚᱱᱡᱩᱨ ᱵᱤᱯᱚᱫ ᱥᱚᱫᱚᱨ ᱧᱟᱢ ᱠᱷᱟᱱ ᱢᱩᱞ ᱠᱟᱹᱢᱤ ᱪᱮᱫ ᱠᱟᱱᱟ?",
            "ᱥᱟᱫᱷᱟᱨᱚᱱ ᱠᱟᱹᱢᱤ ᱪᱟᱞᱟᱣ ᱢᱮ",
            "ᱵᱤᱯᱚᱫ ᱱᱤᱭᱚᱢ ᱢᱟᱱᱟᱣ ᱟᱨ ᱥᱩᱨᱚᱠᱷᱟ ᱫᱮ ᱪᱟᱞᱟᱣ ᱢᱮ",
            "ᱡᱤᱱᱤᱥ ᱟᱹᱜᱩ ᱟᱹᱜᱩ ᱱᱟᱯᱟᱢ ᱢᱮ",
            "ᱟᱞᱟᱨᱢ ᱵᱟᱝ ᱜᱚᱱᱚᱝ ᱢᱮ"
        ),

        "Where should a worker go after completing the designated evacuation route?": (
            "ᱯᱟᱞᱟᱣ ᱨᱚᱥᱛᱟ ᱪᱟᱵᱟ ᱠᱟᱛᱮ ᱠᱟᱹᱢᱤ ᱦᱚᱲ ᱚᱠᱟ ᱛᱮ ᱥᱮᱫ ᱢᱮ?",
            "ᱵᱤᱯᱚᱫ ᱠᱟᱹᱢᱤ ᱡᱟᱭᱜᱟ",
            "ᱡᱟᱭᱜᱟ ᱵᱟᱦᱨᱮ ᱡᱮ ᱠᱚᱱᱟ ᱡᱟᱭᱜᱟ",
            "ᱢᱚᱱᱡᱩᱨ ᱥᱟᱯᱷᱟᱹᱭ ᱥᱮ ᱡᱚᱢᱟᱣ ᱡᱟᱭᱜᱟ",
            "ᱵᱟᱝ ᱟᱫᱮᱥ ᱡᱟᱭᱜᱟ"
        ),

        "What should a worker do if an emergency action is beyond their training or authorization?": (
            "ᱵᱤᱯᱚᱫ ᱠᱟᱹᱢᱤ ᱱᱤᱡᱟᱜ ᱥᱤᱠᱷᱟᱹᱣ ᱥᱮ ᱢᱚᱱᱡᱩᱨ ᱮᱞᱟᱠᱟ ᱵᱟᱦᱨᱮ ᱛᱟᱦᱟᱸ ᱠᱷᱟᱱ ᱪᱮᱫ ᱠᱟᱹᱢᱤ ᱢᱮ?",
            "ᱵᱟᱝ ᱥᱤᱠᱷᱟᱹᱣ ᱠᱟᱹᱢᱤ ᱪᱟᱹᱞᱩ ᱢᱮ",
            "ᱢᱚᱱᱡᱩᱨ ᱵᱤᱯᱚᱫ ᱱᱤᱭᱚᱢ ᱢᱟᱱᱟᱣ ᱟᱨ ᱟᱹᱲᱤ ᱥᱟᱦᱟᱭ ᱧᱟᱢ ᱢᱮ",
            "ᱵᱤᱯᱚᱫ ᱞᱩᱠᱟᱹᱣ ᱢᱮ",
            "ᱥᱟᱫᱷᱟᱨᱚᱱ ᱠᱟᱹᱢᱤ ᱫᱮ ᱨᱩᱦᱟᱹᱲ ᱢᱮ"
        ),

        "Why should workers avoid returning to an affected area after evacuation?": (
            "ᱯᱟᱞᱟᱣ ᱠᱟᱛᱮ ᱵᱤᱯᱚᱫ ᱡᱟᱭᱜᱟ ᱫᱮ ᱠᱟᱹᱢᱤ ᱠᱚ ᱫᱩᱦᱲᱟ ᱪᱮᱫ ᱞᱟᱹᱜᱤᱫ ᱵᱟᱝ ᱥᱮᱫ ᱠᱚᱣᱟ?",
            "ᱡᱤᱱᱤᱥ ᱫᱚ ᱟᱞᱜᱟ ᱠᱟᱱᱟ",
            "ᱫᱩᱦᱲᱟ ᱥᱮᱫ ᱠᱷᱟᱱ ᱵᱤᱯᱚᱫ ᱫᱟᱹᱨᱟᱭ ᱢᱮ",
            "ᱡᱚᱢᱟᱣ ᱡᱟᱭᱜᱟ ᱵᱟᱝ ᱡᱟᱹᱨᱩᱨᱤ",
            "ᱟᱞᱟᱨᱢ ᱥᱟᱹᱫᱷᱟᱹᱨᱚᱱ ᱠᱟᱱᱟ"
        ),

        "Which information is site-specific and must be learned from the workplace emergency plan?": (
            "ᱚᱠᱟ ᱵᱟᱵᱚᱫ ᱡᱟᱭᱜᱟ ᱠᱷᱟᱹᱴᱤ ᱥᱟᱱᱛᱟᱹ ᱟᱨ ᱵᱤᱯᱚᱫ ᱯᱚᱨᱤᱠᱟᱞᱯᱚᱱᱟ ᱠᱷᱚᱱ ᱥᱤᱠᱷᱟᱹᱣ ᱞᱟᱹᱜᱤᱫ ᱡᱟᱹᱨᱩᱨᱤ?",
            "ᱯᱟᱞᱟᱣ ᱨᱚᱥᱛᱟ ᱟᱨ ᱡᱚᱢᱟᱣ ᱵᱮᱵᱥᱛᱟ",
            "ᱵᱤᱯᱚᱫ ᱦᱚᱭᱚᱜ",
            "ᱯᱟᱞᱟᱣ ᱥᱟᱵᱫᱚᱨ ᱨᱮᱭᱟᱜ ᱢᱮᱱ",
            "ᱥᱩᱨᱚᱠᱷᱟ ᱞᱟᱹᱜᱤᱫ ᱜᱚᱱᱚᱝ"
        ),

        "After reaching the designated safe area, what should the worker do?": (
            "ᱥᱟᱯᱷᱟᱹᱭ ᱡᱟᱭᱜᱟ ᱫᱮ ᱯᱷᱟᱸᱥ ᱠᱟᱛᱮ ᱠᱟᱹᱢᱤ ᱦᱚᱲ ᱪᱮᱫ ᱠᱟᱹᱢᱤ ᱢᱮ?",
            "ᱛᱟᱹᱲᱟᱜ ᱨᱩᱦᱟᱹᱲ ᱢᱮ",
            "ᱢᱚᱱᱡᱩᱨ ᱟᱫᱮᱥ ᱠᱟᱹᱜᱮ ᱦᱟᱹᱛᱤᱝ ᱢᱮ",
            "ᱱᱤᱡᱟᱜ ᱨᱚᱥᱛᱟ ᱵᱟᱪᱷᱟᱣ ᱢᱮ",
            "ᱵᱟᱝ ᱥᱚᱫᱚᱨ ᱠᱟᱛᱮ ᱪᱟᱞᱟᱣ ᱢᱮ"
        ),

        "What is a useful prevention practice for fire hazards?": (
            "ᱥᱮᱫ ᱵᱤᱯᱚᱫ ᱯᱨᱟᱛᱤᱨᱚᱫᱷ ᱞᱟᱹᱜᱤᱫ ᱪᱮᱫ ᱜᱚᱲᱚ ᱠᱟᱱᱟ?",
            "ᱠᱷᱟᱨᱟᱯ ᱥᱟᱢᱟᱱ ᱵᱟᱝ ᱧᱮᱞ ᱢᱮ",
            "ᱵᱟᱝ ᱥᱟᱹᱯᱷᱟᱹᱭ ᱠᱟᱹᱢᱤ ᱨᱤᱯᱚᱨᱴ ᱢᱮ",
            "ᱡᱟᱦᱟᱸ ᱛᱟᱭᱚᱢ ᱡᱟᱹᱞᱟᱣ ᱡᱤᱱᱤᱥ ᱫᱟᱵᱚᱞ ᱢᱮ",
            "ᱥᱟᱹᱱᱫᱮᱥ ᱥᱤᱥᱴᱮᱢ ᱵᱚᱸᱫ ᱢᱮ"
        ),

        "What should the simulator's evacuation drill primarily assess?": (
            "ᱥᱤᱢᱩᱞᱮᱴᱚᱨ ᱯᱟᱞᱟᱣ ᱰᱨᱤᱞ ᱫᱚ ᱢᱩᱞ ᱛᱮ ᱪᱮᱫ ᱵᱩᱡᱷᱟᱹᱣ ᱢᱮ?",
            "ᱵᱟᱝ ᱥᱤᱠᱷᱟᱹᱣ ᱵᱤᱯᱚᱫ ᱢᱮᱥᱤᱱ ᱛᱷᱤᱨ ᱠᱟᱹᱢᱤ",
            "ᱟᱞᱟᱨᱢ ᱵᱩᱡᱷᱟᱹᱣ ᱟᱨ ᱥᱟᱯᱷᱟᱹᱭ ᱯᱟᱞᱟᱣ ᱨᱚᱥᱛᱟ ᱵᱟᱪᱷᱟᱣ",
            "ᱟᱞᱟᱨᱢ ᱵᱟᱝ ᱜᱚᱱᱚᱝ",
            "ᱵᱤᱯᱚᱫ ᱡᱟᱭᱜᱟ ᱫᱮ ᱫᱩᱦᱲᱟ ᱥᱮᱫ"
        ),

        "Why is ventilation important in underground workings?": (
            "ᱡᱚᱢᱤᱱ ᱛᱟᱞᱟ ᱠᱟᱹᱢᱤ ᱨᱮ ᱵᱮᱞᱮᱱᱴᱤᱞᱮᱥᱚᱱ ᱪᱮᱫ ᱞᱟᱹᱜᱤᱫ ᱡᱟᱹᱨᱩᱨᱤ?",
            "ᱠᱮᱵᱚᱞ ᱥᱩᱠᱷᱟᱹ ᱞᱟᱹᱜᱤᱫ",
            "ᱥᱩᱨᱚᱠᱷᱤᱛ ᱵᱟᱭᱩ ᱛᱟᱦᱟᱸ ᱟᱨ ᱵᱤᱯᱚᱫ ᱠᱚ ᱠᱚᱱᱴᱨᱚᱞ ᱞᱟᱹᱜᱤᱫ",
            "ᱜᱮᱥ ᱢᱚᱱᱤᱴᱚᱨᱤᱝ ᱵᱚᱫᱚᱞ ᱞᱟᱹᱜᱤᱫ",
            "ᱵᱤᱯᱚᱫ ᱛᱟᱭᱚᱢ ᱠᱮᱵᱚᱞ"
        ),

        "What should a worker do after an atmospheric warning or abnormal reading?": (
            "ᱵᱟᱭᱩ ᱵᱟᱵᱚᱫ ᱟᱞᱟᱨᱢ ᱥᱮ ᱵᱟᱝ ᱥᱟᱢᱟᱱᱭ ᱨᱤᱰᱤᱝ ᱧᱟᱢ ᱠᱷᱟᱱ ᱠᱟᱹᱢᱤ ᱦᱚᱲ ᱪᱮᱫ ᱢᱮ?",
            "ᱛᱮᱭᱟᱨ ᱵᱟᱝ ᱜᱚᱱᱚᱝ ᱢᱮ",
            "ᱡᱟᱭᱜᱟᱭᱟᱜ ᱢᱚᱱᱡᱩᱨ ᱯᱨᱚᱛᱤᱠᱨᱤᱭᱟ ᱱᱤᱭᱚᱢ ᱢᱟᱱᱟᱣ ᱢᱮ",
            "ᱵᱤᱯᱚᱫ ᱡᱟᱭᱜᱟ ᱛᱟᱞᱟ ᱫᱮ ᱪᱟᱞᱟᱣ ᱢᱮ",
            "ᱥᱟᱹᱱᱫᱮᱥ ᱥᱤᱥᱴᱮᱢ ᱵᱚᱸᱫ ᱢᱮ"
        ),

        "Who should perform technical ventilation interventions?": (
            "ᱴᱮᱠᱱᱤᱠᱟᱞ ᱵᱮᱞᱮᱱᱴᱤᱞᱮᱥᱚᱱ ᱠᱟᱹᱢᱤ ᱚᱠᱚ ᱠᱟᱹᱢᱤ ᱢᱮ?",
            "ᱡᱟᱦᱟᱸ ᱠᱟᱹᱢᱤ ᱦᱚᱲ",
            "ᱥᱤᱠᱷᱟᱹᱣ ᱟᱨ ᱢᱚᱱᱡᱩᱨ ᱠᱟᱹᱢᱤ ᱦᱚᱲ",
            "ᱧᱮᱞᱚᱜ ᱠᱚ",
            "ᱚᱠᱚ ᱵᱟᱝ"
        ),

        "Why should ventilation controls not be disturbed without authorization?": (
            "ᱢᱚᱱᱡᱩᱨ ᱟᱫᱮᱥ ᱵᱟᱝ ᱛᱟᱦᱟᱸ ᱵᱮᱞᱮᱱᱴᱤᱞᱮᱥᱚᱱ ᱠᱚᱱᱴᱨᱚᱞ ᱪᱮᱫ ᱞᱟᱹᱜᱤᱫ ᱵᱟᱝ ᱵᱚᱫᱞᱟᱣ ᱢᱮ?",
            "ᱵᱮᱞᱮᱱᱴᱤᱞᱮᱥᱚᱱ ᱵᱚᱫᱞᱟᱣ ᱫᱚ ᱵᱟᱭᱩ ᱟᱨ ᱥᱩᱨᱚᱠᱷᱟ ᱫᱮ ᱟᱥᱚᱞ ᱯᱟᱹᱞᱟᱣ ᱫᱟᱲᱮ",
            "ᱵᱮᱞᱮᱱᱴᱤᱞᱮᱥᱚᱱ ᱨᱮ ᱥᱩᱨᱚᱠᱷᱟ ᱵᱟᱝ",
            "ᱠᱮᱵᱚᱞ ᱞᱟᱹᱭᱤᱴ ᱵᱚᱫᱞᱟᱣ",
            "ᱡᱤᱱᱤᱥ ᱠᱚ ᱵᱚᱫᱞᱟᱣ"
        ),

        "Can a hazardous atmosphere always be identified visually?": (
            "ᱵᱤᱯᱚᱫᱡᱚᱱᱟ ᱵᱟᱭᱩ ᱫᱚ ᱥᱟᱹᱞᱟᱜ ᱛᱮ ᱧᱮᱞ ᱛᱮ ᱥᱟᱢᱵᱷᱟᱵᱱᱟ ᱵᱩᱡᱷᱟᱹᱣ ᱥᱟᱢᱵᱷᱟᱵᱱᱟ ᱢᱮᱱᱟᱜᱼᱟ?",
            "ᱦᱚᱭᱚᱜᱼᱟ",
            "ᱵᱟᱝ, ᱧᱮᱞ ᱛᱮ ᱠᱮᱵᱚᱞ ᱥᱩᱨᱚᱠᱷᱟ ᱵᱟᱝ ᱵᱩᱡᱷᱟᱹᱣ ᱥᱟᱢᱵᱷᱟᱵᱱᱟ",
            "ᱠᱮᱵᱚᱞ ᱫᱤᱱ ᱨᱮ",
            "ᱠᱮᱵᱚᱞ ᱢᱮᱥᱤᱱ ᱪᱟᱞᱟᱣ ᱠᱷᱟᱱ"
        ),

        "What should happen when a worker is instructed to leave an unsafe tunnel area?": (
            "ᱵᱟᱝ ᱥᱩᱨᱚᱠᱷᱤᱛ ᱛᱩᱱᱮᱞ ᱡᱟᱭᱜᱟ ᱵᱟᱝ ᱪᱟᱞᱟᱣ ᱞᱟᱹᱜᱤᱫ ᱟᱫᱮᱥ ᱧᱟᱢ ᱠᱷᱟᱱ ᱪᱮᱫ ᱢᱮ?",
            "ᱟᱞᱟᱨᱢ ᱡᱷᱟᱹᱞ ᱵᱟᱝ ᱞᱮ ᱛᱟᱦᱟᱸ",
            "ᱢᱚᱱᱡᱩᱨ ᱯᱟᱞᱟᱣ ᱥᱮ ᱥᱟᱯᱷᱟᱹᱭ ᱪᱟᱞᱟᱣ ᱱᱤᱭᱚᱢ ᱢᱟᱱᱟᱣ ᱢᱮ",
            "ᱮᱴᱟᱜ ᱵᱤᱯᱚᱫ ᱡᱟᱭᱜᱟ ᱫᱮ ᱧᱮᱞ ᱢᱮ",
            "ᱟᱫᱮᱥ ᱵᱟᱝ ᱢᱟᱱᱟᱣ ᱢᱮ"
        ),

        "Why is communication important during a tunnel emergency?": (
            "ᱛᱩᱱᱮᱞ ᱵᱤᱯᱚᱫ ᱨᱮ ᱥᱚᱫᱚᱨ ᱪᱮᱫ ᱞᱟᱹᱜᱤᱫ ᱡᱟᱹᱨᱩᱨᱤ?",
            "ᱵᱤᱯᱚᱫ ᱵᱟᱵᱚᱫ ᱥᱟᱹᱱᱫᱮᱥ ᱢᱚᱱᱡᱩᱨ ᱯᱨᱚᱛᱤᱠᱨᱤᱭᱟ ᱫᱮ ᱯᱷᱚᱨᱚᱢ ᱮᱢ ᱫᱟᱲᱮ",
            "ᱯᱟᱞᱟᱣ ᱵᱟᱝ ᱡᱟᱹᱨᱩᱨᱤ",
            "ᱵᱤᱯᱚᱫ ᱪᱟᱵᱟ ᱞᱮᱱᱟ",
            "ᱵᱤᱯᱚᱫ ᱱᱤᱭᱚᱢ ᱡᱟᱹᱨᱩᱨᱤ ᱵᱟᱝ"
        ),

        "What is the main learning objective of the tunnel AR drill?": (
            "ᱛᱩᱱᱮᱞ AR ᱰᱨᱤᱞ ᱨᱮ ᱢᱩᱞ ᱥᱤᱠᱷᱟᱹᱣ ᱠᱟᱹᱢᱤ ᱪᱮᱫ ᱠᱟᱱᱟ?",
            "ᱥᱤᱢᱩᱞᱮᱴᱚᱨ ᱛᱩᱱᱮᱞ ᱵᱤᱯᱚᱫ ᱵᱟᱵᱚᱫ ᱥᱩᱨᱚᱠᱷᱟ ᱯᱟᱹᱞᱟᱣ ᱥᱤᱱᱤᱭᱟᱹᱨ ᱢᱮ",
            "ᱵᱟᱝ ᱥᱤᱠᱷᱟᱹᱣ ᱢᱮᱥᱤᱱ ᱛᱷᱤᱨ",
            "ᱵᱤᱯᱚᱫ ᱡᱟᱭᱜᱟ ᱫᱮ ᱥᱮᱫ",
            "ᱟᱞᱟᱨᱢ ᱵᱚᱸᱫ"
        ),
    }

    for question, values in drill.items():
        upsert_question(db, question, values, DrillQuestion)


    # =========================================================
    # MODULE ASSESSMENT QUESTIONS
    # =========================================================

    module = {

        "What is the primary purpose of an emergency evacuation procedure?": (
            "ᱵᱤᱯᱚᱫ ᱯᱟᱞᱟᱣ ᱯᱚᱨᱤᱠᱟᱞᱯᱚᱱᱟ ᱨᱮ ᱢᱩᱞ ᱩᱫᱮᱥ ᱪᱮᱫ ᱠᱟᱱᱟ?",
            "ᱦᱚᱲ ᱠᱚ ᱥᱩᱨᱚᱠᱷᱤᱛ ᱡᱟᱭᱜᱟ ᱫᱮ ᱪᱟᱞᱟᱣ ᱠᱟᱛᱮ ᱥᱩᱨᱚᱠᱷᱟ ᱮᱢ",
            "ᱯᱨᱚᱰᱟᱠᱥᱚᱱ ᱡᱚᱛᱚ ᱞᱮᱠᱟ ᱪᱟᱞᱟᱣ",
            "ᱥᱟᱢᱟᱱ ᱦᱟᱛᱟᱣ ᱠᱟᱛᱮ ᱯᱟᱞᱟᱣ",
            "ᱡᱚᱛᱚ ᱵᱤᱯᱚᱫ ᱧᱮᱞ ᱡᱚᱠᱷᱚᱱ ᱛᱟᱦᱟᱸ"
        ),

        "Which source should determine the exact evacuation route at a workplace?": (
            "ᱠᱟᱹᱢᱤ ᱡᱟᱭᱜᱟ ᱨᱮ ᱥᱟᱹᱠᱷᱟᱛ ᱯᱟᱞᱟᱣ ᱨᱚᱥᱛᱟ ᱚᱠᱟ ᱥᱚᱨᱥ ᱫᱮ ᱩᱫᱩᱜ ᱠᱟᱱᱟ?",
            "ᱡᱟᱭᱜᱟᱭᱟᱜ ᱵᱚᱛᱚᱨᱢᱟᱱ ᱵᱤᱯᱚᱫ ᱯᱚᱨᱤᱠᱟᱞᱯᱚᱱᱟ ᱟᱨ ᱨᱚᱥᱛᱟ ᱪᱤᱱᱦᱟᱹ",
            "ᱵᱤᱯᱚᱫ ᱵᱮᱞᱟ ᱨᱮ ᱡᱮ ᱠᱚᱱᱟ ᱨᱚᱥᱛᱟ",
            "ᱮᱴᱟᱜ ᱡᱟᱭᱜᱟᱭᱟᱜ ᱡᱩᱨᱟᱹ ᱨᱚᱥᱛᱟ",
            "ᱥᱩᱵᱤᱫᱷᱟ ᱞᱟᱹᱜᱤᱫ ᱵᱟᱪᱷᱟᱣ ᱨᱚᱥᱛᱟ"
        ),

        "What should happen after reaching the designated assembly area?": (
            "ᱢᱚᱱᱡᱩᱨ ᱡᱚᱢᱟᱣ ᱡᱟᱭᱜᱟ ᱫᱮ ᱯᱷᱟᱸᱥ ᱠᱟᱛᱮ ᱪᱮᱫ ᱦᱚᱭᱚᱜ ᱢᱮ?",
            "ᱚᱱᱟ ᱨᱮ ᱛᱟᱦᱟᱸ ᱟᱨ ᱢᱚᱱᱡᱩᱨ ᱟᱫᱮᱥ ᱢᱟᱱᱟᱣ",
            "ᱛᱷᱩᱱᱤᱞ ᱨᱮ ᱨᱩᱦᱟᱹᱲ",
            "ᱥᱟᱢᱟᱱ ᱧᱮᱞ ᱞᱟᱹᱜᱤᱫ ᱫᱩᱦᱲᱟ ᱥᱮᱫ",
            "ᱵᱟᱝ ᱥᱩᱨᱚᱠᱷᱤᱛ ᱡᱟᱭᱜᱟ ᱫᱮ ᱪᱟᱞᱟᱣ"
        ),

        "Why is reporting unsafe fire-related conditions important?": (
            "ᱵᱟᱝ ᱥᱩᱨᱚᱠᱷᱤᱛ ᱥᱮᱫ ᱵᱟᱵᱚᱫ ᱯᱚᱨᱤᱥᱛᱤᱛᱤ ᱨᱤᱯᱚᱨᱴ ᱪᱮᱫ ᱞᱟᱹᱜᱤᱫ ᱡᱟᱹᱨᱩᱨᱤ?",
            "ᱵᱤᱯᱚᱫ ᱠᱚ ᱥᱩᱨᱚᱠᱷᱟ ᱱᱤᱭᱚᱢ ᱛᱮ ᱥᱟᱢᱟᱫᱷᱟᱱ ᱦᱚᱭᱚᱜ ᱫᱟᱲᱮ",
            "ᱵᱤᱯᱚᱫ ᱠᱟᱹᱞ ᱛᱟᱦᱟᱸ ᱵᱟᱝ",
            "ᱥᱩᱨᱚᱠᱷᱟ ᱥᱤᱠᱷᱟᱹᱣ ᱵᱚᱫᱚᱞ",
            "ᱧᱮᱞ ᱡᱟᱹᱛᱤ ᱵᱚᱫᱚᱞ"
        ),

        "What should a worker do if an emergency response action is outside their training?": (
            "ᱵᱤᱯᱚᱫ ᱯᱨᱚᱛᱤᱠᱨᱤᱭᱟ ᱱᱤᱡᱟᱜ ᱥᱤᱠᱷᱟᱹᱣ ᱵᱟᱦᱨᱮ ᱦᱚᱭᱚᱜ ᱠᱷᱟᱱ ᱪᱮᱫ ᱢᱮ?",
            "ᱢᱚᱱᱡᱩᱨ ᱱᱤᱭᱚᱢ ᱢᱟᱱᱟᱣ ᱟᱨ ᱟᱹᱲᱤ ᱥᱟᱦᱟᱭ ᱧᱟᱢ",
            "ᱱᱟᱣᱟ ᱴᱮᱠᱱᱤᱠ ᱯᱚᱨᱤᱠᱥᱟ",
            "ᱥᱟᱫᱷᱟᱨᱚᱱ ᱠᱟᱹᱢᱤ ᱪᱟᱞᱟᱣ",
            "ᱵᱤᱯᱚᱫ ᱞᱩᱠᱟᱹᱣ"
        ),

        "Which behavior is inappropriate after evacuation?": (
            "ᱯᱟᱞᱟᱣ ᱛᱟᱭᱚᱢ ᱚᱠᱟ ᱠᱟᱹᱢᱤ ᱵᱟᱝ ᱡᱩᱛᱟᱹᱣ ᱠᱟᱱᱟ?",
            "ᱢᱚᱱᱡᱩᱨ ᱟᱫᱮᱥ ᱵᱟᱝ ᱛᱟᱦᱟᱸ ᱵᱤᱯᱚᱫ ᱡᱟᱭᱜᱟ ᱫᱮ ᱫᱩᱦᱲᱟ ᱥᱮᱫ",
            "ᱥᱟᱯᱷᱟᱹᱭ ᱡᱟᱭᱜᱟ ᱨᱮ ᱛᱟᱦᱟᱸ",
            "ᱵᱤᱯᱚᱫ ᱯᱚᱨᱤᱠᱟᱞᱯᱚᱱᱟ ᱢᱟᱱᱟᱣ",
            "ᱵᱟᱹᱲᱤ ᱟᱫᱮᱥ ᱟᱹᱭᱫᱟᱹ"
        ),

        "Why are site-specific emergency instructions important?": (
            "ᱡᱟᱭᱜᱟ ᱠᱷᱟᱹᱴᱤ ᱵᱤᱯᱚᱫ ᱟᱫᱮᱥ ᱪᱮᱫ ᱞᱟᱹᱜᱤᱫ ᱡᱟᱹᱨᱩᱨᱤ?",
            "ᱯᱟᱞᱟᱣ ᱨᱚᱥᱛᱟ ᱟᱨ ᱵᱤᱯᱚᱫ ᱵᱮᱵᱥᱛᱟ ᱡᱟᱭᱜᱟ ᱞᱮᱠᱟ ᱵᱚᱫᱞᱟᱣ ᱠᱟᱱᱟ",
            "ᱡᱚᱛᱚ ᱢᱟᱭᱤᱱ ᱨᱮ ᱢᱤᱫ ᱞᱮᱠᱟ ᱠᱚᱱᱰᱤᱥᱚᱱ",
            "ᱠᱮᱵᱚᱞ ᱧᱮᱞᱚᱜ ᱠᱚ ᱞᱟᱹᱜᱤᱫ",
            "ᱥᱩᱨᱚᱠᱷᱟ ᱥᱟᱢᱟᱱ ᱵᱚᱫᱚᱞ"
        ),

        "What does the AR evacuation assessment measure?": (
            "AR ᱯᱟᱞᱟᱣ ᱯᱚᱨᱤᱠᱷᱟ ᱪᱮᱫ ᱵᱩᱡᱷᱟᱹᱣ ᱢᱮ?",
            "ᱟᱞᱟᱨᱢ ᱵᱩᱡᱷᱟᱹᱣ ᱟᱨ ᱥᱟᱯᱷᱟᱹᱭ ᱯᱨᱚᱛᱤᱠᱨᱤᱭᱟ ᱵᱟᱪᱷᱟᱣ",
            "ᱡᱚᱨ ᱛᱮ ᱥᱟᱹᱵ",
            "ᱯᱨᱚᱰᱟᱠᱥᱚᱱ ᱥᱟᱹᱢᱟᱱ",
            "ᱵᱟᱝ ᱧᱮᱞ ᱢᱮᱥᱤᱱ ᱪᱟᱞᱟᱣ"
        ),

        "Why is ventilation a key underground safety control?": (
            "ᱵᱮᱞᱮᱱᱴᱤᱞᱮᱥᱚᱱ ᱡᱚᱢᱤᱱ ᱛᱟᱞᱟ ᱥᱩᱨᱚᱠᱷᱟ ᱞᱟᱹᱜᱤᱫ ᱢᱩᱞ ᱠᱚᱱᱴᱨᱚᱞ ᱪᱮᱫ ᱞᱟᱹᱜᱤᱫ?",
            "ᱥᱩᱨᱚᱠᱷᱤᱛ ᱵᱟᱭᱩ ᱛᱟᱦᱟᱸ ᱫᱟᱲᱮ",
            "ᱠᱮᱵᱚᱞ ᱥᱩᱱᱫᱚᱨ",
            "ᱥᱚᱡᱷᱮ ᱥᱤᱠᱷᱟᱹᱣ ᱵᱚᱫᱚᱞ",
            "ᱵᱤᱯᱚᱫ ᱛᱟᱭᱚᱢ ᱠᱮᱵᱚᱞ"
        ),

        "What should a worker do after a gas or atmospheric warning?": (
            "ᱜᱮᱥ ᱥᱮ ᱵᱟᱭᱩ ᱟᱞᱟᱨᱢ ᱠᱷᱟᱱ ᱠᱟᱹᱢᱤ ᱦᱚᱲ ᱪᱮᱫ ᱢᱮ?",
            "ᱡᱟᱭᱜᱟᱭᱟᱜ ᱢᱚᱱᱡᱩᱨ ᱯᱨᱚᱛᱤᱠᱨᱤᱭᱟ ᱱᱤᱭᱚᱢ ᱢᱟᱱᱟᱣ ᱢᱮ",
            "ᱛᱩᱱᱮᱞ ᱨᱮ ᱛᱟᱦᱟᱸ",
            "ᱟᱞᱟᱨᱢ ᱵᱚᱸᱫ ᱢᱮ",
            "ᱟᱜᱟᱲ ᱛᱮ ᱪᱟᱞᱟᱣ ᱢᱮ"
        ),

        "Who should make technical changes to ventilation controls?": (
            "ᱵᱮᱞᱮᱱᱴᱤᱞᱮᱥᱚᱱ ᱠᱚᱱᱴᱨᱚᱞ ᱨᱮ ᱴᱮᱠᱱᱤᱠᱟᱞ ᱵᱚᱫᱞᱟᱣ ᱚᱠᱚ ᱠᱟᱹᱢᱤ ᱢᱮ?",
            "ᱥᱤᱠᱷᱟᱹᱣ ᱟᱨ ᱢᱚᱱᱡᱩᱨ ᱠᱟᱹᱢᱤ ᱦᱚᱲ",
            "ᱡᱟᱦᱟᱸ ᱠᱟᱹᱢᱤ ᱦᱚᱲ",
            "ᱧᱮᱞᱚᱜ ᱠᱚ",
            "ᱵᱟᱝ ᱥᱤᱠᱷᱟᱹᱣ ᱠᱟᱹᱢᱤ ᱦᱚᱲ"
        ),

        "Why can visual inspection alone be insufficient for atmospheric safety?": (
            "ᱵᱟᱭᱩ ᱥᱩᱨᱚᱠᱷᱟ ᱞᱟᱹᱜᱤᱫ ᱠᱮᱵᱚᱞ ᱧᱮᱞ ᱛᱮ ᱪᱮᱫ ᱵᱟᱝ ᱯᱩᱨᱟᱹ ᱠᱟᱱᱟ?",
            "ᱪᱮᱫ ᱵᱤᱯᱚᱫᱡᱚᱱᱟ ᱵᱟᱭᱩ ᱧᱮᱞ ᱛᱮ ᱥᱟᱹᱠᱷᱟᱛ ᱵᱩᱡᱷᱟᱹᱣ ᱵᱟᱝ ᱦᱚᱭᱚᱜ ᱫᱟᱲᱮ",
            "ᱡᱚᱛᱚ ᱜᱮᱥ ᱵᱟᱝ ᱧᱮᱞᱚᱜ",
            "ᱛᱩᱱᱮᱞ ᱨᱮ ᱞᱟᱹᱭᱤᱴ ᱵᱟᱝ",
            "ᱧᱮᱞ ᱵᱟᱝ ᱟᱹᱲᱤ"
        ),

        "What is an appropriate response to an unsafe-area instruction?": (
            "ᱵᱟᱝ ᱥᱩᱨᱚᱠᱷᱤᱛ ᱡᱟᱭᱜᱟ ᱠᱷᱚᱱ ᱪᱟᱞᱟᱣ ᱟᱫᱮᱥ ᱧᱟᱢ ᱠᱷᱟᱱ ᱪᱮᱫ ᱢᱮ?",
            "ᱢᱚᱱᱡᱩᱨ ᱥᱟᱯᱷᱟᱹᱭ ᱪᱟᱞᱟᱣ ᱥᱮ ᱯᱟᱞᱟᱣ ᱱᱤᱭᱚᱢ ᱢᱟᱱᱟᱣ",
            "ᱡᱟᱭᱜᱟ ᱨᱮ ᱛᱟᱦᱟᱸ",
            "ᱵᱟᱝ ᱟᱫᱮᱥ ᱮᱴᱟᱜ ᱨᱚᱥᱛᱟ ᱧᱮᱞ",
            "ᱟᱫᱮᱥ ᱵᱟᱝ ᱢᱟᱱᱟᱣ"
        ),

        "Why should ventilation arrangements be maintained properly?": (
            "ᱵᱮᱞᱮᱱᱴᱤᱞᱮᱥᱚᱱ ᱵᱮᱵᱥᱛᱟ ᱥᱟᱹᱯᱷᱟᱹ ᱛᱮ ᱪᱮᱫ ᱞᱟᱹᱜᱤᱫ ᱛᱟᱦᱟᱸ ᱢᱮ?",
            "ᱥᱩᱨᱚᱠᱷᱤᱛ ᱵᱟᱭᱩ ᱟᱨ ᱵᱤᱯᱚᱫ ᱯᱟᱞᱟᱣ ᱨᱮ ᱜᱚᱲᱚ",
            "ᱠᱮᱵᱚᱞ ᱢᱮᱥᱤᱱ ᱥᱮᱛᱟᱜ",
            "ᱥᱩᱨᱚᱠᱷᱟ ᱥᱟᱦᱟᱭ ᱵᱟᱝ",
            "ᱵᱤᱯᱚᱫ ᱥᱚᱫᱚᱨ ᱵᱚᱫᱚᱞ"
        ),

        "What role does communication play in an emergency?": (
            "ᱵᱤᱯᱚᱫ ᱨᱮ ᱥᱚᱫᱚᱨ ᱪᱮᱫ ᱠᱟᱹᱢᱤ ᱠᱟᱱᱟ?",
            "ᱢᱚᱱᱡᱩᱨ ᱨᱤᱯᱚᱨᱴ ᱟᱨ ᱯᱨᱚᱛᱤᱠᱨᱤᱭᱟ ᱨᱮ ᱜᱚᱲᱚ",
            "ᱯᱟᱞᱟᱣ ᱵᱚᱫᱚᱞ",
            "ᱵᱤᱯᱚᱫ ᱪᱟᱵᱟ ᱦᱚᱭᱚᱜ",
            "ᱟᱞᱟᱨᱢ ᱵᱟᱝ ᱡᱟᱹᱨᱩᱨᱤ"
        ),

        "What should the AR tunnel drill evaluate?": (
            "AR ᱛᱩᱱᱮᱞ ᱰᱨᱤᱞ ᱨᱮ ᱪᱮᱫ ᱯᱚᱨᱤᱠᱷᱟ ᱦᱚᱭᱚᱜ ᱢᱮ?",
            "ᱥᱤᱢᱩᱞᱮᱴᱚᱨ ᱛᱩᱱᱮᱞ ᱵᱤᱯᱚᱫ ᱵᱟᱵᱚᱫ ᱥᱩᱨᱚᱠᱷᱟ ᱥᱚᱪᱮᱛᱟᱱ ᱯᱨᱚᱛᱤᱠᱨᱤᱭᱟ",
            "ᱵᱟᱝ ᱥᱤᱠᱷᱟᱹᱣ ᱴᱮᱠᱱᱤᱠᱟᱞ ᱠᱟᱹᱢᱤ",
            "ᱵᱤᱯᱚᱫ ᱡᱟᱭᱜᱟ ᱫᱮ ᱥᱮᱫ ᱨᱮ ᱫᱷᱟᱹᱣ",
            "ᱥᱩᱨᱚᱠᱷᱟ ᱥᱤᱥᱴᱮᱢ ᱵᱚᱸᱫ"
        ),
    }

    for question, values in module.items():
        upsert_question(db, question, values, QuizQuestion)


    # =========================================================
    # SAVE
    # =========================================================

    db.commit()

    print()
    print("======================================")
    print("SANTALI PATCH COMPLETE")
    print("======================================")

    lesson_count = (
        db.query(LessonTranslation)
        .filter(LessonTranslation.language == LANG)
        .count()
    )

    drill_count = (
        db.query(DrillQuestionTranslation)
        .filter(DrillQuestionTranslation.language == LANG)
        .count()
    )

    module_count = (
        db.query(QuestionTranslation)
        .filter(QuestionTranslation.language == LANG)
        .count()
    )

    print("Santali lessons:", lesson_count)
    print("Santali module questions:", module_count)
    print("Santali drill questions:", drill_count)
    print()
    print("NOTE: These are prototype Santali translations.")
    print("======================================")

except Exception:
    db.rollback()
    raise

finally:
    db.close()
