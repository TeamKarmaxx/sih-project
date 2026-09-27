from pydantic import BaseModel


class DrillQuestionTranslationCreate(BaseModel):
    language: str
    question: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str