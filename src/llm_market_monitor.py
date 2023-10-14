import os
import json
from typing import Dict, Any

import openai


class MarketMonitor:
    def __init__(self):
        openai.api_key = os.environ.get("OPENAI_API_KEY")
        if openai.api_key is None:
            raise ValueError("OPENAI_API_KEY is not set in the environment variables")

    def check_market(self, latest_indicators: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # Call GPT3 with indicators to decide if we should call GPT4
            resp = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an extremely savvy trader. You have been trading bitcoin for years and have made a lot of money. Provide recommendations avoiding things like FOMO and FUD.",
                    },
                    {
                        "role": "system",
                        "content": "price and indicators of bitcoin" + str(latest_indicators),
                    },
                    {
                        "role": "user",
                        "content": "Given the price and indicators of bitcoin, should we call GPT4 to make a trade decision based off the latest price movement and indicators? Answer this and provide a reason for your decision.",
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
                            },
                            "required": ["should_call", "reasoning"],
                        },
                    }
                ],
                function_call={"name": "should_call_gpt4"},
            )

            return json.loads(resp["choices"][0]["message"]["function_call"]["arguments"])

        except KeyError as ke:
            print(f"KeyError: {ke}")
            # Handle KeyError, maybe log it and/or re-raise as a more specific exception
            raise

        except ValueError as ve:
            print(f"ValueError: {ve}")
            # Handle ValueError, maybe log it and/or re-raise as a more specific exception
            raise

        except openai.error.OpenAIError as oe:
            print(f"OpenAIError: {oe}")
            # Handle OpenAI API-related errors
            # Log it and/or re-raise as needed
            raise

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            # Handle other types of exceptions
            # Log it and/or re-raise as needed
            raise
