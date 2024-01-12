import time
import sys
import signal

from kucoin_interface import KucoinInterface
from dotenv import load_dotenv

from trading_strategy import TradingStrategy
from crypto_indicators import CryptoIndicators

ONE_HOUR = 3600


def signal_handler(signum, frame):
    print("Signal received, initiating graceful shutdown...")
    sys.exit(0)


def main():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    load_dotenv()
    kucoin = KucoinInterface()
    indicators_fetcher_hourly = CryptoIndicators()
    indicators_fetcher_daily = CryptoIndicators(interval="1d")
    trading_strategy = TradingStrategy(kucoin, indicators_fetcher_hourly, indicators_fetcher_daily)

    try:
        current_dom = time.localtime().tm_mday
        while True:
            indicators_fetcher_hourly.fetch_indicators()

            if time.localtime().tm_mday != current_dom:
                indicators_fetcher_daily.fetch_indicators()
                current_dom = time.localtime().tm_mday

            trading_strategy.execute()
            time.sleep(ONE_HOUR)

    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
