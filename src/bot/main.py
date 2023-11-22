import time
import sys
import signal

from kucoin_interface import KucoinInterface
from dotenv import load_dotenv

from trading_strategy import TradingStrategy
from crypto_indicators import CryptoIndicators
from logging import log

ONE_HOUR = 3600


def signal_handler(signum, frame):
    print("Signal received, initiating graceful shutdown...")
    sys.exit(0)


def main():
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    load_dotenv()
    kucoin = KucoinInterface()
    indicators_fetcher = CryptoIndicators()
    trading_strategy = TradingStrategy(kucoin, indicators_fetcher)

    try:
        while True:
            indicators_fetcher.fetch_indicators()
            trading_strategy.execute()
            time.sleep(ONE_HOUR)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
