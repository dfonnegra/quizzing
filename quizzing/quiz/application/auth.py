from quizzing.pkg.transactional import (
    TransactionalServiceMixin,
    TransactionManager,
    transactional,
)

from ..domain.entities.author import Author
from ..domain.exceptions import AuthorExists, NotFound
from ..domain.registry import DomainRegistry


class AuthorService(TransactionalServiceMixin):
    def __init__(self, transaction_manager: TransactionManager) -> None:
        self._transaction_manager = transaction_manager

    @transactional()
    def by_email(self, email: str) -> Author:
        return DomainRegistry.authors.by_email(email)

    @transactional()
    def create(self, email: str, password: str):
        try:
            self.by_email(email)
            raise AuthorExists(f"Author with email '{email}' already exists")
        except NotFound:
            author = Author.new(email, password)
            DomainRegistry.authors.save(author)
