from kucoin_interface import KucoinInterface
from trading_strategy import TradingStrategy
import time

ONE_HOUR = 3600


def main():
  kucoin = KucoinInterface()
  trading_strategy = TradingStrategy(kucoin)

  while True:
    kucoin.update_prices()
    trading_strategy.execute()
    time.sleep(ONE_HOUR)


if __name__ == "__main__":
  main()
