from dataclasses import dataclass

from .entities.quiz import QuizStatus


@dataclass
class QuizFilter:
    status: QuizStatus | None = None
    author_id: str | None = None
    page: int = 1
    page_size: int = 10
