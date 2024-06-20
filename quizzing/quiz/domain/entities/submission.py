from enum import Enum
from uuid import uuid4

from ..exceptions import SubmissionValidationError
from ..registry import DomainRegistry
from .author import AuthorID
from .quiz import AnswerOption, QuizID


class SubmissionID(str):
    pass


class Submission:
    class Status(Enum):
        IN_PROGRESS = "in_progress"
        COMPLETED = "completed"

    def __init__(
        self,
        id: str,
        quiz_id: QuizID,
        user_id: AuthorID,
        status: Status,
    ):
        self._id = id
        self._quiz_id = quiz_id
        self._user_id = user_id
        self._status = status
        self._answers: list[Answer] = []
        self._score: float | None = None

    @classmethod
    def start(cls, quiz_id: QuizID, user_id: AuthorID):
        submissions = DomainRegistry.submissions.by_user(user_id)
        for submission in submissions:
            if submission._quiz_id == quiz_id:
                raise SubmissionValidationError(
                    [f"User {user_id} already has a submission for quiz {quiz_id}"]
                )

        id_ = SubmissionID(str(uuid4()))
        return cls(id_, quiz_id, user_id, cls.Status.IN_PROGRESS)

    def answer(self, answers: list[set["AnswerOption"]]):
        if self._status == self.Status.COMPLETED:
            raise SubmissionValidationError(
                [f"Submission {self._id} is already completed"]
            )
        quiz = DomainRegistry.quiz.get(self._quiz_id)

        parsed_answers: list[Answer] = [Answer(answer) for answer in answers]
        quiz.validate_answers(parsed_answers)
        self._answers = parsed_answers

    def complete(self):
        quiz = DomainRegistry.quiz.get(self._quiz_id)
        self._status = self.Status.COMPLETED
        self._answers = quiz.score(self._answers)
        score = 0
        for answer in self._answers:
            assert answer.score is not None, "Answer must have a score"
            score = score + answer.score
        self._score = score


class Answer:
    def __init__(
        self,
        options: set["AnswerOption"],
        score: float | None = None,
    ):
        self.options = options
        self.score = score

    def is_empty(self):
        return len(self.options) == 0

    def is_single(self):
        return len(self.options) == 1

    def with_score(self, score: float):
        return Answer(self.options, score=score)
