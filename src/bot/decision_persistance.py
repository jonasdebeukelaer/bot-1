from logger import logger

from google.cloud import firestore

from typess.portfolio_breakdown import PortfolioBreakdown
from llm_trader import TraderResponse


class DecisionPersistance:
    def __init__(self):
        self.db = firestore.Client(database="crypto-bot")

        self.trades_collection = self.db.collection("trades")
        self.portfolio_collection = self.db.collection("portfolio")

    def store_llm_output(self, trade_resp: TraderResponse) -> None:
        try:
            trade_data = {
                "timestamp": trade_resp.trade_ts,
                "pair": "GBP-BTC",
                "decision_rationale": trade_resp.decision_rationale,
                "data_requests": trade_resp.data_requests,
                "data_issues": trade_resp.data_issues,
                "trading_decision": trade_resp.trading_decision,
            }

            self.trades_collection.add(trade_data)

        except Exception as e:
            logger.log_error(f"ERROR: failed to record trade data to Firestore (trade data: {trade_resp}). {e}")

    def store_portfolio(self, portfolio_breakdown: PortfolioBreakdown, trade_resp: TraderResponse) -> None:
        account_data = {
            "timestamp": trade_resp.trade_ts,
            "GBP": portfolio_breakdown.portfolio["GBP"],
            "BTC": portfolio_breakdown.portfolio["BTC"],
            "total_value_gbp": portfolio_breakdown.total_value_gbp,
            "btc_percentage": portfolio_breakdown.btc_percentage,
            "btc_price": portfolio_breakdown.bitcoin_price,
        }

        try:
            self.portfolio_collection.add(account_data)

        except Exception as e:
            logger.log_error(
                f"ERROR: failed to record account data to Firestore (data: {portfolio_breakdown.portfolio}). {e}"
            )
