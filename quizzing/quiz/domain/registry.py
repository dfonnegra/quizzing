from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .ports import AuthorRepository, QuizRepository, SubmissionRepository


class DomainRegistry:
    quizzes: "QuizRepository"
    submissions: "SubmissionRepository"
    authors: "AuthorRepository"

    @classmethod
    def initialize(
        cls,
        quiz: "QuizRepository",
        submission: "SubmissionRepository",
        author: "AuthorRepository",
    ) -> None:
        cls.quizzes = quiz
        cls.submissions = submission
        cls.authors = author
