class QuizValidationError(Exception):
    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        msg = "\n".join(errors)
        super().__init__(msg)


class SubmissionValidationError(Exception):
    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        msg = "\n".join(errors)
        super().__init__(msg)


class NotFound(Exception): ...


class AuthorExists(Exception): ...
