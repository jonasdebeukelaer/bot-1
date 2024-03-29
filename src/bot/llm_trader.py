import time
from typing import Dict, List, Any

from llm_interface import LLMInterface
from logger import logger
from typess.PortfolioBreakdown import PortfolioBreakdown


class Trader(LLMInterface):
    def __init__(self, model_name: str):
        super().__init__(model_name)
        self.previous_bitcoin_percentage: int = 0

    def get_trading_instructions(
        self,
        indicator_history_hourly: str,
        indicator_history_daily: str,
        portfolio_breakdown: PortfolioBreakdown,
        last_trades: List[str],
        order_book: Dict[str, Any],
        news: str,
    ) -> Dict[str, Any]:
        system_message = """
        You are an advanced swing trader with a medium-high risk appetite, trading Bitcoin. Your decisions are driven by a blend of technical analysis, market trends, and the latest news, with a strict policy against succumbing to FOMO and FUD. Decisions should be made as a percentage of portfolio to hold in bitcoin. The rest will be held as GBP. Your strategy involves capitalizing on short to medium-term fluctuations and managing risks by adjusting the position size according to the portfolio's current state and market conditions. Provide detailed reasoning for each decision, taking into account both the latest market indicators and news. Highlight any additional data you would find helpful or any issues with the current data set in the appropriate fields.
        """

        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        # TODO add trailing percentages
        #  Last 20 percentages of portfolio in Bitcoin: {portfolio_breakdown.get_percentage("BTC")}

        # TODO is portfolio breakdown useful?

        user_message = f"""
        Current time: {current_time}

        Portfolio breakdown: {portfolio_breakdown.get_formatted()}

        Last 20 trades within 7 days: {last_trades}

        Hourly price and indicators of Bitcoin: {indicator_history_hourly}

        Daily price and indicators of Bitcoin: {indicator_history_daily}

        Kucoin order book (20 entries): {order_book}

        Latest Bitcoin and cryptocurrency news: {news}

        Your current bitcoin holding percentage is: {self.previous_bitcoin_percentage}%

        Based on the information provided, recommend a good perentage of bitcoin to hold in our portfolio. Take into consideration that trading fees are 0.1% for both buying and selling, and the proportion of your portfolio which is already bitcoin.

        Analyze the latest market data, including price movements, indicators, and news, to make a trading decision. 
        Your decision should reflect a strategy that aligns with a medium-high risk appetite and leverages current market trends and technical analysis. 
        Provide the percentage of your porfolio you wish to be in bitcoin. 
        Include detailed reasoning for your decision, specifying how the data influenced your choice.
        Highlight any additional data that could improve decision-making or identify any perceived issues with the provided data in the 'data_request' and 'data_issues' return fields respectively.
        """

        logger.log_info("Message sent to LLM: " + user_message)

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ]

        function = {
            "name": "decide_portfolio_breakdown",
            "description": "expected return format",
            "parameters": {
                "type": "object",
                "properties": {
                    "bitcoin_percentage": {
                        "type": "number",
                        "description": "The percentage of the portfolio to hold in Bitcoin (0-100). The rest will be held as GBP.",
                    },
                    "reasoning": {
                        "type": "string",
                        "description": "A detailed explanation of the decision-making process, including the analysis of market data and how it fits with the trading strategy.",
                    },
                    "data_request": {
                        "type": "string",
                        "description": "Any additional information that would aid in making a more informed trading decision.",
                    },
                    "data_issues": {
                        "type": "string",
                        "description": "Any issues or inconsistencies noticed within the provided data set.",
                    },
                },
                "required": ["bitcoin_percentage", "reasoning", "data_request", "data_issues"],
            },
        }

        trading_instructions = self.send_messages(messages, function)

        # set previous bitcoin percentage for next call
        self.previous_bitcoin_percentage = trading_instructions["bitcoin_percentage"]

        return trading_instructions
