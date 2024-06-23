from enum import Enum
from uuid import uuid4

from ..exceptions import NotFound, SubmissionValidationError
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
        author_id: AuthorID,
        status: Status,
        answers: list["Answer"],
        score: float | None,
    ):
        self.id = id
        self.quiz_id = quiz_id
        self.author_id = author_id
        self.status = status
        self.answers = answers
        self.score = score

    @classmethod
    def start(cls, quiz_id: QuizID, author_id: AuthorID):
        quiz = DomainRegistry.quizzes.get(quiz_id)
        if not quiz.can_be_answered():
            raise NotFound(f"Quiz {quiz_id} not found")

        submissions = DomainRegistry.submissions.by_author(author_id)
        for submission in submissions:
            if submission.quiz_id == quiz_id:
                raise SubmissionValidationError(
                    [f"Author {author_id} already has a submission for quiz {quiz_id}"]
                )

        id_ = SubmissionID(str(uuid4()))
        answers = [Answer.empty()] * len(quiz.questions)
        return cls(id_, quiz_id, author_id, cls.Status.IN_PROGRESS, answers, None)

    def answer(self, answers: list[set["AnswerOption"]]):
        if self.status == self.Status.COMPLETED:
            raise SubmissionValidationError(
                [f"Submission {self.id} is already completed"]
            )

        quiz = DomainRegistry.quizzes.get(self.quiz_id)
        parsed_answers: list[Answer] = [Answer(answer) for answer in answers]
        quiz.validate_answers(parsed_answers)
        self.answers = parsed_answers

    def complete(self):
        if self.status == self.Status.COMPLETED:
            raise SubmissionValidationError(
                [f"Submission {self.id} is already completed"]
            )
        quiz = DomainRegistry.quizzes.get(self.quiz_id)
        self.status = self.Status.COMPLETED
        self.answers = quiz.score(self.answers)
        score = 0
        for answer in self.answers:
            assert answer.score is not None, "Answer must have a score"
            score = score + answer.score
        self.score = score


class Answer:
    def __init__(
        self,
        options: set["AnswerOption"],
        score: float | None = None,
    ):
        self.options = options
        self.score = score

    @classmethod
    def empty(cls):
        return cls(set())

    def is_empty(self):
        return len(self.options) == 0

    def is_single(self):
        return len(self.options) == 1

    def with_score(self, score: float):
        return Answer(self.options, score=score)
