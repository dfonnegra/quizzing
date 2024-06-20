from enum import Enum
from typing import TYPE_CHECKING
from uuid import uuid4

from ..exceptions import QuizValidationError, SubmissionValidationError
from .author import AuthorID

if TYPE_CHECKING:
    from .submission import Answer


class QuizID(str): ...


class QuizStatus(Enum):
    DRAFT = "draft"
    PUBLISHED = "published"


class Quiz:
    def __init__(
        self,
        id: QuizID,
        title: str,
        author_id: AuthorID,
        status: QuizStatus,
    ) -> None:
        self.id = id
        self.title = title
        self.questions: list[Question] = []
        self.status = status
        self.author_id = author_id

    @classmethod
    def new(
        cls,
        title: str,
        author_id: AuthorID,
    ):
        id_ = QuizID(str(uuid4()))
        return cls(id_, title, author_id, QuizStatus.DRAFT)

    def set_title(
        self,
        title: str,
    ):
        self.title = title

    def set_questions(
        self,
        questions: list["Question"],
    ):
        if len(questions) == 0:
            raise QuizValidationError(
                [f"Quiz {self.title} must have at least one question"]
            )
        if len(questions) > 10:
            raise QuizValidationError(
                [f"Quiz {self.title} can have at most 10 questions"]
            )
        if self.status != QuizStatus.DRAFT:
            raise QuizValidationError(
                [f"Quiz {self.title} can only be edited if it is in draft status"]
            )

        self.questions = questions

    def publish(self) -> None:
        self.status = QuizStatus.PUBLISHED

    def is_published(self) -> bool:
        return self.status == QuizStatus.PUBLISHED

    def validate_answers(self, answers: list["Answer"]):
        if len(answers) != len(self.questions):
            raise SubmissionValidationError(
                [
                    f"Quiz {self.title} has {len(self.questions)} questions, but {len(answers)} answers were submitted"
                ]
            )
        for question, answer in zip(self.questions, answers):
            if answer is None:
                continue
            question._validate_answer(answer)

    def score(self, answers: list["Answer"]) -> list["Answer"]:
        self.validate_answers(answers)
        scored_answers: list[Answer] = []
        for question, answer in zip(self.questions, answers):
            if answer is None:
                continue
            scored_answers.append(question._score(answer))
        return scored_answers


class AnswerOption(str): ...


class QuestionID(str): ...


class Question:
    def __init__(
        self,
        text: str,
        options: list[AnswerOption],
        correct_options: set[AnswerOption],
    ) -> None:
        errors = []
        if len(options) == 0:
            errors.append(f"Question '{text}' must have at least one option")
        if len(options) > 5:
            errors.append(f"Question '{text}' can have at most 5 options")
        if len(set(options)) != len(options):
            errors.append(f"Question '{text}' options must be unique")
        if len(correct_options) == 0:
            errors.append(f"Question '{text}' must have at least one correct option")
        if any(o not in options for o in correct_options):
            errors.append(
                f"All correct options for question '{text}' must be present in the options list"
            )
        if len(errors) > 0:
            raise QuizValidationError(errors)

        self.text = text
        self.options = options
        self.correct_options = correct_options

    def _is_single_choice(self) -> bool:
        return len(self.correct_options) == 1

    def _is_multiple_choice(self) -> bool:
        return len(self.correct_options) > 1

    def _validate_answer(self, answer: "Answer"):
        if answer.is_empty():
            return

        if answer.is_single() and self._is_single_choice():
            raise SubmissionValidationError(
                [f"Question '{self.text}' must have a single choice answer"]
            )

    def _score(self, answer: "Answer") -> Answer:
        if len(self.correct_options) == len(answer.options):
            wrong_question_weight = 0
        else:
            wrong_question_weight = 1 / (len(self.options) - len(self.correct_options))
        right_question_weight = 1 / len(self.correct_options)
        score = 0
        for option in answer.options:
            if option in self.correct_options:
                score += right_question_weight
            else:
                score -= wrong_question_weight
        return answer.with_score(score)