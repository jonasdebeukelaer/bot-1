import logging
from typing import Any


class Logger:
    def __init__(self, filename: str = "bot.log"):
        self.counter = 1
        self.setup_logger(filename)

    def setup_logger(self, filename: str) -> None:
        logging.basicConfig(filename=filename, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
        logging.getLogger().addHandler(logging.StreamHandler())

    def log_info(self, msg: Any) -> None:
        logging.info(f"{self.counter}: {msg}")
        self.counter += 1

    def log_error(self, msg: Any) -> None:
        logging.error(f"{self.counter}: {msg}")
        self.counter += 1

    def reset_counter(self) -> None:
        self.counter = 1


logger = Logger("bot.log")
