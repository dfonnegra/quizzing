import uvicorn

from quizzing.pkg.logging import config as config_logging

from . import config

if __name__ == "__main__":
    log_config = config_logging()

    uvicorn.run(
        "quizzing.quiz.infrastructure.rest.api:app",
        reload=config.DEBUG,
        host="0.0.0.0",
        port=80,
        workers=4 if not config.DEBUG else 1,
        log_config=log_config,
    )
