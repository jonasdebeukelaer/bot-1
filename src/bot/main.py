from dotenv import load_dotenv

from kucoin_interface import KucoinInterface
from trading_strategy import TradingStrategy
from data_retriever import DataRetriever

import functions_framework
from flask import Request


@functions_framework.http
def function_entry_point(request: Request):
    _load_secrets()
    main()
    return "Data ingestion completed.", 200


def _load_secrets():
    with open("/mnt2/secrets.env", "r") as src_file:
        with open(".env", "w") as dest_file:
            dest_file.write(src_file.read())

    load_dotenv()


def main():
    kucoin = KucoinInterface()
    crypto_data = DataRetriever().get_latest()
    trading_strategy = TradingStrategy(kucoin, crypto_data)
    trading_strategy.execute()


if __name__ == "__main__":
    load_dotenv()
    main()
