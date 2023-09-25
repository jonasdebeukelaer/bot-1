from kucoin_interface import KucoinInterface
from trading_strategy import TradingStrategy
import time

def main():
  kucoin = KucoinInterface()
  trading_strategy = TradingStrategy(kucoin)

  # Start hourly trading loop
  while True:
    kucoin.update_prices()
    trading_strategy.execute()
    time.sleep(3600) # sleep for an hour

if __name__ == "__main__":
  main()