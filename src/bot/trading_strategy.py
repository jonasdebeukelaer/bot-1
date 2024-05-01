from typing import Any, Dict, List

from src.bot.typess.TraderInputData import TraderInputData
from src.bot.typess.PortfolioBreakdown import PortfolioBreakdown
from src.bot.logger import logger
from src.bot.kucoin_interface import KucoinInterface
from src.bot.crypto_indicators import CryptoIndicators
from src.bot.llm_trader import Trader
from src.bot.decision_tracker import DecisionTracker
from src.bot.news_extractor import NewsExtractor


class TradingStrategy:
    def __init__(
        self,
        exchange_interface: KucoinInterface,
        indicators_hourly: CryptoIndicators,
        indicators_daily: CryptoIndicators,
    ):
        self.exchange_interface = exchange_interface
        self.indicators_hourly = indicators_hourly
        self.indicators_daily = indicators_daily
        self.trader = Trader()
        self.decision_tracker = DecisionTracker()
        self.news_extractor = NewsExtractor()

    def execute(self):
        logger.reset_counter()

        logger.log_info("Starting new trading strategy execution...")

        logger.log_info("Getting portfolio breakdown...")
        portfolio_breakdown = self.exchange_interface.get_portfolio_breakdown()

        logger.log_info("Getting last trades...")
        last_trades = self.exchange_interface.get_last_trades()

        logger.log_info("Getting order book...")
        order_book = self.exchange_interface.get_part_order_book()

        logger.log_info("Getting latest news...")
        news = self.news_extractor.get_news()

        logger.log_info("Calling LLM for trade decision...")
        self._make_trade_decision(
            portfolio_breakdown,
            last_trades,
            order_book,
            news,
            self.indicators_hourly.get_latest_price(),
        )

        logger.log_info("Finished execution\n")

    def _make_trade_decision(
        self,
        portfolio_breakdown: PortfolioBreakdown,
        last_trades: List[str],
        order_book: Dict[str, Any],
        news: str,
        latest_bitcoin_price: float,
    ) -> None:
        logger.log_info("Calling LLM for trading decision...")

        trading_input_data = TraderInputData(
            self.indicators_hourly.get_formatted_indicator_history(),
            self.indicators_daily.get_formatted_indicator_history(),
            portfolio_breakdown,
            last_trades,
            order_book,
            news,
        )

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

    ci = CryptoIndicators()
    ci.fetch_indicators()

    ci_daily = CryptoIndicators(interval="1d")
    ci_daily.fetch_indicators()
    ts = TradingStrategy(KucoinInterface(), ci, ci_daily)
    ts.execute()
