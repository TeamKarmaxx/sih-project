from pydantic import BaseModel


class QuizSubmission(BaseModel):
    answers: dict[int, str]