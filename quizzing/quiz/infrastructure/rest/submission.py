from fastapi import APIRouter, Depends, FastAPI, status
from fastapi.exceptions import HTTPException

from quizzing.quiz.domain.dto import QuizFilter
from quizzing.quiz.domain.entities.author import Author
from quizzing.quiz.domain.entities.quiz import AnswerOption, QuizID, QuizStatus
from quizzing.quiz.domain.entities.submission import SubmissionID
from quizzing.quiz.domain.exceptions import NotFound, SubmissionValidationError

from .auth import authenticate
from .models.submission import SubmissionAnswer, SubmissionCreate, SubmissionRead
from .registry import RestRegistry

router = APIRouter(prefix="/submissions")


@router.post("", response_model=SubmissionCreate, status_code=status.HTTP_201_CREATED)
def start_submission(
    submission_create: SubmissionCreate, author: Author = Depends(authenticate)
):
    try:
        submission = RestRegistry.submissions.start(
            author, QuizID(submission_create.quiz_id)
        )
        return SubmissionRead.from_entity(submission)
    except NotFound as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))
    except SubmissionValidationError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, e.errors)


@router.get("", response_model=list[SubmissionRead])
def submissions(author: Author = Depends(authenticate)):
    return [
        SubmissionRead.from_entity(submission)
        for submission in RestRegistry.submissions.list(author)
    ]


@router.put("/{submission_id}/answers", response_model=SubmissionRead)
def answer_submission(
    submission_id: str,
    submission_answer: SubmissionAnswer,
    author: Author = Depends(authenticate),
):
    try:
        submission = RestRegistry.submissions.answer(
            author,
            SubmissionID(submission_id),
            [
                {AnswerOption(o) for o in options}
                for options in submission_answer.answers
            ],
        )
    except NotFound as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))
    except SubmissionValidationError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, e.errors)
    return SubmissionRead.from_entity(submission)


@router.put("/{submission_id}/complete", response_model=SubmissionRead)
def complete_submission(submission_id: str, author: Author = Depends(authenticate)):
    try:
        submission = RestRegistry.submissions.complete(
            author, SubmissionID(submission_id)
        )
    except NotFound as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))
    except SubmissionValidationError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, e.errors)
    return SubmissionRead.from_entity(submission)
