import os
import json
from typing import Dict, List, Any

import openai


class Trader:
    def __init__(self):
        openai.api_key = os.environ.get("OPENAI_API_KEY")
        if openai.api_key is None:
            raise ValueError("OPENAI_API_KEY is not set in the environment variables")

    def get_trading_instructions(
        self, latest_indicators: Dict[str, Any], portfolio_breakdown: List[Dict], last_trades: List[Dict]
    ):
        try:
            resp = openai.ChatCompletion.create(
                model="gpt-4-1106-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an extremely savvy trader. You have been trading bitcoin for years and have made a lot of money. Provide recommendations avoiding things like FOMO and FUD.",
                    },
                    {"role": "system", "content": f"Your trading porfolio breakdown: {portfolio_breakdown}"},
                    {"role": "system", "content": f"Your last 20 trades within the last 7 days: {last_trades}"},
                    {
                        "role": "system",
                        "content": "price and indicators of bitcoin" + str(latest_indicators),
                    },
                    {
                        "role": "user",
                        "content": "Given the price and indicators of bitcoin, what is your trading decision",
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
                            },
                            "required": ["size", "price", "side", "reasoning"],
                        },
                    }
                ],
                function_call={"name": "decide_trade"},
            )

            return json.loads(resp["choices"][0]["message"]["function_call"]["arguments"])

        except KeyError as ke:
            print(f"KeyError: {ke}")
            raise

        except ValueError as ve:
            print(f"ValueError: {ve}")
            raise

        except openai.error.OpenAIError as oe:
            print(f"OpenAIError: {oe}")
            raise

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            raise
