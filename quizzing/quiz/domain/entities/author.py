from uuid import uuid4

import bcrypt


class AuthorID(str): ...


class Author:
    def __init__(
        self,
        id: AuthorID,
        email: str,
        hashed_password: str,
    ) -> None:
        self._id = id
        self._email = email
        self._hashed_password = hashed_password

    def verify_password(self, plain_password: str) -> bool:
        password_byte_enc = plain_password.encode("utf-8")
        return bcrypt.checkpw(
            password=password_byte_enc,
            hashed_password=self._hashed_password.encode("utf-8"),
        )

    @classmethod
    def new(cls, email: str, password: str) -> "Author":
        id_ = AuthorID(str(uuid4()))
        pwd_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
        return cls(id_, email, hashed_password.decode("utf-8"))

    @property
    def email(self) -> str:
        return self._email

    @property
    def id(self) -> AuthorID:
        return self._id

    @property
    def hashed_password(self) -> str:
        return self._hashed_password
