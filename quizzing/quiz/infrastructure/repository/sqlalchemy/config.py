import os
import urllib.parse as urlparse

from sqlalchemy import Engine, MetaData, create_engine

_engine: Engine | None = None

_encoded_password = urlparse.quote(os.environ["DB_PASSWORD"])
QUIZZING_QUIZ_DB_URL = f"postgresql://{os.environ['DB_USERNAME']}:{_encoded_password}@{os.environ['DB_HOST']}:{os.environ['DB_PORT']}/{os.environ['DB_NAME']}"


def get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(QUIZZING_QUIZ_DB_URL)
    return _engine


metadata: MetaData | None = None


def get_metadata():
    global metadata
    if metadata is None:
        metadata = MetaData()
    return metadata
