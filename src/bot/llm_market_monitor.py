import os
import json
from typing import Dict, Any, List

import openai

from logger import logger


class MarketMonitor:
    def __init__(self):
        self.model_name = os.environ.get("OPENAI_MODEL_NAME", "gpt-3.5-turbo-1106")

        openai.api_key = os.environ.get("OPENAI_API_KEY")
        if openai.api_key is None:
            raise ValueError("OPENAI_API_KEY is not set in the environment variables")

    def check_market(self, latest_indicators: Dict[str, Any], portfolio_breakdown: List[Dict]) -> Dict[str, Any]:
        try:
            # Call GPT3 with indicators to decide if we should call GPT4
            resp = openai.ChatCompletion.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an advanced swing trader with a medium-high risk appetite. You've been trading Bitcoin and other cryptocurrencies, leveraging your expertise to capitalize on market trends while managing risks. Provide recommendations avoiding things like FOMO and FUD. You are requested to make a decision once an hour, so take this into account when making your decision.",
                    },
                    {"role": "system", "content": f"Your trading porfolio breakdown: {portfolio_breakdown}"},
                    {
                        "role": "system",
                        "content": "price and indicators of bitcoin" + str(latest_indicators),
                    },
                    {
                        "role": "user",
                        "content": "Given the price and indicators of bitcoin, should we call GPT4 to make a trade decision based off the latest price movement and indicators and their recent history? Answer this and provide a reason for your decision.",
                    },
                ],
                functions=[
                    {
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
                ],
                function_call={"name": "should_call_gpt4"},
            )

            response_arguments = json.loads(resp["choices"][0]["message"]["function_call"]["arguments"])
            if not isinstance(response_arguments, dict):
                raise TypeError("The response from OpenAI API is not in the expected format.")
            return response_arguments

        except KeyError as ke:
            logger.log_error(f"KeyError during OpenAI API response parsing: {ke}")
            raise
        except ValueError as ve:
            logger.log_error(f"ValueError during OpenAI API response parsing: {ve}")
            raise
        except openai.error.OpenAIError as oe:
            logger.log_error(f"OpenAIError during API call: {oe}")
            raise
        except Exception as e:
            logger.log_error(f"An unexpected error occurred during market check: {e}")
            raise
