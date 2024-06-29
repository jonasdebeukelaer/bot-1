import os
import time
from typing import Any, Dict, List

from coinbase.rest import RESTClient

from logger import logger
from util import five_sig_fig
from typess.portfolio_breakdown import PortfolioBreakdown

SMALLEST_TRADE_SIZE_PERCENTAGE = 10
BTC_INCREMENT_DECIMAL = 4

PORTFOLIO_UUID = "476ae963-495c-4edd-8872-16fb0b54802d"


class CoinbaseInterface:
    def __init__(self):
        api_key = os.environ.get("COINBASE_API_KEY")
        if not api_key:
            raise EnvironmentError("The COINBASE_API_KEY environment variable is not set.")
        api_secret = os.environ.get("COINBASE_API_SECRET")
        if not api_secret:
            raise EnvironmentError("The COINBASE_API_SECRET environment variable is not set.")

        self.client = RESTClient(api_key=api_key, api_secret=api_secret)

    def execute_trade(self, latest_bitcoin_price: float, bitcoin_holding_percentage_request: int) -> None:
        portfolio_breakdown = self.get_portfolio_breakdown()

        if bitcoin_holding_percentage_request < 0 or bitcoin_holding_percentage_request > 100:
            raise ValueError(f"Invalid percentage value '{bitcoin_holding_percentage_request}'")

        # calculate trade size in btc
        current_btc_percentage = portfolio_breakdown.btc_percentage
        difference = bitcoin_holding_percentage_request - current_btc_percentage

        if abs(difference) < SMALLEST_TRADE_SIZE_PERCENTAGE:
            logger.log_info(
                "No trade wanted (portfolio change would be < 10%). Avoiding these small changes to save on fees."
            )
            return

        btc_in_gbp = portfolio_breakdown.btc_in_gbp
        trade_size_gbp = abs(btc_in_gbp * difference / 100)
        trade_size_btc = round(trade_size_gbp / latest_bitcoin_price, BTC_INCREMENT_DECIMAL)

        # calculate trade side
        side = "buy" if difference > 0 else "sell"

        # define order id
        timestamp = str(time.time_ns())[:-5]
        order_id = f"{timestamp}_{trade_size_btc}_{side}"

        try:
            logger.log_info(f"Executing trade: {trade_size_btc} BTC")

            if side == "buy":
                self.client.market_order_buy(
                    client_order_id=order_id,
                    product_id="BTC-GBP",
                    base_size=str(trade_size_btc),
                    retail_portfolio_id=PORTFOLIO_UUID,
                )

            else:
                self.client.market_order_sell(
                    client_order_id=order_id,
                    product_id="BTC-GBP",
                    base_size=str(trade_size_btc),
                )

        except Exception as e:
            logger.log_error(f"Error executing trade: {str(e)}")
            raise e

    def get_portfolio_breakdown(self) -> PortfolioBreakdown:
        logger.log_info("Getting portfolio breakdown...")
        accounts = self.client.get_accounts()

        succinct_porfolio = []
        for account in accounts["accounts"]:
            if account["currency"] in ["GBP", "BTC"]:
                succinct_porfolio.append(
                    {
                        "currency": account["available_balance"]["currency"],
                        "available_balance": five_sig_fig(account["available_balance"]["value"]),
                    }
                )

        bitcoin_price = self._get_product_price()

        portfolio = PortfolioBreakdown(succinct_porfolio, bitcoin_price)
        logger.log_info(f"Portfolio breakdown: {portfolio.formatted}")
        return portfolio

    def _get_product_price(self, product_id: str = "BTC-GBP") -> float:
        return float(self.client.get_product(product_id=product_id)["price"])

    def get_latest_orders(self, product_id="BTC-GBP", limit=10) -> List[Dict[str, Any]]:
        logger.log_info("Getting latest order...")

        # ordered by most recent first by default
        orders = self.client.list_orders(product_id=product_id, limit=limit, retail_portfolio_id=PORTFOLIO_UUID)[
            "orders"
        ]

        succinct_orders = []
        for order in orders:
            succinct_orders.append(
                {
                    "created_time": order["created_time"][:-8],
                    "side": order["side"],
                    "filled_size": five_sig_fig(order["filled_size"]),
                    "average_filled_price": five_sig_fig(order["average_filled_price"]),
                }
            )

        return succinct_orders

    def get_product_book(self, product_id: str = "BTC-GBP", limit=10) -> List[Dict[str, Any]]:
        logger.log_info("Getting product book...")
        return self.client.get_product_book(product_id=product_id, limit=limit)["pricebook"]["bids"]


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    coinbase_interface = CoinbaseInterface()

    bd = coinbase_interface.get_portfolio_breakdown()
    print("\nPortfolio breakdown:")
    print(bd.portfolio)

    last_trades = coinbase_interface.get_latest_orders()
    print("\nLast 20 trades:")
    print(last_trades)

    product_book = coinbase_interface.get_product_book()
    print("\nProduct book:")
    print(product_book)
