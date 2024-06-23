from dataclasses import dataclass

from quizzing.quiz.domain.dto import QuizFilter
from quizzing.quiz.domain.entities.author import Author, AuthorID
from quizzing.quiz.domain.entities.quiz import Quiz, QuizID
from quizzing.quiz.domain.entities.submission import Submission
from quizzing.quiz.domain.exceptions import NotFound


class InMemoryQuizRepository:
    def __init__(self):
        self.quizzes = {}

    def get(self, quiz_id: str) -> Quiz:
        if quiz_id not in self.quizzes:
            raise NotFound(f"Quiz {quiz_id} not found")
        return self.quizzes[quiz_id]

    def save(self, quiz: Quiz) -> None:
        self.quizzes[quiz.id] = quiz

    def list(self, filter_: QuizFilter) -> list[Quiz]:
        return list(self.quizzes.values())


class InMemorySubmissionRepository:
    def __init__(self):
        self.submissions = []

    def by_author(self, author_id: AuthorID) -> list[Submission]:
        return [
            submission
            for submission in self.submissions
            if submission.author_id == author_id
        ]

    def by_quiz(
        self, quiz_id: QuizID, page: int | None = None, page_size: int | None = None
    ) -> list[Submission]:
        return [
            submission
            for submission in self.submissions
            if submission.quiz_id == quiz_id
        ]

    def save(self, submission: Submission) -> None:
        self.submissions.append(submission)

    def get(self, submission_id: str) -> Submission:
        for submission in self.submissions:
            if submission.id == submission_id:
                return submission
        raise NotFound(f"Submission {submission_id} not found")


class InMemoryAuthorRepository:
    def __init__(self):
        self.authors = {}

    def by_email(self, email: str) -> Author:
        for author in self.authors.values():
            if author.email == email:
                return author
        raise NotFound(f"Author with email {email} not found")

    def save(self, author: Author) -> None:
        self.authors[author.id] = author
