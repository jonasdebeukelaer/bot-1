import logger

from kucoin_interface import KucoinInterface
from crypto_indicators import CryptoIndicators
from llm_market_monitor import MarketMonitor
from llm_trader import Trader


class TradingStrategy:
    def __init__(self, exchange_interface: KucoinInterface, crypto_indictators: CryptoIndicators):
        self.exchange_interface = exchange_interface
        self.crypto_indictators = crypto_indictators
        self.market_monitor = MarketMonitor()
        self.trader = Trader()

    def execute(self):
        # Call GPT3 with indicators to decide if we should call GPT4
        answer = self.market_monitor.check_market(self.crypto_indictators.get_latest())

        log_msg = "Decided to call GPT4: {}. Reasoning: {}".format(answer["should_call"], answer["reasoning"])
        logger.log(log_msg)

        if answer["should_call"]:
            portfolio_breakdown = self.exchange_interface.get_portfolio_breakdown()
            trading_instructions = self.trader.get_trading_instructions(
                self.crypto_indictators.indicator_history, portfolio_breakdown
            )

            log_msg = "Made trade decision. Trade instructions: {}".format(trading_instructions)
            logger.log(log_msg)

            self.exchange_interface.execute_trade(
                trading_instructions["size"], trading_instructions["side"], trading_instructions["price"]
            )

            logger.log("Made trade.")
