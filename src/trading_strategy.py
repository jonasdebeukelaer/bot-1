import logger

from kucoin_interface import KucoinInterface
from crypto_indicators import CryptoIndicators
from llm_market_monitor import MarketMonitor
from llm_trader import Trader
from decision_tracker import DecisionTracker


class TradingStrategy:
    def __init__(self, exchange_interface: KucoinInterface, crypto_indictators: CryptoIndicators):
        self.exchange_interface = exchange_interface
        self.crypto_indictators = crypto_indictators
        self.market_monitor = MarketMonitor()
        self.trader = Trader()
        self.decision_tracker = DecisionTracker()

    def execute(self):
        logger.reset_counter()

        logger.log("Starting new trading strategy execution...")

        logger.log("Getting portfolio breakdown...")
        portfolio_breakdown = self.exchange_interface.get_portfolio_breakdown()

        logger.log("Getting last trades...")
        last_trades = self.exchange_interface.get_last_trades()

        logger.log("Checking market...")
        latest_crypto_indicators = self.crypto_indictators.get_latest()
        answer = self.market_monitor.check_market(latest_crypto_indicators, portfolio_breakdown)

        log_msg = "Decided to call GPT4: {}. Reasoning: {}".format(answer["should_call"], answer["reasoning"])
        logger.log(log_msg)

        if answer["should_call"]:
            logger.log("Calling GPT4 for trading decision...")
            trading_instructions = self.trader.get_trading_instructions(
                self.crypto_indictators.indicator_history, portfolio_breakdown, last_trades
            )

            log_msg = "Made trade decision. Trade instructions: {}".format(trading_instructions)
            logger.log(log_msg)

            self.exchange_interface.execute_trade(
                trading_instructions["size"], trading_instructions["side"], trading_instructions["price"]
            )

            # TODO: Add reason to decision tracker
            # TODO: track all params of each trading round so easier to collect at the end
            self.decision_tracker.record(
                [
                    "GBP-BTC",
                    trading_instructions["size"],
                    trading_instructions["price"],
                    trading_instructions["side"],
                    "<reason>",
                ]
            )

            logger.log("Made trade.")
        else:
            self.decision_tracker.record(["", 0, 0, 0, "no trade requested"])

            logger.log("No trade requested.")

        logger.log("Finished execution\n")


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    ci = CryptoIndicators()
    ci.get_indicators()
    ts = TradingStrategy(KucoinInterface(), ci)
    ts.execute()
