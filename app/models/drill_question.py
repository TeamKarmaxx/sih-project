from sqlalchemy import Column, Integer, String, ForeignKey
from app.database.connection import Base


class DrillQuestion(Base):
    __tablename__ = "drill_questions"

    id = Column(Integer, primary_key=True, index=True)

    drill_id = Column(
        Integer,
        ForeignKey("training_drills.id"),
        nullable=False
    )

    question = Column(String, nullable=False)
    option_a = Column(String, nullable=False)
    option_b = Column(String, nullable=False)
    option_c = Column(String, nullable=False)
    option_d = Column(String, nullable=False)
    correct_answer = Column(String, nullable=False)