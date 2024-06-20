import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from functools import wraps
from random import uniform
from typing import Any, Callable, ParamSpec, Protocol, TypeVar

from typing_extensions import Self


class IsolationLevel(Enum):
    READ_UNCOMMITTED = 1
    READ_COMMITTED = 2
    REPEATABLE_READ = 3
    SERIALIZABLE = 4


@dataclass
class RetryParams:
    max_retries: int = 3
    min_delay: float = 0.1
    max_delay: float = 1.0


class Transaction(ABC):
    def __enter__(self) -> Self:
        self.begin()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.rollback()
            return
        self.commit()

    @abstractmethod
    def begin(self): ...

    @abstractmethod
    def commit(self): ...

    @abstractmethod
    def rollback(self): ...


class TransactionManager(Protocol):
    def transaction(
        self, isolation_level: IsolationLevel = IsolationLevel.READ_COMMITTED
    ) -> Transaction: ...

    def is_retriable_exception(self, ex: Exception) -> bool: ...


P = ParamSpec("P")
R = TypeVar("R")


def transactional(
    isolation_level: IsolationLevel = IsolationLevel.READ_COMMITTED,
    retry_params: RetryParams | None = None,
):
    def func(f: Callable[P, R]) -> Callable[P, R]:
        f._is_transactional = True
        f._isolation_level = isolation_level
        f._retry_params = retry_params
        if retry_params is None:
            f._retry_params = RetryParams()
        return f

    return func


class MaxRetryError(Exception):
    pass


class TransactionalServiceMixin:
    _transaction_manager: TransactionManager

    def __getattribute__(self, __name: str) -> Any:
        attr = super().__getattribute__(__name)
        if not callable(attr) or not getattr(attr, "_is_transactional", False):
            return attr
        isolation_level: IsolationLevel = getattr(attr, "_isolation_level")
        retry_params: RetryParams = getattr(attr, "_retry_params")

        @wraps(attr)
        def wrapper(*args, **kwargs):
            for _ in range(retry_params.max_retries + 1):
                try:
                    with self._transaction_manager.transaction(isolation_level):
                        return attr(*args, **kwargs)
                except Exception as ex:
                    if not self._transaction_manager.is_retriable_exception(ex):
                        raise ex
                    if retry_params.max_retries == 0:
                        raise MaxRetryError() from ex
                    time.sleep(uniform(retry_params.min_delay, retry_params.max_delay))

        return wrapper
