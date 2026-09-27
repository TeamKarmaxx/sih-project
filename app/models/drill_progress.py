from sqlalchemy import Column, Integer, Boolean, ForeignKey
from app.database.connection import Base


class DrillProgress(Base):
    __tablename__ = "drill_progress"

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

    completed = Column(Boolean, default=False, nullable=False)