from typing import Protocol

from .dto import QuizFilter
from .entities.author import Author, AuthorID
from .entities.quiz import Quiz
from .entities.submission import Submission


class QuizRepository(Protocol):
    def get(self, quiz_id: str) -> "Quiz": ...
    def save(self, quiz: "Quiz") -> None: ...
    def list(self, filter_: QuizFilter) -> list["Quiz"]: ...


class SubmissionRepository(Protocol):
    def by_user(self, user_id: AuthorID) -> list["Submission"]: ...


class AuthorRepository(Protocol):
    def by_email(self, email: str) -> "Author": ...
    def save(self, author: "Author") -> None: ...
