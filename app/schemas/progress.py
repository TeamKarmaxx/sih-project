from pydantic import BaseModel


class ProgressCreate(BaseModel):
    completed: bool