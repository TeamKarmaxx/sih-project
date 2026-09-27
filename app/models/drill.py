from sqlalchemy import Column, Integer, String, Text, ForeignKey
from app.database.connection import Base


class TrainingDrill(Base):
    __tablename__ = "training_drills"

    id = Column(Integer, primary_key=True, index=True)

    module_id = Column(
        Integer,
        ForeignKey("training_modules.id"),
        nullable=False
    )

    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    instructions = Column(Text, nullable=True)
    difficulty = Column(String, nullable=False)

    # AR / industrial safety information
    ar_scene = Column(String, nullable=True)
    equipment = Column(String, nullable=True)
    scenario = Column(Text, nullable=True)
    hazard_type = Column(String, nullable=True)
    safety_action = Column(Text, nullable=True)