from dataclasses import dataclass

from quizzing.pkg.transactional import (
    IsolationLevel,
    TransactionalServiceMixin,
    TransactionManager,
    transactional,
)

from ..domain.dto import QuizFilter
from ..domain.entities.author import Author
from ..domain.entities.quiz import Question, Quiz, QuizID, QuizStatus
from ..domain.exceptions import NotFound
from ..domain.registry import DomainRegistry


class QuizService(TransactionalServiceMixin):
    def __init__(self, transaction_manager: TransactionManager) -> None:
        self._transaction_manager = transaction_manager

    @transactional()
    def create(self, author: Author, title: str) -> Quiz:
        quiz = Quiz.new(title, author.id)
        DomainRegistry.quiz.save(quiz)
        return DomainRegistry.quiz.get(quiz.id)

    @transactional()
    def get(self, author: Author, quiz_id: str) -> Quiz:
        quiz = DomainRegistry.quiz.get(quiz_id)
        if not quiz.is_published() and quiz.author_id != author.id:
            raise NotFound(f"Quiz {quiz_id} not found")
        return quiz

    @transactional()
    def list(self, author: Author, filter_: "QuizFilter") -> list[Quiz]:
        if filter_.status is None or filter_.status != QuizStatus.PUBLISHED:
            filter_.author_id = author.id
        return DomainRegistry.quiz.list(filter_)

    @transactional(IsolationLevel.SERIALIZABLE)
    def edit(
        self,
        quiz_id: QuizID,
        title: str,
        questions: "list[Question]",
    ) -> Quiz:
        quiz = DomainRegistry.quiz.get(quiz_id)
        quiz.set_title(title)
        quiz.set_questions(questions)
        DomainRegistry.quiz.save(quiz)
        return quiz
