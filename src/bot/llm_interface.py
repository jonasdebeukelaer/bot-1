import os
import json
from typing import List, Dict, Any

import openai
import litellm

from logger import logger

litellm.add_function_to_prompt = True


class LLMInterface:
    def __init__(self, model_name: str):
        self.model_name = model_name

        if os.environ.get("OPENAI_API_KEY") is None:
            raise ValueError("OPENAI_API_KEY is not set in the environment variables")

    def send_messages(self, messages: List[Dict], tool: Dict) -> Dict[str, Any]:
        logger.log_debug(f"Sending messages to OpenAI API: {messages}")
        try:
            resp = litellm.completion(
                model=self.model_name,
                messages=messages,
                tools=[tool],
                tool_choice={"type": "function", "function": {"name": tool["function"]["name"]}},
            )

            response_arguments = json.loads(resp["choices"][0]["message"]["tool_calls"][0].function.arguments)
            if not isinstance(response_arguments, dict):
                raise TypeError("The response from OpenAI API is not in the expected format.")
            return response_arguments

        except KeyError as ke:
            logger.log_error(f"KeyError during LLM response parsing: {ke} \nRaw response: {resp}")
            raise
        except ValueError as ve:
            logger.log_error(f"ValueError during LLM response parsing: {ve} \nRaw response: {resp}")
            raise
        except openai.OpenAIError as oe:
            logger.log_error(f"OpenAIError during LLM API call: {oe} \nRaw response: {resp}")
            raise
        except Exception as e:
            logger.log_error(
                f"An unexpected error occurred during trading instructions retrieval: {e} \nRaw response: {resp}"
            )
            raise
