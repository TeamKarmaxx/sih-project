from pydantic import BaseModel


class DrillQuestionCreate(BaseModel):
    question: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_answer: str


class DrillQuestionPublic(BaseModel):
    id: int
    question: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str


class DrillQuizSubmission(BaseModel):
    answers: dict[int, str]