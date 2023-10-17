import logging
from typing import Any

logging.basicConfig(filename="bot.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logging.getLogger().addHandler(logging.StreamHandler())

# TODO: change to class
counter = 1

def log(msg: Any) -> None:
    global counter
    logging.info(f"{counter}: " + msg)
    counter += 1

def reset_counter() -> None:
    global counter
    counter = 1
