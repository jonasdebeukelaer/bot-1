import os
import time
from typing import Any, Dict, List

from kucoin.client import Trade, User, Market

from src.bot.logger import logger
from src.bot.util import format_value
from src.bot.typess.PortfolioBreakdown import PortfolioBreakdown

SMALLEST_TRADE_SIZE_PERCENTAGE = 10
BTC_INCREMENT_DECIMAL = 4


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

    def execute_trade(self, latest_bitcoin_price: float, bitcoin_holding_percentage_request: float) -> None:
        portfolio_breakdown = self.get_portfolio_breakdown()

        if bitcoin_holding_percentage_request < 0 or bitcoin_holding_percentage_request > 100:
            raise ValueError(f"Invalid percentage value '{bitcoin_holding_percentage_request}'")

        current_btc_percentage = portfolio_breakdown.get_btc_percentage(latest_bitcoin_price)
        difference = bitcoin_holding_percentage_request - current_btc_percentage

        # Check if trade size is too small to bother
        if abs(difference) < SMALLEST_TRADE_SIZE_PERCENTAGE:
            logger.log_info("No trade wanted (porfolio change would be < 10%). Avoiding these small changes to save on fees.")
            return

        # Calculate trade size based on difference
        # For simplicity, let's assume trade size is proportional to the difference in percentages
        btc_in_gbp = portfolio_breakdown.get_btc_in_gbp(latest_bitcoin_price)
        trade_size_gbp = abs(btc_in_gbp * difference / 100)
        trade_size_btc = round(trade_size_gbp / latest_bitcoin_price, BTC_INCREMENT_DECIMAL)

        side = "buy" if difference > 0 else "sell"

        timestamp = str(time.time_ns())[:-5]
        id = f"{timestamp}_{trade_size_btc}_{side}"

        try:
            # Execute trade
            logger.log_info(f"Executing trade: {id}")
            self.trade_client.create_market_order(clientOid=id, symbol="BTC-GBP", side=side, size=trade_size_btc)
        except Exception as e:
            if type(e.args) == tuple and "200004" in e.args[0]:
                logger.log_error(
                    f"Insufficient funds in KuCoin to execute trade. Attempted with {trade_size_btc} BTC ({trade_size_gbp} GBP) at market price"
                )
            else:
                raise e

    def get_portfolio_breakdown(self) -> PortfolioBreakdown:
        data = self.user_client.get_account_list()

        relevant_data = []
        for entry in data:
            if entry["currency"] not in ["GBP", "USDT", "BTC"]:
                continue
            elif entry["balance"] == "0" or entry["available"] == "0":
                continue

            relevant_data.append(entry)

        portfolio = PortfolioBreakdown(relevant_data)
        logger.log_info(f"Portfolio breakdown: {portfolio.get_formatted()}")
        return portfolio

    def get_last_trades(self, symbol="BTC-GBP", limit=20) -> List[str]:
        # just look at first page for now as a limit
        # NOTE: built in limit of up to 1 week old trades only
        data = self.trade_client.get_fill_list(tradeType="TRADE", symbol=symbol, pageSize=limit)
        formatted = []
        for item in data["items"]:
            ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(item["createdAt"] / 1000))
            formatted.append(f"{ts} {item['side']} {item['size']} {item['symbol']} at £{format_value(item['price'])}")

        logger.log_info(f"Last {limit} trades: {formatted}")
        return formatted

    def get_part_order_book(self, symbol="BTC-GBP", pieces=20) -> Dict[str, Any]:
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

    data = kucoin.get_portfolio_breakdown()
    print(data)

    data.get_btc_percentage()
    kucoin.execute_trade({"BTC": "100", "GBP": "20000"}, 100.000, 10)

    print("----------")
    symbols = kucoin.market_client.get_symbol_list_v2()
    for symbol in symbols:
        if symbol["symbol"] == "BTC-GBP":
            print(symbol)

    print("----------")
    trades = kucoin.get_last_trades("BTC-GBP")

    print("----------")
    kucoin.get_part_order_book("BTC-GBP")
