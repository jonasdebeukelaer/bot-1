import os
import json
from typing import Dict, List, Any

import openai

from logger import log


class Trader:
    def __init__(self):
        self.model_name = os.environ.get("OPENAI_MODEL_NAME", "gpt-3.5-turbo-1106")

        openai.api_key = os.environ.get("OPENAI_API_KEY")
        if openai.api_key is None:
            raise ValueError("OPENAI_API_KEY is not set in the environment variables")

    def get_trading_instructions(
        self, latest_indicators: Dict[str, Any], portfolio_breakdown: List[Dict], last_trades: List[Dict]
    ) -> Dict[str, Any]:
        try:
            resp = openai.ChatCompletion.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an advanced swing trader with a medium-high risk appetite. You've been trading Bitcoin and other cryptocurrencies, leveraging your expertise to capitalize on market trends while managing risks. Provide recommendations avoiding things like FOMO and FUD. You are requested to make a decision once an hour, so take this into account when making your decision.",
                    },
                    {"role": "system", "content": f"Your trading porfolio breakdown: {portfolio_breakdown}"},
                    {"role": "system", "content": f"Your last 20 trades within the last 7 days: {last_trades}"},
                    {
                        "role": "system",
                        "content": "price and indicators of bitcoin" + str(latest_indicators),
                    },
                    {
                        "role": "user",
                        "content": "Given the price and indicators of bitcoin, what is your trading decision?",
                    },
                ],
                functions=[
                    {
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
                                    "description": "Specify any additional data which would help you make an optimal decision.",
                                },
                            },
                            "required": ["size", "price", "side", "reasoning"],
                        },
                    }
                ],
                function_call={"name": "decide_trade"},
            )

            response_arguments = json.loads(resp["choices"][0]["message"]["function_call"]["arguments"])
            if not isinstance(response_arguments, dict):
                raise TypeError("The response from OpenAI API is not in the expected format.")
            return response_arguments

        except KeyError as ke:
            log(f"KeyError during OpenAI API response parsing: {ke}")
            raise
        except ValueError as ve:
            log(f"ValueError during OpenAI API response parsing: {ve}")
            raise
        except openai.error.OpenAIError as oe:
            log(f"OpenAIError during API call: {oe}")
            raise
        except Exception as e:
            log(f"An unexpected error occurred during trading instructions retrieval: {e}")
            raise
