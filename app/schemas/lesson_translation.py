from pydantic import BaseModel


class LessonTranslationCreate(BaseModel):
    language: str
    title: str
    content: str | None = None