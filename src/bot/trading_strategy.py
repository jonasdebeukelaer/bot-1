from logger import logger
from kucoin_interface import KucoinInterface
from crypto_indicators import CryptoIndicators
from llm_market_monitor import MarketMonitor
from llm_trader import Trader
from decision_tracker import DecisionTracker


class TradingStrategy:
    def __init__(self, exchange_interface: KucoinInterface, crypto_indicators: CryptoIndicators):
        self.exchange_interface = exchange_interface
        self.crypto_indicators = crypto_indicators
        self.market_monitor = MarketMonitor()
        self.trader = Trader()
        self.decision_tracker = DecisionTracker()

    def execute(self):
        logger.reset_counter()

        logger.log_info("Starting new trading strategy execution...")

        logger.log_info("Getting portfolio breakdown...")
        portfolio_breakdown = self.exchange_interface.get_portfolio_breakdown()

        logger.log_info("Getting last trades...")
        last_trades = self.exchange_interface.get_last_trades()

        logger.log_info("Getting order book...")
        order_book = self.exchange_interface.get_part_order_book()

        logger.log_info("Checking market...")
        latest_crypto_indicators = self.crypto_indicators.get_latest()
        answer = self.market_monitor.check_market(latest_crypto_indicators, portfolio_breakdown)

        log_msg = "Decided to call GPT4: {}. Reasoning: {}".format(answer["should_call"], answer["reasoning"])
        logger.log_info(log_msg)

        if answer["should_call"]:
            logger.log_info("Calling GPT4 for trading decision...")
            trading_instructions = self.trader.get_trading_instructions(
                self.crypto_indicators.indicator_history, portfolio_breakdown, last_trades, order_book
            )

            log_msg = "Made trade decision. Trade instructions: {}".format(trading_instructions)
            logger.log_info(log_msg)

            self.exchange_interface.execute_trade(
                trading_instructions["size"], trading_instructions["side"], trading_instructions["price"]
            )

            # TODO: track all params of each trading round so easier to collect at the end
            self.decision_tracker.record_trade(trading_instructions)
            self.decision_tracker.record_porfolio(portfolio_breakdown)

            logger.log_info("Made trade.")
        else:
            self.decision_tracker.record_trade("no trade")

            logger.log_info("No trade requested.")

        logger.log_info("Finished execution\n")


if __name__ == "__main__":
    import logging 
    from dotenv import load_dotenv

    load_dotenv()
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

    ci = CryptoIndicators()
    ci.fetch_indicators()
    ts = TradingStrategy(KucoinInterface(), ci)
    ts.execute()
