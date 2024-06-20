import os

ACCESS_TOKEN_EXPIRE_MINUTES = 14 * 24 * 60
SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = "HS256"
DEBUG = bool(int(os.environ.get("DEBUG", 0)))
