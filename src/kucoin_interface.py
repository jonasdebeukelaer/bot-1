import os

from kucoin.client import Trade, Market
from peewee import PostgresqlDatabase
from playhouse.shortcuts import model_to_dict
from metrics import calculate_EMA, calculate_RSI, calculate_Fear_Greed_Index


class KucoinInterface:
  API_KEY = os.environ.get("KUCOIN_API_KEY")
  API_SECRET = os.environ.get("KUCOIN_API_SECRET")
  API_PASSPHRASE = os.environ.get("KUCOIN_API_PASSPHRASE")
  URL = os.environ.get("KUCOIN_URL")

  def __init__(self):
    self.trade_client = Trade(key=self.API_KEY, secret=self.API_SECRET, passphrase=self.API_PASSPHRASE, url=self.URL)
    self.market_client = Market(self.URL)
    self.price_history = []

  def execute_trade(self, size, price):
    # add actual trading command for the KuCoin
    self.trade_client.create_market_order('BTC-GBP', 'buy', size=size)

  def update_prices(self):
    # Query the last price of BTC and append to price history
    latest_price = self.market_client.get_ticker('BTC-GBP')['price']
    self.price_history.append(latest_price)

    # Calculate and store trading indicators
    self.ema_50 = calculate_EMA(self.price_history, 50)
    self.ema_200 = calculate_EMA(self.price_history, 200)
    self.ema_800 = calculate_EMA(self.price_history, 800)
    self.rsi = calculate_RSI(self.price_history)
    self.fear_greed_index = calculate_Fear_Greed_Index(self.price_history)

  def get_trade_indicators(self):
    return self.price_history, self.ema_50, self.ema_200, self.ema_800, self.rsi, self.fear_greed_index