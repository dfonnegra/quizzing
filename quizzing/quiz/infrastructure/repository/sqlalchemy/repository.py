from typing import Sequence

from sqlalchemy import delete, insert, select, update
from sqlalchemy.engine.row import Row

from quizzing.pkg.db.sqlalchemy import SQLATransaction, SQLATransactionManager
from quizzing.quiz.domain.dto import QuizFilter
from quizzing.quiz.domain.entities.author import Author, AuthorID
from quizzing.quiz.domain.entities.quiz import (
    AnswerOption,
    Question,
    Quiz,
    QuizID,
    QuizStatus,
)
from quizzing.quiz.domain.entities.submission import Answer, Submission, SubmissionID
from quizzing.quiz.domain.exceptions import NotFound

from .models import (
    answer_table,
    author_table,
    question_table,
    quiz_table,
    submission_table,
)


class SQLAQuizRepository:
    def __init__(self, manager: SQLATransactionManager) -> None:
        self._manager = manager

    def transaction(self) -> SQLATransaction:
        return self._manager.transaction()

    def get(self, quiz_id: str) -> "Quiz":
        with self.transaction() as tx:
            stmt = select(quiz_table).where(quiz_table.c.id == quiz_id)
            quiz = tx.session.execute(stmt).one_or_none()
            if quiz is None:
                raise NotFound(f"Quiz {quiz_id} not found")
            quiz = self._quiz_from_row(quiz)
            stmt = select(question_table).where(question_table.c.quiz_id == quiz_id)
            questions = [
                self._question_from_row(r) for r in tx.session.execute(stmt).all()
            ]
            quiz.questions = questions
            return quiz

    def save(self, quiz: "Quiz") -> None:
        with self.transaction() as tx:
            stmts = []
            try:
                self.get(quiz.id)
                stmts.append(
                    update(quiz_table)
                    .where(quiz_table.c.id == quiz.id)
                    .values(
                        title=quiz.title,
                        author_id=quiz.author_id,
                        status=quiz.status.value,
                    )
                )
                stmts.append(
                    delete(question_table).where(question_table.c.quiz_id == quiz.id)
                )
            except NotFound:
                stmts.append(
                    insert(quiz_table).values(
                        id=quiz.id,
                        title=quiz.title,
                        author_id=quiz.author_id,
                        status=quiz.status.value,
                    )
                )
            for idx, question in enumerate(quiz.questions):
                stmt = insert(question_table).values(
                    quiz_id=quiz.id,
                    index=idx,
                    text=question.text,
                    options=[str(o) for o in question.options],
                    correct_options=[str(c) for c in question.correct_options],
                )
                stmts.append(stmt)
            for stmt in stmts:
                tx.session.execute(stmt)

    def list(self, filter_: QuizFilter) -> list["Quiz"]:
        with self.transaction() as tx:
            stmt = select(quiz_table)
            if filter_.status is not None:
                stmt = stmt.where(quiz_table.c.status == filter_.status.value)
            if filter_.author_id is not None:
                stmt = stmt.where(quiz_table.c.author_id == filter_.author_id)
            if filter_.page is not None and filter_.page_size is not None:
                stmt = stmt.offset((filter_.page - 1) * filter_.page_size).limit(
                    filter_.page_size
                )

            quizzes = [self._quiz_from_row(r) for r in tx.session.execute(stmt).all()]
            for quiz in quizzes:
                stmt = select(question_table).where(question_table.c.quiz_id == quiz.id)
                questions = tx.session.execute(stmt).all()
                quiz.questions = [
                    self._question_from_row(question) for question in questions
                ]
            return quizzes

    def _quiz_from_row(self, quiz: Row) -> "Quiz":
        quiz_entity = Quiz(
            id=QuizID(quiz.id),
            title=quiz.title,
            author_id=AuthorID(quiz.author_id),
            status=QuizStatus(quiz.status),
        )
        return quiz_entity

    def _question_from_row(self, question: Row) -> "Question":
        question_entity = Question(
            text=question.text,
            options=[AnswerOption(o) for o in question.options],
            correct_options={AnswerOption(c) for c in question.correct_options},
        )
        return question_entity


class SQLASubmissionRepository:
    def __init__(self, manager: SQLATransactionManager) -> None:
        self._manager = manager

    def transaction(self) -> SQLATransaction:
        return self._manager.transaction()

    def by_quiz(
        self, quiz_id: QuizID, page: int | None = None, page_size: int | None = None
    ) -> list["Submission"]:
        with self.transaction() as tx:
            stmt = select(submission_table).where(submission_table.c.quiz_id == quiz_id)
            if page is not None and page_size is not None:
                stmt = stmt.offset((page - 1) * page_size).limit(page_size)
            submissions = tx.session.execute(stmt).all()
            stmt = select(answer_table).where(
                answer_table.c.submission_id.in_([s.id for s in submissions])
            )
            answers = tx.session.execute(stmt).all()
            submission_id_to_answers: dict[str, list[Row]] = {}
            for row in answers:
                submission_id_to_answers.setdefault(row.submission_id, []).append(row)
            return [
                self._submission_from_row(
                    submission, submission_id_to_answers[submission.id]
                )
                for submission in submissions
            ]

    def by_author(self, author_id: AuthorID) -> list["Submission"]:
        with self.transaction() as tx:
            stmt = (
                select(answer_table)
                .join(
                    submission_table,
                    answer_table.c.submission_id == submission_table.c.id,
                )
                .where(submission_table.c.author_id == author_id)
            )
            answers = tx.session.execute(stmt).all()
            submission_id_to_answers: dict[str, list[Row]] = {}
            for row in answers:
                submission_id_to_answers.setdefault(row.submission_id, []).append(row)
            stmt = select(submission_table).where(
                submission_table.c.author_id == author_id
            )
            submissions = tx.session.execute(stmt).all()

            return [
                self._submission_from_row(s, submission_id_to_answers[s.id])
                for s in submissions
            ]

    def save(self, submission: "Submission") -> None:
        with self.transaction() as tx:
            stmts = []
            try:
                self.get(submission.id)
                stmts.append(
                    update(submission_table)
                    .where(submission_table.c.id == submission.id)
                    .values(
                        status=submission.status.value,
                        score=submission.score,
                    )
                )
                stmts.append(
                    delete(answer_table).where(
                        answer_table.c.submission_id == submission.id
                    )
                )
            except NotFound:
                stmts.append(
                    insert(submission_table).values(
                        id=submission.id,
                        quiz_id=submission.quiz_id,
                        author_id=submission.author_id,
                        status=submission.status.value,
                        score=submission.score,
                    )
                )
            for idx, answer in enumerate(submission.answers):
                stmt = insert(answer_table).values(
                    submission_id=submission.id,
                    index=idx,
                    options=[str(o) for o in answer.options],
                    score=answer.score,
                )
                stmts.append(stmt)
            for stmt in stmts:
                tx.session.execute(stmt)

    def get(self, submission_id: str) -> "Submission":
        with self.transaction() as tx:
            stmt = select(submission_table).where(
                submission_table.c.id == submission_id
            )
            submission = tx.session.execute(stmt).one_or_none()
            if submission is None:
                raise NotFound(f"Submission {submission_id} not found")
            stmt = select(answer_table).where(
                answer_table.c.submission_id == submission_id
            )
            answers = tx.session.execute(stmt).all()
            return self._submission_from_row(submission, answers)

    def _submission_from_row(
        self, submission: Row, answers: Sequence[Row]
    ) -> "Submission":
        submission_entity = Submission(
            id=SubmissionID(submission.id),
            quiz_id=QuizID(submission.quiz_id),
            author_id=AuthorID(submission.author_id),
            status=Submission.Status(submission.status),
            answers=[self._answer_from_row(a) for a in answers],
            score=submission.score,
        )
        return submission_entity

    def _answer_from_row(self, answer: Row) -> Answer:
        answer_entity = Answer(
            options={AnswerOption(o) for o in answer.options},
            score=answer.score,
        )
        return answer_entity


class SQLAAuthorRepository:
    def __init__(self, manager: SQLATransactionManager) -> None:
        self._manager = manager

    def transaction(self) -> SQLATransaction:
        return self._manager.transaction()

    def by_email(self, email: str) -> Author:
        with self.transaction() as tx:
            stmt = select(author_table).where(author_table.c.email == email)
            author = tx.session.execute(stmt).one_or_none()
            if author is None:
                raise NotFound(f"Author with email {email} not found")
            return self._author_from_row(author)

    def get(self, author_id: AuthorID) -> Author:
        with self.transaction() as tx:
            stmt = select(author_table).where(author_table.c.id == author_id)
            author = tx.session.execute(stmt).one_or_none()
            if author is None:
                raise NotFound(f"Author {author_id} not found")
            return self._author_from_row(author)

    def save(self, author: Author) -> None:
        with self.transaction() as tx:
            try:
                self.get(author.id)
                stmt = (
                    update(author_table)
                    .where(author_table.c.id == author.id)
                    .values(
                        email=author.email,
                        hashed_password=author.hashed_password,
                    )
                )
            except NotFound:
                stmt = insert(author_table).values(
                    id=author.id,
                    email=author.email,
                    hashed_password=author.hashed_password,
                )
                tx.session.execute(stmt)

    def _author_from_row(self, author: Row) -> Author:
        return Author(
            id=AuthorID(author.id),
            email=author.email,
            hashed_password=author.hashed_password,
        )
