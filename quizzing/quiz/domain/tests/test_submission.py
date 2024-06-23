import pytest

from quizzing.quiz.domain.entities.author import AuthorID
from quizzing.quiz.domain.entities.quiz import (
    AnswerOption,
    Question,
    Quiz,
    QuizID,
    QuizStatus,
)
from quizzing.quiz.domain.entities.submission import Answer, Submission, SubmissionID
from quizzing.quiz.domain.exceptions import NotFound, SubmissionValidationError
from quizzing.quiz.domain.registry import DomainRegistry
from quizzing.quiz.infrastructure.repository.inmemory.repository import (
    InMemoryAuthorRepository,
    InMemoryQuizRepository,
    InMemorySubmissionRepository,
)


def setup_function():
    quiz_repo = InMemoryQuizRepository()
    submission_repo = InMemorySubmissionRepository()
    author_repo = InMemoryAuthorRepository()
    DomainRegistry.initialize(quiz_repo, submission_repo, author_repo)


def test_submission_initialization():
    submission_id = SubmissionID("1234")
    quiz_id = QuizID("quiz1")
    author_id = AuthorID("author1")
    status = Submission.Status.IN_PROGRESS
    answers = [Answer({AnswerOption("Option 1")})]
    score = None

    submission = Submission(submission_id, quiz_id, author_id, status, answers, score)

    assert submission.id == submission_id
    assert submission.quiz_id == quiz_id
    assert submission.author_id == author_id
    assert submission.status == status
    assert submission.answers == answers
    assert submission.score == score


def test_submission_start():
    quiz_id = QuizID("quiz1")
    author_id = AuthorID("author1")
    question = Question(
        "Question 1",
        [AnswerOption("Option 1"), AnswerOption("Option 2")],
        {AnswerOption("Option 1")},
    )
    quiz = Quiz(quiz_id, "Sample Quiz", author_id, QuizStatus.PUBLISHED)
    quiz.questions = [question]
    DomainRegistry.quizzes.save(quiz)

    submission = Submission.start(quiz_id, author_id)

    assert submission.quiz_id == quiz_id
    assert submission.author_id == author_id
    assert submission.status == Submission.Status.IN_PROGRESS
    assert len(submission.answers) == len(quiz.questions)
    assert all(answer.is_empty() for answer in submission.answers)


def test_submission_start_quiz_not_found():
    quiz_id = QuizID("quiz2")
    author_id = AuthorID("author1")

    with pytest.raises(NotFound):
        Submission.start(quiz_id, author_id)


def test_submission_start_already_exists():
    quiz_id = QuizID("quiz1")
    author_id = AuthorID("author2")
    question = Question(
        "Question 1",
        [AnswerOption("Option 1"), AnswerOption("Option 2")],
        {AnswerOption("Option 1")},
    )
    quiz = Quiz(quiz_id, "Sample Quiz", author_id, QuizStatus.PUBLISHED)
    quiz.questions = [question]
    DomainRegistry.quizzes.save(quiz)

    submission = Submission.start(quiz_id, author_id)
    DomainRegistry.submissions.save(submission)

    with pytest.raises(SubmissionValidationError):
        Submission.start(quiz_id, author_id)


def test_submission_answer():
    quiz_id = QuizID("quiz1")
    author_id = AuthorID("author1")
    question = Question(
        "Question 1",
        [AnswerOption("Option 1"), AnswerOption("Option 2")],
        {AnswerOption("Option 1")},
    )
    quiz = Quiz(quiz_id, "Sample Quiz", author_id, QuizStatus.PUBLISHED)
    quiz.questions = [question]
    DomainRegistry.quizzes.save(quiz)

    submission = Submission.start(quiz_id, author_id)
    DomainRegistry.submissions.save(submission)

    answers = [{AnswerOption("Option 1")}]
    submission.answer(answers)
    assert len(submission.answers) == 1
    assert submission.answers[0].options == answers[0]


def test_submission_complete():
    quiz_id = QuizID("quiz1")
    author_id = AuthorID("author1")
    question = Question(
        "Question 1",
        [AnswerOption("Option 1"), AnswerOption("Option 2")],
        {AnswerOption("Option 1")},
    )
    quiz = Quiz(quiz_id, "Sample Quiz", author_id, QuizStatus.PUBLISHED)
    quiz.questions = [question]
    DomainRegistry.quizzes.save(quiz)

    submission = Submission.start(quiz_id, author_id)
    DomainRegistry.submissions.save(submission)

    answers = [{AnswerOption("Option 1")}]
    submission.answer(answers)
    submission.complete()

    assert submission.status == Submission.Status.COMPLETED
    assert submission.score == 1.0


def test_submission_complete_already_completed():
    quiz_id = QuizID("quiz1")
    author_id = AuthorID("author1")
    question = Question(
        "Question 1",
        [AnswerOption("Option 1"), AnswerOption("Option 2")],
        {AnswerOption("Option 1")},
    )
    quiz = Quiz(quiz_id, "Sample Quiz", author_id, QuizStatus.PUBLISHED)
    quiz.questions = [question]
    DomainRegistry.quizzes.save(quiz)

    submission = Submission.start(quiz_id, author_id)
    DomainRegistry.submissions.save(submission)

    answers = [{AnswerOption("Option 1")}]
    submission.answer(answers)
    submission.complete()

    with pytest.raises(SubmissionValidationError):
        submission.complete()
