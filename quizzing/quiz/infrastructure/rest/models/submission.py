from pydantic import BaseModel

from quizzing.quiz.domain.entities.submission import Answer, Submission


class SubmissionCreate(BaseModel):
    quiz_id: str


class SubmissionRead(BaseModel):
    id: str
    quiz_id: str
    author_id: str
    status: str
    answers: list["AnswerRead"]
    score: float | None

    @classmethod
    def from_entity(cls, submission: Submission) -> "SubmissionRead":
        return cls(
            id=submission.id,
            quiz_id=submission.quiz_id,
            author_id=submission.author_id,
            status=submission.status.value,
            answers=[
                AnswerRead(
                    options=[str(o) for o in answer.options],
                    score=answer.score,
                )
                for answer in submission.answers
            ],
            score=submission.score,
        )


class SubmissionAnswer(BaseModel):
    answers: list[list[str]]


class AnswerRead(BaseModel):
    options: list[str]
    score: float | None
