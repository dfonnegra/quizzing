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
from ..domain.entities.submission import Submission
from ..domain.exceptions import NotFound
from ..domain.registry import DomainRegistry


class QuizService(TransactionalServiceMixin):
    def __init__(self, transaction_manager: TransactionManager) -> None:
        self._transaction_manager = transaction_manager

    @transactional()
    def create(self, author: Author, title: str) -> Quiz:
        quiz = Quiz.new(title, author.id)
        DomainRegistry.quizzes.save(quiz)
        return DomainRegistry.quizzes.get(quiz.id)

    @transactional()
    def get(self, author: Author, quiz_id: str) -> Quiz:
        quiz = DomainRegistry.quizzes.get(quiz_id)
        if not quiz.is_published() and quiz.author_id != author.id:
            raise NotFound(f"Quiz {quiz_id} not found")
        if quiz.author_id != author.id:
            quiz.hide_correct_answers()
        return quiz

    @transactional()
    def list(self, author: Author, filter_: "QuizFilter") -> list[Quiz]:
        if filter_.status is None or filter_.status != QuizStatus.PUBLISHED:
            filter_.author_id = author.id
        quizzes = DomainRegistry.quizzes.list(filter_)
        for quiz in quizzes:
            if quiz.author_id != author.id:
                quiz.hide_correct_answers()
        return quizzes

    @transactional(IsolationLevel.SERIALIZABLE)
    def edit(
        self,
        author: Author,
        quiz_id: QuizID,
        title: str,
        questions: "list[Question]",
    ) -> Quiz:
        quiz = DomainRegistry.quizzes.get(quiz_id)
        if quiz.author_id != author.id:
            raise NotFound(f"Quiz {quiz_id} not found")
        quiz.set_title(title)
        quiz.set_questions(questions)
        DomainRegistry.quizzes.save(quiz)
        return quiz

    @transactional()
    def publish(self, author: Author, quiz_id: QuizID) -> Quiz:
        quiz = DomainRegistry.quizzes.get(quiz_id)
        if quiz.author_id != author.id:
            raise NotFound(f"Quiz {quiz_id} not found")
        quiz.publish()
        DomainRegistry.quizzes.save(quiz)
        return quiz

    @transactional()
    def submissions(
        self, author: Author, quiz_id: QuizID, page: int, page_size: int
    ) -> "list[Submission]":
        quiz = DomainRegistry.quizzes.get(quiz_id)
        if quiz.author_id != author.id:
            raise NotFound(f"Quiz {quiz_id} not found")
        return DomainRegistry.submissions.by_quiz(quiz_id, page, page_size)
