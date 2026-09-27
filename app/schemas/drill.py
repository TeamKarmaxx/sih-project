from pydantic import BaseModel


class TrainingDrillCreate(BaseModel):
    title: str
    description: str | None = None
    instructions: str | None = None
    difficulty: str

    ar_scene: str | None = None
    equipment: str | None = None
    scenario: str | None = None
    hazard_type: str | None = None
    safety_action: str | None = None