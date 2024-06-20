from dataclasses import dataclass

from pkg.db.sqlalchemy import SQLATransactionManager

from quizzing.quiz.application.auth import AuthorService
from quizzing.quiz.application.quiz import QuizService
from quizzing.quiz.domain.registry import DomainRegistry
from quizzing.quiz.infrastructure.repository.sqlalchemy import config


class RestRegistry:
    authors: AuthorService
    quizzes: QuizService

    @classmethod
    def initialize(cls) -> None:
        # TODO: DomainRegistry.initialize()
        transaction_manager = SQLATransactionManager(config.get_engine())
        cls.authors = AuthorService(transaction_manager)
        cls.quizzes = QuizService(transaction_manager)
