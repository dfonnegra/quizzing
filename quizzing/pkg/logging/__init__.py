import logging
import logging.config
from typing import Any

import yaml


def config() -> dict[str, Any]:
    with open("quizzing/pkg/logging/logging.yaml", "r") as log_config_file:
        config = yaml.load(log_config_file, Loader=yaml.FullLoader)

    logging.basicConfig(level=logging.INFO)
    logging.config.dictConfig(config)
    return config
