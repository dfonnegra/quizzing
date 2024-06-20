from fastapi import APIRouter, FastAPI

from .auth import router as auth_router
from .quiz import router as quiz_router
from .submission import router as submission_router

app = FastAPI()
api_router = APIRouter(prefix="/api")
app.include_router(auth_router)
app.include_router(quiz_router)
app.include_router(submission_router)
