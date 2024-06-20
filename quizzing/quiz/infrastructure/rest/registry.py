from dataclasses import dataclass

from quizzing.pkg.db.sqlalchemy import SQLATransactionManager
from quizzing.quiz.application.auth import AuthorService
from quizzing.quiz.application.quiz import QuizService
from quizzing.quiz.application.submission import SubmissionService
from quizzing.quiz.domain.registry import DomainRegistry
from quizzing.quiz.infrastructure.repository.sqlalchemy import config
from quizzing.quiz.infrastructure.repository.sqlalchemy.repository import (
    SQLAAuthorRepository,
    SQLAQuizRepository,
    SQLASubmissionRepository,
)


class RestRegistry:
    authors: AuthorService
    quizzes: QuizService
    submissions: SubmissionService

    @classmethod
    def initialize(cls) -> None:
        transaction_manager = SQLATransactionManager(config.get_engine())
        DomainRegistry.initialize(
            SQLAQuizRepository(transaction_manager),
            SQLASubmissionRepository(transaction_manager),
            SQLAAuthorRepository(transaction_manager),
        )
        cls.authors = AuthorService(transaction_manager)
        cls.quizzes = QuizService(transaction_manager)
        cls.submissions = SubmissionService(transaction_manager)
