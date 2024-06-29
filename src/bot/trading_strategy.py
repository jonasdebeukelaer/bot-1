from data_retriever import CryptoData
from typess.trader_input_data import TraderInputData
from logger import logger
from coinbase_interface import CoinbaseInterface
from llm_trader import Trader
from decision_tracker import DecisionTracker
from data_formatter import DataFormatter


class TradingStrategy:
    def __init__(self, exchange_interface: CoinbaseInterface, crypto_data: CryptoData):
        self.exchange_interface = exchange_interface
        self.crypto_data = crypto_data
        self.trader = Trader()
        self.decision_tracker = DecisionTracker()
        self.data_formatter = DataFormatter()

    def execute(self):
        logger.reset_counter()
        logger.log_info("Starting new trading strategy execution...")

        portfolio_breakdown = self.exchange_interface.get_portfolio_breakdown()
        latest_orders = self.exchange_interface.get_latest_orders()
        product_book = self.exchange_interface.get_product_book()
        formatted_indicators_hourly = self.data_formatter.format_hourly_data(self.crypto_data.taapi_1h)
        formatted_indicators_daily = self.data_formatter.format_daily_data(
            self.crypto_data.taapi_1d, self.crypto_data.alternative_me
        )
        formatted_news = self.data_formatter.format_news(self.crypto_data.google_feed)

        trading_input_data = TraderInputData(
            formatted_indicators_hourly,
            formatted_indicators_daily,
            portfolio_breakdown,
            latest_orders,
            product_book,
            formatted_news,
        )

        self._make_trade_decision(
            trading_input_data,
        )

        logger.log_info("Finished execution\n")

    def _make_trade_decision(
        self,
        trading_input_data: TraderInputData,
    ) -> None:
        logger.log_info("Calling LLM for trading decision...")

        trader_resp = self.trader(trading_input_data)

        log_msg = f"Received trade instructions: {str(trader_resp)}"
        logger.log_info(log_msg)

        self.decision_tracker.record_trade_instructions(trader_resp)

        self.exchange_interface.execute_trade(
            trading_input_data.portfolio_breakdown.bitcoin_price,
            trader_resp.trading_decision,
        )
        new_portfolio_breakdown = self.exchange_interface.get_portfolio_breakdown()
        self.decision_tracker.record_portfolio(new_portfolio_breakdown)
        logger.log_info("Trade request executed successfully.")
