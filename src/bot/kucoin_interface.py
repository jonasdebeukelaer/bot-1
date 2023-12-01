import os
import time

from kucoin.client import Trade, User, Market
from logger import logger


class KucoinInterface:
    def __init__(self):
        API_KEY = os.environ.get("KUCOIN_API_KEY")
        if not API_KEY:
            raise EnvironmentError("The KUCOIN_API_KEY environment variable is not set.")
        API_SECRET = os.environ.get("KUCOIN_API_SECRET")
        if not API_SECRET:
            raise EnvironmentError("The KUCOIN_API_SECRET environment variable is not set.")
        API_PASSPHRASE = os.environ.get("KUCOIN_API_PASSPHRASE")
        if not API_PASSPHRASE:
            raise EnvironmentError("The KUCOIN_API_PASSPHRASE environment variable is not set.")
        URL = os.environ.get("KUCOIN_URL")
        if not URL:
            raise EnvironmentError("The KUCOIN_URL environment variable is not set.")

        self.trade_client = Trade(key=API_KEY, secret=API_SECRET, passphrase=API_PASSPHRASE, url=URL)
        self.user_client = User(key=API_KEY, secret=API_SECRET, passphrase=API_PASSPHRASE, url=URL)
        self.market_client = Market(key=API_KEY, secret=API_SECRET, passphrase=API_PASSPHRASE, url=URL)

    def execute_trade(self, size, side, price):
        if size == 0:
            logger.log_info("No trade wanted (trade size = 0)")
            return

        # TODO: change to limit order when ready
        id = f"{str(time.time_ns())[:-5]}_{size}_{side}_{price}"

        try:
            logger.log_info(f"Executing trade: {id}")
            self.trade_client.create_market_order(clientOid=id, symbol="BTC-GBP", side=side, size=size)
        except Exception as e:
            if "200004" in e.args[0]:
                logger.log_error(
                    f"Insufficient funds in kucoin to execute trade. attempted with {size} {side} at £{price}"
                )
            else:
                raise e

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

        logger.log_info(f"Portfolio breakdown: {output}")
        return output

    def get_last_trades(self, symbol="BTC-GBP", limit=20):
        # just look at first page for now as a limit
        # NOTE: built in limit of up to 1 week old trades only
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

        logger.log_info(f"Last {limit} trades: {cleaned}")
        return cleaned

    def get_part_order_book(self, symbol="BTC-GBP", pieces=20):
        data = self.market_client.get_part_order(symbol=symbol, pieces=pieces)
        data["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(data["time"] / 1000))
        del data["time"], data["sequence"]

        logger.log_info(f"Order book for {symbol}: {data}")
        return data


# test
if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    kucoin = KucoinInterface()

    # # insufficient funds buy
    # kucoin.execute_trade(100000000, "sell", 9000000)

    # data = kucoin.get_portfolio_breakdown()
    # print(data)

    # print("----------")
    # symbols = kucoin.market_client.get_symbol_list_v2()
    # for symbol in symbols:
    #     if symbol["symbol"] == "BTC-GBP":
    #         print(symbol)

    print("----------")
    trades = kucoin.get_last_trades("BTC-GBP")

    print("----------")
    kucoin.get_part_order_book("BTC-GBP")
