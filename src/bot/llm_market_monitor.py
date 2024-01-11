from typing import Dict, Any

from llm_interface import LLMInterface
from kucoin_interface import PortfolioBreakdown


class MarketMonitor(LLMInterface):
    def check_market(
        self,
        latest_indicators_hourly: str,
        latest_indicators_daily: str,
        portfolio_breakdown: PortfolioBreakdown,
    ) -> Dict[str, Any]:
        messages = [
            {
                "role": "system",
                "content": "You are an advanced swing trader with a medium-high risk appetite. You've been trading Bitcoin and other cryptocurrencies, leveraging your expertise to capitalize on market trends while managing risks. Provide recommendations avoiding things like FOMO and FUD. You are requested to make a decision once an hour, so take this into account when making your decision.",
            },
            {
                "role": "user",
                "content": f"Your trading porfolio breakdown: {portfolio_breakdown.get_formatted()} \n\nhourly price and indicators of bitcoin: {latest_indicators_hourly} \n\ndaily price indicators of bitcoin: {latest_indicators_daily} \n\nGiven the price and indicators of bitcoin, should we call GPT4 to make a trade decision based off the latest price movement and indicators and their recent history? Consider that GPT4 costs are about $0.03 per request. Answer this and provide a reason for your decision.",
            },
        ]
        function = {
            "name": "should_call_gpt4",
            "description": "Decide if we should call GPT4 to make trade decision based off the latest price movement and indicators.",
            "parameters": {
                "type": "object",
                "properties": {
                    "should_call": {
                        "type": "boolean",
                    },
                    "reasoning": {
                        "type": "string",
                        "description": "The reasoning behind the decision.",
                    },
                    "data_request": {
                        "type": "string",
                        "description": "Specify any additional data which would help you make an optimal decision.",
                    },
                },
                "required": ["should_call", "reasoning"],
            },
        }

        return self.send_messages(messages, function)
