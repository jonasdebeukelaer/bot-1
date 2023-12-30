import os
import requests
from collections import deque
from typing import Any, Dict

from logger import logger
from util import format_value

INSTANTANEOUS_RESULT_COUNT = 1  # adjust formatting before changing
MAX_INDICATOR_HISTORY = 20


class CryptoIndicators:
    def __init__(self, symbol: str = "BTC/GBP", exchange: str = "binance", interval: str = "1h"):
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
                    "id": "price",
                    "indicator": "price",
                    "results": INSTANTANEOUS_RESULT_COUNT,
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

    def get_latest(self) -> str:
        if self.indicator_history:
            return self.format_indicators(self.indicator_history[-1])
        else:
            return {}

    def formatted_indicator_history(self) -> str:
        formatted_history = ""
        for indicators in self.indicator_history:
            formatted_history += self.format_indicators(indicators) + "\n"
        return formatted_history

    def format_indicators(self, indicators: Dict[str, Any]) -> str:
        # TODO: consider more than one value per indicator
        # TODO: volume seems off?
        formatted_indicators = f"symbol: {self.symbol}, interval: {self.interval}, exchange: {self.exchange}\n\n"
        for indicator_name, indicator_value in indicators.items():
            if indicator_name == "candle":
                formatted_indicators += f"candle_timestamp: {indicator_value['timestampHuman']}, "
                formatted_indicators += f"candle_volume: {indicator_value['volume']}, "
                formatted_indicators += f"candle_high: {indicator_value['high']}, "
                formatted_indicators += f"candle_low: {indicator_value['low']}, "
                formatted_indicators += f"candle_open: {indicator_value['open']}, "
                formatted_indicators += f"candle_close: {indicator_value['close']}, "

            elif indicator_name == "MACD":
                formatted_indicators += f"MACD: {indicator_value['valueMACD'][0]}, "
                formatted_indicators += f"MACD_signal: {indicator_value['valueMACDSignal'][0]}, "
                formatted_indicators += f"MACD_hist: {indicator_value['valueMACDHist'][0]}, "
            elif indicator_name == "price":
                formatted_indicators += f"price: {indicator_value[0]}, "
            else:
                formatted_indicators += f"{indicator_name}: {indicator_value[0]}, "

        return formatted_indicators[:-2] + "\n\n"


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    crypto_indicators = CryptoIndicators()
    crypto_indicators.fetch_indicators()
    logger.log_info(f"Indicators: {crypto_indicators.get_latest()}")

    logger.log_info(f"Formatted indicator history: {crypto_indicators.formatted_indicator_history()}")
