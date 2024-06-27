import os
import time
from typing import Any, Dict, List

from kucoin.client import Trade, User, Market

from logger import logger
from util import five_sig_fig
from typess.PortfolioBreakdown import PortfolioBreakdown

SMALLEST_TRADE_SIZE_PERCENTAGE = 10
BTC_INCREMENT_DECIMAL = 4


class KucoinInterface:
    def __init__(self):
        api_key = os.environ.get("KUCOIN_API_KEY")
        if not api_key:
            raise EnvironmentError("The KUCOIN_API_KEY environment variable is not set.")
        api_secret = os.environ.get("KUCOIN_API_SECRET")
        if not api_secret:
            raise EnvironmentError("The KUCOIN_API_SECRET environment variable is not set.")
        api_passphrase = os.environ.get("KUCOIN_API_PASSPHRASE")
        if not api_passphrase:
            raise EnvironmentError("The KUCOIN_API_PASSPHRASE environment variable is not set.")
        url = os.environ.get("KUCOIN_URL")
        if not url:
            raise EnvironmentError("The KUCOIN_URL environment variable is not set.")

        self.trade_client = Trade(key=api_key, secret=api_secret, passphrase=api_passphrase, url=url)
        self.user_client = User(key=api_key, secret=api_secret, passphrase=api_passphrase, url=url)
        self.market_client = Market(key=api_key, secret=api_secret, passphrase=api_passphrase, url=url)

    def execute_trade(self, latest_bitcoin_price: float, bitcoin_holding_percentage_request: int) -> None:
        portfolio_breakdown = self.get_portfolio_breakdown()

        if bitcoin_holding_percentage_request < 0 or bitcoin_holding_percentage_request > 100:
            raise ValueError(f"Invalid percentage value '{bitcoin_holding_percentage_request}'")

        current_btc_percentage = portfolio_breakdown.get_btc_percentage(latest_bitcoin_price)
        difference = bitcoin_holding_percentage_request - current_btc_percentage

        # Check if trade size is too small to bother
        if abs(difference) < SMALLEST_TRADE_SIZE_PERCENTAGE:
            logger.log_info(
                "No trade wanted (porfolio change would be < 10%). Avoiding these small changes to save on fees."
            )
            return

        # Calculate trade size based on difference
        # For simplicity, let's assume trade size is proportional to the difference in percentages
        btc_in_gbp = portfolio_breakdown.get_btc_in_gbp(latest_bitcoin_price)
        trade_size_gbp = abs(btc_in_gbp * difference / 100)
        trade_size_btc = round(trade_size_gbp / latest_bitcoin_price, BTC_INCREMENT_DECIMAL)

        side = "buy" if difference > 0 else "sell"

        timestamp = str(time.time_ns())[:-5]
        trade_id = f"{timestamp}_{trade_size_btc}_{side}"

        try:
            # Execute trade
            logger.log_info(f"Executing trade: {trade_id}")
            self.trade_client.create_market_order(clientOid=trade_id, symbol="BTC-GBP", side=side, size=trade_size_btc)
        except Exception as e:
            if isinstance(e.args, tuple) and "200004" in e.args[0]:
                logger.log_error(
                    f"Insufficient funds in KuCoin to execute trade. Attempted with {trade_size_btc} BTC ({trade_size_gbp} GBP) at market price"
                )
            else:
                raise e

    def get_portfolio_breakdown(self) -> PortfolioBreakdown:
        data = self.user_client.get_account_list()

        if not isinstance(data, list):
            logger.log_error("Failed to get account list")
            return PortfolioBreakdown([])

        relevant_data = []
        for entry in data:
            if entry["currency"] not in ["GBP", "BTC"]:
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

        if not isinstance(data, dict):
            logger.log_error(f"Failed to get trades for {symbol}")
            return []

        formatted = []
        for item in data["items"]:
            ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(item["createdAt"] / 1000))
            formatted.append(f"{ts} {item['side']} {item['size']} {item['symbol']} at £{five_sig_fig(item['price'])}")

        logger.log_info(f"Last {limit} trades: {formatted}")
        return formatted

    def get_part_order_book(self, symbol: str = "BTC-GBP", pieces=20) -> Dict[str, Any]:
        data = self.market_client.get_part_order(symbol=symbol, pieces=pieces)

        if isinstance(data, dict):
            data["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(data["time"] / 1000))
            del data["time"], data["sequence"]

            logger.log_info(f"Order book for {symbol}: {data}")
            return data
        else:
            logger.log_error(f"Order book for {symbol} not found")
            return {}


# test
if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    kucoin = KucoinInterface()

    data = kucoin.get_portfolio_breakdown()
    print(data)

    data.get_btc_percentage(1000.0)
    kucoin.execute_trade(100.000, 10)

    print("----------")
    symbols = kucoin.market_client.get_symbol_list_v2()
    if isinstance(symbols, dict):
        for symbol in symbols:
            if symbol["symbol"] == "BTC-GBP":
                print(symbol)

    print("----------")
    trades = kucoin.get_last_trades("BTC-GBP")

    print("----------")
    kucoin.get_part_order_book("BTC-GBP")
