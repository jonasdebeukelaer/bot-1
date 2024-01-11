from typing import Dict, List, Any

from llm_interface import LLMInterface
from logger import logger


class Trader(LLMInterface):
    def get_trading_instructions(
        self,
        indicator_history_hourly: str,
        indicator_history_daily: str,
        portfolio_breakdown: List[Dict],
        last_trades: List[str],
        order_book: Dict[str, Any],
    ) -> Dict[str, Any]:
        system_message = "You are an advanced swing trader with a medium-high risk appetite. You've been trading Bitcoin and other cryptocurrencies, leveraging your expertise to capitalize on market trends while managing risks. Provide recommendations avoiding things like FOMO and FUD. You are requested to make a decision once an hour, so take this into account when making your decision. Make sure to think step by stepin the reasoning property before making a decision."

        user_message = f"Your trading porfolio breakdown: {portfolio_breakdown} \n\n Your last 20 trades within the last 7 days: {last_trades} \n\nhourly price and indicators of bitcoin: {indicator_history_hourly} \n\ndaily price and indicators of bitcoin: {indicator_history_daily} \n\nkucoin order book (20 pieces): {order_book} \n\nGiven your portfolio, the price and indicators history of bitcoin provided and your last trades, what is your trading decision?"

        logger.log_info("Message sent to LLM: " + user_message)

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ]

        function = {
            "name": "decide_trade",
            "description": "Analyze the latest price movement and indicators to make a trading decision. Include the price, amount and side you would like to trade.",
            "parameters": {
                "type": "object",
                "properties": {
                    "size": {
                        "type": "number",
                        "description": "The size of the trading order. Set to 0 if you do not want to make any trade.",
                    },
                    "price": {
                        "type": "number",
                        "description": "The price of bitcoin at which to make the trade (price increment is 0.0001).",
                    },
                    "side": {
                        "type": "string",
                        "enum": ["buy", "sell"],
                        "description": "The side on which to make the order.",
                    },
                    "reasoning": {
                        "type": "string",
                        "description": "The reasoning behind the trading decision.",
                    },
                    "data_request": {
                        "type": "string",
                        "description": "Specify any additional data which would have helped you make a better decision.",
                    },
                    "data_issues": {
                        "type": "string",
                        "description": "Specify any issues you noticed in the data provided.",
                    }
                },
                "required": ["size", "price", "side", "reasoning"],
            },
        }

        return self.send_messages(messages, function)
