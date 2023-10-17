import os
import time
import json

from kucoin.client import Trade, User, Market
from logger import log


class KucoinInterface:
    def __init__(self):
        API_KEY = os.environ.get("KUCOIN_API_KEY")
        API_SECRET = os.environ.get("KUCOIN_API_SECRET")
        API_PASSPHRASE = os.environ.get("KUCOIN_API_PASSPHRASE")
        URL = os.environ.get("KUCOIN_URL")
        self.trade_client = Trade(key=API_KEY, secret=API_SECRET, passphrase=API_PASSPHRASE, url=URL)
        self.user_client = User(key=API_KEY, secret=API_SECRET, passphrase=API_PASSPHRASE, url=URL)
        self.market_client = Market(key=API_KEY, secret=API_SECRET, passphrase=API_PASSPHRASE, url=URL)

    def execute_trade(self, size, side, price):
        if size == 0:
            log("No trade wanted (trade size = 0)")
            return

        # TODO: change to limit order when ready
        id = f"{str(time.time_ns())[:-5]}_{size}_{side}_{price}"

        log(f"Executing trade: {id}")
        self.trade_client.create_market_order(clientOid=id, symbol="BTC-GBP", side=side, size=size)

    def get_portfolio_breakdown(self):
        data = self.user_client.get_account_list()

        output = []
        for entry in data:
            if entry["currency"] not in ["GBP", "USDT", "BTC"]:
                continue

            new_entry = entry
            del new_entry["id"]
            del new_entry["type"]

            output.append(new_entry)

        log(f"Portfolio breakdown: {output}")
        return output

    def get_last_trades(self, symbol="BTC-GBP", limit=20):
        # just look at first page for now as a limit
        data = self.trade_client.get_fill_list(tradeType="TRADE", symbol=symbol, pageSize=limit)
        cleaned = []
        for item in data["items"]:
            cleaned.append(
                {
                    "symbol": item["symbol"],
                    "side": item["side"],
                    "price": item["price"],
                    "size": item["size"],
                    "fee": f'{item["fee"]} {item["feeCurrency"]}',
                    "createdAt": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(item["createdAt"] / 1000)),
                }
            )

        log(f"Last {limit} trades: {cleaned}")
        return data["items"]


# test
if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    kucoin = KucoinInterface()

    data = kucoin.get_portfolio_breakdown()

    print(data)

    print("----------")
    symbols = kucoin.market_client.get_symbol_list_v2()
    for symbol in symbols:
        if symbol["symbol"] == "BTC-GBP":
            print(symbol)

    trades = kucoin.get_last_trades("BTC-GBP")
    # print(trades)
