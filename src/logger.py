import logging
from typing import Any

logging.basicConfig(filename='bot.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def log(msg: Any) -> None:
    logging.info(msg)
