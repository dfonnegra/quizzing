from sqlalchemy import (
    Column,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ARRAY

from .config import get_metadata

author_table = Table(
    "author",
    get_metadata(),
    Column("id", String, primary_key=True),
    Column("email", String, nullable=False, unique=True),
    Column("hashed_password", String, nullable=False),
)

quiz_table = Table(
    "quiz",
    get_metadata(),
    Column("id", String, primary_key=True),
    Column("title", String, nullable=False),
    Column("author_id", String, ForeignKey("author.id"), nullable=False),
    Column("status", Enum("draft", "published", name="quiz_status")),
)

question_table = Table(
    "question",
    get_metadata(),
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("index", Integer, nullable=False),
    Column("quiz_id", String, ForeignKey("quiz.id"), nullable=False),
    Column("text", String, nullable=False),
    Column("options", ARRAY(String), nullable=False),
    Column("correct_options", ARRAY(String), nullable=False),
)

submission_table = Table(
    "submission",
    get_metadata(),
    Column("id", String, primary_key=True),
    Column("quiz_id", String, ForeignKey("quiz.id"), nullable=False),
    Column("author_id", String, ForeignKey("author.id"), nullable=False),
    Column("status", Enum("in_progress", "completed", name="submission_status")),
    Column("score", Float, nullable=True),
    UniqueConstraint("quiz_id", "author_id"),
)

answer_table = Table(
    "answer",
    get_metadata(),
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("submission_id", String, ForeignKey("submission.id"), nullable=False),
    Column("index", Integer, nullable=False),
    Column("options", ARRAY(String), nullable=False),
    Column("score", Float, nullable=True),
)
