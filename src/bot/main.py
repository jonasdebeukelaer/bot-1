from dotenv import load_dotenv

from coinbase_interface import CoinbaseInterface
from trading_strategy_v2 import TradingStrategy

import functions_framework
from flask import Request


@functions_framework.http
def function_entry_point(_: Request):
    _load_secrets()
    main()
    return "Data ingestion completed.", 200


def _load_secrets():
    with open("/mnt2/secrets.env", "r", encoding="utf-8") as src_file:
        with open(".env", "w", encoding="utf-8") as dest_file:
            dest_file.write(src_file.read())

    load_dotenv()


def main():
    coinbase_interface = CoinbaseInterface()
    trading_strategy = TradingStrategy(coinbase_interface)
    trading_strategy.execute()


if __name__ == "__main__":
    load_dotenv(override=True)
    main()
