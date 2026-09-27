from pydantic import BaseModel


class DrillProgressCreate(BaseModel):
    completed: bool