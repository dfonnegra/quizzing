from dataclasses import dataclass

from quizzing.pkg.transactional import (
    IsolationLevel,
    TransactionalServiceMixin,
    TransactionManager,
    transactional,
)

from ..domain.entities.author import Author
from ..domain.entities.quiz import AnswerOption, Quiz, QuizID
from ..domain.entities.submission import Answer, Submission, SubmissionID
from ..domain.registry import DomainRegistry


class SubmissionService(TransactionalServiceMixin):
    def __init__(self, transaction_manager: TransactionManager) -> None:
        self._transaction_manager = transaction_manager

    @transactional()
    def list(self, author: Author) -> list[Submission]:
        return DomainRegistry.submissions.by_author(author.id)

    @transactional()
    def start(self, author: Author, quiz_id: QuizID) -> Submission:
        submission = Submission.start(quiz_id, author.id)
        DomainRegistry.submissions.save(submission)
        return submission

    @transactional(IsolationLevel.SERIALIZABLE)
    def answer(
        self,
        author: Author,
        submission_id: SubmissionID,
        answers: "list[set[AnswerOption]]",
    ) -> Submission:
        submission = DomainRegistry.submissions.get(submission_id)
        if submission.author_id != author.id:
            raise ValueError(
                f"Author {author.id} is not allowed to answer submission {submission_id}"
            )
        submission.answer(answers)
        DomainRegistry.submissions.save(submission)
        return submission

    @transactional(IsolationLevel.SERIALIZABLE)
    def complete(self, author: Author, submission_id: SubmissionID) -> Submission:
        submission = DomainRegistry.submissions.get(submission_id)
        if submission.author_id != author.id:
            raise ValueError(
                f"Author {author.id} is not allowed to complete submission {submission_id}"
            )
        submission.complete()
        DomainRegistry.submissions.save(submission)
        return submission
