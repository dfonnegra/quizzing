import pytest

from quizzing.quiz.domain.entities.author import AuthorID
from quizzing.quiz.domain.entities.quiz import (
    AnswerOption,
    Question,
    Quiz,
    QuizID,
    QuizStatus,
)
from quizzing.quiz.domain.entities.submission import Answer
from quizzing.quiz.domain.exceptions import (
    QuizValidationError,
    SubmissionValidationError,
)


def test_quiz_initialization():
    quiz_id = QuizID("1234")
    title = "Sample Quiz"
    author_id = AuthorID("author1")
    quiz = Quiz(quiz_id, title, author_id, QuizStatus.DRAFT)

    assert quiz.id == quiz_id
    assert quiz.title == title
    assert quiz.author_id == author_id
    assert quiz.status == QuizStatus.DRAFT
    assert len(quiz.questions) == 0


def test_quiz_new():
    author_id = AuthorID("author1")
    quiz = Quiz.new("New Quiz", author_id)

    assert quiz.title == "New Quiz"
    assert quiz.author_id == author_id
    assert quiz.status == QuizStatus.DRAFT


def test_set_title():
    quiz_id = QuizID("1234")
    title = "Sample Quiz"
    author_id = AuthorID("author1")
    quiz = Quiz(quiz_id, title, author_id, QuizStatus.DRAFT)

    new_title = "Updated Title"
    quiz.set_title(new_title)
    assert quiz.title == new_title


def test_set_questions():
    quiz_id = QuizID("1234")
    title = "Sample Quiz"
    author_id = AuthorID("author1")
    quiz = Quiz(quiz_id, title, author_id, QuizStatus.DRAFT)

    question = Question(
        "Question 1",
        [AnswerOption("Option 1"), AnswerOption("Option 2")],
        {AnswerOption("Option 1")},
    )
    quiz.set_questions([question])
    assert quiz.questions == [question]


def test_set_questions_too_many():
    quiz_id = QuizID("1234")
    title = "Sample Quiz"
    author_id = AuthorID("author1")
    quiz = Quiz(quiz_id, title, author_id, QuizStatus.DRAFT)

    questions = [
        Question(
            f"Question {i+1}",
            [AnswerOption(f"Option {j+1}") for j in range(5)],
            {AnswerOption("Option 1")},
        )
        for i in range(11)
    ]
    with pytest.raises(QuizValidationError):
        quiz.set_questions(questions)


def test_publish():
    quiz_id = QuizID("1234")
    title = "Sample Quiz"
    author_id = AuthorID("author1")
    quiz = Quiz(quiz_id, title, author_id, QuizStatus.DRAFT)

    question = Question(
        "Question 1",
        [AnswerOption("Option 1"), AnswerOption("Option 2")],
        {AnswerOption("Option 1")},
    )
    quiz.set_questions([question])
    quiz.publish()
    assert quiz.status == QuizStatus.PUBLISHED


def test_publish_no_questions():
    quiz_id = QuizID("1234")
    title = "Sample Quiz"
    author_id = AuthorID("author1")
    quiz = Quiz(quiz_id, title, author_id, QuizStatus.DRAFT)

    with pytest.raises(QuizValidationError):
        quiz.publish()


def test_is_published():
    quiz_id = QuizID("1234")
    title = "Sample Quiz"
    author_id = AuthorID("author1")
    quiz = Quiz(quiz_id, title, author_id, QuizStatus.PUBLISHED)

    assert quiz.is_published()


def test_validate_answers_not_published():
    quiz_id = QuizID("1234")
    title = "Sample Quiz"
    author_id = AuthorID("author1")
    quiz = Quiz(quiz_id, title, author_id, QuizStatus.DRAFT)

    answers = [Answer({AnswerOption("Option 1")})]
    with pytest.raises(SubmissionValidationError):
        quiz.validate_answers(answers)


def test_validate_answers_length_mismatch():
    quiz_id = QuizID("1234")
    title = "Sample Quiz"
    author_id = AuthorID("author1")
    quiz = Quiz(quiz_id, title, author_id, QuizStatus.PUBLISHED)

    quiz.questions = [
        Question(
            "Question 1",
            [AnswerOption("Option 1"), AnswerOption("Option 2")],
            {AnswerOption("Option 1")},
        ),
        Question(
            "Question 2",
            [AnswerOption("Option 1"), AnswerOption("Option 2")],
            {AnswerOption("Option 1")},
        ),
    ]
    answers = [Answer({AnswerOption("Option 1")})]
    with pytest.raises(SubmissionValidationError):
        quiz.validate_answers(answers)


def test_score():
    quiz_id = QuizID("1234")
    title = "Sample Quiz"
    author_id = AuthorID("author1")
    quiz = Quiz(quiz_id, title, author_id, QuizStatus.DRAFT)
    question = Question(
        "Question 1",
        [AnswerOption("Option 1"), AnswerOption("Option 2")],
        {AnswerOption("Option 1")},
    )
    quiz.set_questions([question])
    quiz.publish()
    answers = [Answer({AnswerOption("Option 1")})]
    scored_answers = quiz.score(answers)
    assert scored_answers[0].score == 1


def test_hide_correct_answers():
    quiz_id = QuizID("1234")
    title = "Sample Quiz"
    author_id = AuthorID("author1")
    quiz = Quiz(quiz_id, title, author_id, QuizStatus.DRAFT)

    question = Question(
        "Question 1",
        [AnswerOption("Option 1"), AnswerOption("Option 2")],
        {AnswerOption("Option 1")},
    )
    quiz.set_questions([question])
    quiz.hide_correct_answers()
    assert question.correct_options == set()


def test_can_be_answered():
    quiz_id = QuizID("1234")
    title = "Sample Quiz"
    author_id = AuthorID("author1")
    quiz = Quiz(quiz_id, title, author_id, QuizStatus.PUBLISHED)

    assert quiz.can_be_answered()


def test_question_initialization():
    text = "Sample Question"
    options = [AnswerOption("Option 1"), AnswerOption("Option 2")]
    correct_options = {AnswerOption("Option 1")}
    question = Question(text, options, correct_options)

    assert question.text == text
    assert question.options == options
    assert question.correct_options == correct_options


def test_correct_options_hidden():
    text = "Sample Question"
    options = [AnswerOption("Option 1"), AnswerOption("Option 2")]
    correct_options = {AnswerOption("Option 1")}
    question = Question(text, options, correct_options)

    question.hide_correct_options()
    assert question.correct_options == set()


def test_is_single_choice():
    text = "Sample Question"
    options = [AnswerOption("Option 1"), AnswerOption("Option 2")]
    correct_options = {AnswerOption("Option 1")}
    question = Question(text, options, correct_options)

    assert question.is_single_choice()


def test_validate_answer():
    text = "Sample Question"
    options = [AnswerOption("Option 1"), AnswerOption("Option 2")]
    correct_options = {AnswerOption("Option 1")}
    question = Question(text, options, correct_options)

    answer = Answer({AnswerOption("Option 1")})
    assert question._validate_answer(answer) == []


def test_score_single_choice():
    text = "Sample Question"
    options = [AnswerOption("Option 1"), AnswerOption("Option 2")]
    correct_options = {AnswerOption("Option 1")}
    question = Question(text, options, correct_options)

    answer = Answer({AnswerOption("Option 1")})
    scored_answer = question._score(answer)
    assert scored_answer.score == 1


def test_score_multiple_choice():
    text = "Sample Question"
    options = [
        AnswerOption("Option 1"),
        AnswerOption("Option 2"),
        AnswerOption("Option 3"),
    ]
    correct_options = {AnswerOption("Option 1"), AnswerOption("Option 2")}
    question = Question(text, options, correct_options)

    answer = Answer({AnswerOption("Option 1"), AnswerOption("Option 2")})
    scored_answer = question._score(answer)
    assert scored_answer.score == 1.0


def test_score_partial_credit():
    text = "Sample Question"
    options = [
        AnswerOption("Option 1"),
        AnswerOption("Option 2"),
        AnswerOption("Option 3"),
    ]
    correct_options = {AnswerOption("Option 1"), AnswerOption("Option 2")}
    question = Question(text, options, correct_options)

    answer = Answer({AnswerOption("Option 1")})
    scored_answer = question._score(answer)
    assert scored_answer.score == 0.5


def test_score_negative():
    text = "Sample Question"
    options = [
        AnswerOption("Option 1"),
        AnswerOption("Option 2"),
        AnswerOption("Option 3"),
    ]
    correct_options = {AnswerOption("Option 1"), AnswerOption("Option 2")}
    question = Question(text, options, correct_options)

    answer = Answer({AnswerOption("Option 3")})
    scored_answer = question._score(answer)
    assert scored_answer.score == -1.0
