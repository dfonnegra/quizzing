from psycopg2.errors import SerializationFailure
from sqlalchemy import Engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from quizzing.pkg.transactional import IsolationLevel, Transaction


class SQLATransaction(Transaction):
    def __init__(self, session: Session, isolation_level: IsolationLevel) -> None:
        self._session: Session = session
        self._begin_count = 0
        self._is_started = False
        self._isolation_level = isolation_level

    def begin(self) -> None:
        self._begin_count += 1
        if self._is_started:
            return
        self._session.begin()
        self._session.connection(
            execution_options={
                "isolation_level": self._map_isolation_level(self._isolation_level)
            }
        )
        self._is_started = True

    def commit(self) -> None:
        self._begin_count -= 1
        self._begin_count = max(0, self._begin_count)
        if self._begin_count == 0 and self._is_started:
            self._session.commit()
            self._session.close()
            self._is_started = False

    def rollback(self) -> None:
        self._begin_count -= 1
        self._begin_count = max(0, self._begin_count)
        if self._begin_count == 0 and self._is_started:
            self._session.rollback()
            self._session.close()
            self._is_started = False

    @property
    def is_closed(self) -> bool:
        return self._is_started and self._begin_count == 0

    @property
    def session(self) -> Session:
        return self._session

    def _map_isolation_level(self, il: IsolationLevel) -> str:
        if il == IsolationLevel.READ_UNCOMMITTED:
            return "READ UNCOMMITTED"
        elif il == IsolationLevel.READ_COMMITTED:
            return "READ COMMITTED"
        elif il == IsolationLevel.REPEATABLE_READ:
            return "REPEATABLE READ"
        elif il == IsolationLevel.SERIALIZABLE:
            return "SERIALIZABLE"
        else:
            raise ValueError(f"Unknown isolation level: {il}")


class SQLATransactionManager:
    def __init__(self, engine: Engine) -> None:
        self._transaction: SQLATransaction | None = None
        self._engine = engine

    def transaction(
        self, isolation_level: IsolationLevel = IsolationLevel.READ_COMMITTED
    ) -> SQLATransaction:
        if self._transaction is None or self._transaction.is_closed:
            self._transaction = SQLATransaction(Session(self._engine), isolation_level)
        return self._transaction

    def is_retriable_exception(self, ex: Exception) -> bool:
        if isinstance(ex, OperationalError):
            if isinstance(ex.orig, SerializationFailure):
                return True
            return False
        return False
