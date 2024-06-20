from fastapi import APIRouter, Depends, FastAPI, status
from fastapi.exceptions import HTTPException

from quizzing.quiz.domain.dto import QuizFilter
from quizzing.quiz.domain.entities.author import Author
from quizzing.quiz.domain.entities.quiz import QuizID, QuizStatus
from quizzing.quiz.domain.exceptions import QuizValidationError

from .auth import authenticate
from .auth import router as auth_router
from .models.quiz import QuizCreate, QuizRead, QuizUpdate
from .registry import RestRegistry

api_router = APIRouter(prefix="/api")


@api_router.post(
    "/quizzes", response_model=QuizRead, status_code=status.HTTP_201_CREATED
)
def start_quiz(quiz_create: QuizCreate, author: Author = Depends(authenticate)):
    quiz = RestRegistry.quizzes.create(author, quiz_create.title)
    return QuizRead.from_entity(quiz)


@api_router.post(
    "/quizzes", response_model=QuizRead, status_code=status.HTTP_201_CREATED
)
def list_quizzes(
    status: QuizStatus | None = None,
    page: int = 1,
    page_size: int = 10,
    author: Author = Depends(authenticate),
):
    filter_ = QuizFilter(status=status, page=page, page_size=page_size)
    quizzes = RestRegistry.quizzes.list(author, filter_)
    return [QuizRead.from_entity(quiz) for quiz in quizzes]


@api_router.get("/quizzes/{quiz_id}", response_model=QuizRead)
def get_quiz(quiz_id: str, author: Author = Depends(authenticate)):
    quiz = RestRegistry.quizzes.get(author, quiz_id)
    return QuizRead.from_entity(quiz)


@api_router.put("/quizzes/{quiz_id}", response_model=QuizRead)
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
    return QuizRead.from_entity(quiz)


app = FastAPI()
app.include_router(auth_router)
app.include_router(api_router)
