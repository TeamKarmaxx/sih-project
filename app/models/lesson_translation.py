from sqlalchemy import Column, Integer, String, Text, ForeignKey
from app.database.connection import Base


class LessonTranslation(Base):
    __tablename__ = "lesson_translations"

    id = Column(Integer, primary_key=True, index=True)

    lesson_id = Column(
        Integer,
        ForeignKey("lessons.id"),
        nullable=False
    )

    language = Column(String, nullable=False)

    title = Column(String, nullable=False)

    content = Column(Text, nullable=True)