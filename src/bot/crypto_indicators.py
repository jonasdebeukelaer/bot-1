import os
import requests
from collections import deque
from typing import Any, Dict

from logger import logger
from util import format_value

INSTANTANEOUS_RESULT_COUNT = 1
MAX_INDICATOR_HISTORY = 20


class CryptoIndicators:
    def __init__(self, symbol: str = "BTC/USDT", exchange: str = "binance", interval: str = "4h"):
        if not os.environ.get("TAAPI_API_KEY"):
            raise EnvironmentError("The TAAPI_API_KEY environment variable is not set.")

        self.taapi_api_key = os.environ.get("TAAPI_API_KEY")
        self.symbol = symbol
        self.exchange = exchange
        self.interval = interval

        self.indicator_history = deque([], maxlen=MAX_INDICATOR_HISTORY)

    def get_taapi_indicators(self) -> Any:
        # Define the construct
        construct = {
            "exchange": self.exchange,
            "symbol": self.symbol,
            "interval": self.interval,
            "indicators": [
                {
                    "id": "candle",
                    "indicator": "candle",
                    "results": INSTANTANEOUS_RESULT_COUNT,
                    "addResultTimestamp": False,
                },
                {
                    "id": "50EMA",
                    "indicator": "ema",
                    "period": 50,
                    "results": INSTANTANEOUS_RESULT_COUNT,
                    "addResultTimestamp": False,
                },
                {
                    "id": "200EMA",
                    "indicator": "ema",
                    "period": 200,
                    "results": INSTANTANEOUS_RESULT_COUNT,
                    "addResultTimestamp": False,
                },
                {
                    "id": "800EMA",
                    "indicator": "ema",
                    "period": 800,
                    "results": INSTANTANEOUS_RESULT_COUNT,
                    "addResultTimestamp": False,
                },
                {
                    "id": "RSI",
                    "indicator": "rsi",
                    "period": 14,
                    "results": INSTANTANEOUS_RESULT_COUNT,
                    "addResultTimestamp": False,
                },
                {
                    "id": "MACD",
                    "indicator": "macd",
                    "exchange": "binance",
                    "results": INSTANTANEOUS_RESULT_COUNT,
                },
            ],
        }

        data = {"secret": self.taapi_api_key, "construct": construct}
        response = requests.post(
            "https://api.taapi.io/bulk",
            json=data,
            headers={"Content-Type": "application/json"},
        )
        if response.status_code == 200:
            return response.json()["data"]
        else:
            logger.log_info(response.text)
            response.raise_for_status()

    def get_alternative_me_indicators(self):
        response = requests.get(
            "https://api.alternative.me/fng/",
            params={"limit": INSTANTANEOUS_RESULT_COUNT, "date_format": "uk"},
        )
        data = response.json()

        # collect the fear/greed index values
        values = []
        for result in data["data"]:
            values.append(int(result["value"]))

        # TODO: take into account timestamps

        return {"fear/greed index": values}

    def fetch_indicators(self) -> None:
        taapi_results = self.get_taapi_indicators()

        # Parse and return the taapi_results
        indicators = {}
        for result in taapi_results:
            indicator_name = result["id"]

            formatted_results = {}
            for key, value in result["result"].items():
                if isinstance(value, list):
                    formatted_results[key] = [format_value(v) for v in value]
                else:
                    formatted_results[key] = format_value(value)

            if "value" in formatted_results:
                indicator_value = formatted_results["value"]
            else:
                indicator_value = formatted_results
            indicators[indicator_name] = indicator_value

        # Get alternative.me indicators
        alternative_me_indicators = self.get_alternative_me_indicators()

        # Parse and return the alternative_me_results
        indicators.update(alternative_me_indicators)

        self.indicator_history.append(indicators)

    def get_latest(self) -> Dict[str, Any]:
        if self.indicator_history:
            return self.indicator_history[-1]
        else:
            return {}


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    crypto_indicators = CryptoIndicators()
    crypto_indicators.fetch_indicators()
    logger.log_info(f"Indicators: {crypto_indicators.get_latest()}")
