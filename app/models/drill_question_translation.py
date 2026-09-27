from sqlalchemy import Column, Integer, String, Text, ForeignKey
from app.database.connection import Base


class DrillQuestionTranslation(Base):
    __tablename__ = "drill_question_translations"

    id = Column(Integer, primary_key=True, index=True)

    question_id = Column(
        Integer,
        ForeignKey("drill_questions.id"),
        nullable=False
    )

    language = Column(String, nullable=False)

    question = Column(Text, nullable=False)
    option_a = Column(String, nullable=False)
    option_b = Column(String, nullable=False)
    option_c = Column(String, nullable=False)
    option_d = Column(String, nullable=False)