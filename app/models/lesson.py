from sqlalchemy import Column, Integer, String, Text, ForeignKey
from app.database.connection import Base


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=True)
    module_id = Column(Integer, ForeignKey("training_modules.id"), nullable=False)