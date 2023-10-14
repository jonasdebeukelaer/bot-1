import time

from kucoin_interface import KucoinInterface
from dotenv import load_dotenv

from trading_strategy import TradingStrategy
from crypto_indicators import CryptoIndicators

ONE_HOUR = 3600


def main():
    load_dotenv()
    kucoin = KucoinInterface()
    indicators_fetcher = CryptoIndicators()
    trading_strategy = TradingStrategy(kucoin, indicators_fetcher)

    while True:
        indicators_fetcher.get_indicators()
        trading_strategy.execute()
        time.sleep(ONE_HOUR)


if __name__ == "__main__":
    main()
