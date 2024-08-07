import os
import logging
from typing import Any


class Logger:
    def __init__(self):
        self.counter = 1
        self.setup_logger()

    def setup_logger(self) -> None:
        level = logging.DEBUG if os.environ.get("DEBUG", "false") == "true" else logging.INFO

        logging.basicConfig(level=level, format="%(asctime)s - %(levelname)s - %(message)s")
        logging.getLogger().addHandler(logging.StreamHandler())

    def log_debug(self, msg: Any) -> None:
        logging.debug("%s: %s", self.counter, msg)
        self.counter += 1

    def log_info(self, msg: Any) -> None:
        logging.info("%s: %s", self.counter, msg)
        self.counter += 1

    def log_error(self, msg: Any) -> None:
        logging.error("%s: %s", self.counter, msg)
        self.counter += 1


logger = Logger()
