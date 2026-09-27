from pydantic import BaseModel


class ModuleCreate(BaseModel):
    title: str
    description: str | None = None
    difficulty: str
    language: str