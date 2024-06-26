from dotenv import load_dotenv

from kucoin_interface import KucoinInterface
from trading_strategy import TradingStrategy
from crypto_indicators import CryptoIndicators

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
    indicators_fetcher_hourly = CryptoIndicators()
    indicators_fetcher_daily = CryptoIndicators(interval="1d")
    trading_strategy = TradingStrategy(kucoin, indicators_fetcher_hourly, indicators_fetcher_daily)

    try:
        indicators_fetcher_hourly.fetch_indicators()
        # TODO: find way to update daily indicator in history if same day
        indicators_fetcher_daily.fetch_indicators()

        trading_strategy.execute()

    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    load_dotenv()
    main()
