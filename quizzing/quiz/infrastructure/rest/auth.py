from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt

from quizzing.quiz.domain.entities.author import Author
from quizzing.quiz.domain.exceptions import AuthorExists, NotFound

from . import config
from .models.auth import Token
from .registry import RestRegistry

router = APIRouter(prefix="/api")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
RestRegistry.initialize()


@router.post("/login", response_model=Token)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    invalid_email_or_password = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Incorrect email or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        author = RestRegistry.authors.by_email(form_data.username)
    except NotFound:
        raise invalid_email_or_password

    if author.verify_password(form_data.password):
        raise invalid_email_or_password

    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": author.email}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    try:
        RestRegistry.authors.create(form_data.username, form_data.password)
    except AuthorExists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Author with email {form_data.username} already exists",
            headers={"WWW-Authenticate": "Bearer"},
        )


def authenticate(token: Annotated[str, Depends(oauth2_scheme)]) -> Author:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        email: str | None = payload.get("sub")
        if email is None:
            raise credentials_exception

        try:
            return RestRegistry.authors.by_email(email)
        except NotFound:
            raise credentials_exception
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    return encoded_jwt
