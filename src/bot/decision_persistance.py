from logger import logger

from google.cloud import firestore

from typess.portfolio_breakdown import PortfolioBreakdown
from llm_trader import TraderResponse


class DecisionPersistance:
    def __init__(self):
        self.db = firestore.Client(database="crypto-bot")

        self.price_prediction_collection = self.db.collection("price_predictions")
        self.trades_collection = self.db.collection("trades")
        self.portfolio_collection = self.db.collection("portfolio")

    def store_prediction_data(self, record_data: dict) -> None:
        try:
            self.price_prediction_collection.document().set(record_data)
            logger.log_info("Prediction data persisted.")
        except Exception as e:
            logger.log_error(f"ERROR: failed to record trade data to Firestore (prediction data: {record_data}). {e}")

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

            self.trades_collection.document(trade_resp.trade_ts).set(trade_data)

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
            self.portfolio_collection.document(trade_resp.trade_ts).set(account_data)

        except Exception as e:
            logger.log_error(
                f"ERROR: failed to record account data to Firestore (data: {portfolio_breakdown.portfolio}). {e}"
            )
