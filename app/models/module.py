from sqlalchemy import Column, Integer, String, Text
from app.database.connection import Base


class TrainingModule(Base):
    __tablename__ = "training_modules"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    difficulty = Column(String, nullable=False)
    language = Column(String, nullable=False)