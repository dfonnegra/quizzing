from fastapi import APIRouter, Depends, FastAPI, status
from fastapi.exceptions import HTTPException

from quizzing.quiz.domain.dto import QuizFilter
from quizzing.quiz.domain.entities.author import Author
from quizzing.quiz.domain.entities.quiz import QuizID, QuizStatus
from quizzing.quiz.domain.exceptions import NotFound, QuizValidationError

from .auth import authenticate
from .models.quiz import QuizCreate, QuizRead, QuizUpdate
from .registry import RestRegistry

router = APIRouter(prefix="/quizzes")


@router.post("", response_model=QuizRead, status_code=status.HTTP_201_CREATED)
def start_quiz(quiz_create: QuizCreate, author: Author = Depends(authenticate)):
    quiz = RestRegistry.quizzes.create(author, quiz_create.title)
    return QuizRead.from_entity(quiz)


@router.get("", response_model=list[QuizRead])
def list_quizzes(
    status: QuizStatus | None = None,
    page: int = 1,
    page_size: int = 10,
    author: Author = Depends(authenticate),
):
    filter_ = QuizFilter(status=status, page=page, page_size=page_size)
    quizzes = RestRegistry.quizzes.list(author, filter_)
    return [QuizRead.from_entity(quiz) for quiz in quizzes]


@router.get("/{quiz_id}", response_model=QuizRead)
def get_quiz(quiz_id: str, author: Author = Depends(authenticate)):
    try:
        quiz = RestRegistry.quizzes.get(author, quiz_id)
        return QuizRead.from_entity(quiz)
    except NotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.put("/{quiz_id}", response_model=QuizRead)
def edit_quiz(quiz_id: str, quiz_update: QuizUpdate):
    try:
        quiz = RestRegistry.quizzes.edit(
            QuizID(quiz_id),
            quiz_update.title,
            [q.to_entity() for q in quiz_update.questions],
        )
    except QuizValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.errors,
        )
    except NotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    return QuizRead.from_entity(quiz)


@router.post("/{quiz_id}/publish", response_model=QuizRead)
def publish_quiz(quiz_id: str):
    try:
        quiz = RestRegistry.quizzes.publish(QuizID(quiz_id))
        return QuizRead.from_entity(quiz)
    except NotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except QuizValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.errors,
        )
