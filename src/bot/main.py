import time
import sys
import signal

from dotenv import load_dotenv

from src.bot.kucoin_interface import KucoinInterface
from src.bot.trading_strategy import TradingStrategy
from src.bot.crypto_indicators import CryptoIndicators

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
        while True:
            indicators_fetcher_hourly.fetch_indicators()
            # TODO: find way to update daily indicator in history if same day
            indicators_fetcher_daily.fetch_indicators()

            trading_strategy.execute()
            time.sleep(ONE_HOUR)

    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
