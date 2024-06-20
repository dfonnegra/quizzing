from .ports import AuthorRepository, QuizRepository, SubmissionRepository


class DomainRegistry:
    quiz: QuizRepository
    submissions: SubmissionRepository
    authors: AuthorRepository

    @classmethod
    def initialize(
        cls,
        quiz: QuizRepository,
        submission: SubmissionRepository,
        author: AuthorRepository,
    ) -> None:
        cls.quiz = quiz
        cls.submissions = submission
        cls.authors = author
