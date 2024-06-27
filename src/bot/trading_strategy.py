from data_retriever import CryptoData
from typess.TraderInputData import TraderInputData
from logger import logger
from kucoin_interface import KucoinInterface
from llm_trader import Trader
from decision_tracker import DecisionTracker
from data_formatter import DataFormatter


class TradingStrategy:
    def __init__(self, exchange_interface: KucoinInterface, crypto_data: CryptoData):
        self.exchange_interface = exchange_interface
        self.crypto_data = crypto_data
        self.trader = Trader()
        self.decision_tracker = DecisionTracker()
        self.data_formatter = DataFormatter()

    def execute(self):
        # TODO: simplify logger and tidy
        # TODO: split into smaller functions
        logger.reset_counter()

        logger.log_info("Starting new trading strategy execution...")

        logger.log_info("Getting portfolio breakdown...")
        portfolio_breakdown = self.exchange_interface.get_portfolio_breakdown()

        logger.log_info("Getting last trades...")
        last_trades = self.exchange_interface.get_last_trades()

        logger.log_info("Getting order book...")
        order_book = self.exchange_interface.get_part_order_book()

        logger.log_info("Format hourly indicators...")
        formatted_indicators_hourly = self.data_formatter.format_hourly_data(self.crypto_data.taapi_1h)

        logger.log_info("Format daily indicators...")
        formatted_indicators_daily = self.data_formatter.format_daily_data(
            self.crypto_data.taapi_1d, self.crypto_data.alternative_me
        )

        logger.log_info("Format latest news...")
        formatted_news = self.data_formatter.format_news(self.crypto_data.google_feed)

        trading_input_data = TraderInputData(
            formatted_indicators_hourly,
            formatted_indicators_daily,
            portfolio_breakdown,
            last_trades,
            order_book,
            formatted_news,
        )

        logger.log_info("Calling LLM for trade decision...")
        self._make_trade_decision(
            trading_input_data,
            self.crypto_data.taapi_1d[0]["data"][1]["result"]["value"][0],
        )

        logger.log_info("Finished execution\n")

    def _make_trade_decision(
        self,
        trading_input_data: TraderInputData,
        latest_bitcoin_price: float,
    ) -> None:
        logger.log_info("Calling LLM for trading decision...")

        trader_resp = self.trader(trading_input_data)

        log_msg = "Received trade instructions: {}".format(str(trader_resp))
        logger.log_info(log_msg)

        self.decision_tracker.record_trade_instructions(trader_resp)

        self.exchange_interface.execute_trade(
            latest_bitcoin_price,
            trader_resp.trading_decision,
        )
        new_portfolio_breakdown = self.exchange_interface.get_portfolio_breakdown()
        self.decision_tracker.record_portfolio(new_portfolio_breakdown, latest_bitcoin_price)
        logger.log_info("Trade request executed successfully.")


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    # ci = CryptoIndicators()
