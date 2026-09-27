from sqlalchemy import Column, Integer, Float, Boolean, ForeignKey
from app.database.connection import Base


class DrillQuizAttempt(Base):
    __tablename__ = "drill_quiz_attempts"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    drill_id = Column(
        Integer,
        ForeignKey("training_drills.id"),
        nullable=False
    )

    score = Column(Integer, nullable=False)
    total_questions = Column(Integer, nullable=False)
    percentage = Column(Float, nullable=False)
    passed = Column(Boolean, nullable=False)