import os
import requests
from collections import deque
from typing import Any, Dict

from logger import logger
from util import format_value

MAX_INDICATOR_HISTORY = 10


class CryptoIndicators:
    def __init__(self, symbol: str = "BTC/GBP", exchange: str = "coinbase", interval: str = "1h"):
        if not os.environ.get("TAAPI_API_KEY"):
            raise EnvironmentError("The TAAPI_API_KEY environment variable is not set.")

        self.taapi_api_key = os.environ.get("TAAPI_API_KEY")
        self.symbol = symbol
        self.exchange = exchange
        self.interval = interval

        self.indicator_history = deque([], maxlen=MAX_INDICATOR_HISTORY)
        # self._backfill_indicator_history()

    def fetch_indicators(self) -> None:
        taapi_results = self._get_taapi_indicators()

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

        # Get alternative.me indicators, only if interval is 1d since fear/greed
        # index is only updated once a day
        if self.interval == "1d":
            alternative_me_indicators = self._get_alternative_me_indicators()
            indicators.update(alternative_me_indicators)

        self.indicator_history.append(indicators)

    def get_formatted_latest_indicator_set(self) -> str:
        if self.indicator_history:
            formatted_latest_indicator_set = self._format_indicator_set(self.indicator_history[-1])
            formatted_message = f"symbol: {self.symbol}, interval: {self.interval}, exchange: {self.exchange}\n{formatted_latest_indicator_set}"
            return formatted_message
        else:
            return {}

    def get_formatted_indicator_history(self) -> str:
        formatted_history = ""
        for indicators in self.indicator_history:
            formatted_history += self._format_indicator_set(indicators) + "\n"
        
        formatted_message = f"symbol: {self.symbol}, interval: {self.interval}, exchange: {self.exchange}\n{formatted_history}"
        return formatted_message

    # TODO: implement
    def backfill_indicator_history(self) -> None:
        taapi_results = self._get_taapi_indicators()

        # Parse and return the taapi_results
        indicator_history = {}

        # # Get alternative.me indicators, only if interval is 1d since fear/greed
        # # index is only updated once a day
        # if self.interval == "1d":
        #     alternative_me_indicators = self._get_alternative_me_indicators()
        #     indicators.update(alternative_me_indicators)

        # for result in taapi_results:
        #     indicator_name = result["id"]

        #     formatted_results = {}
        #     for key, value in result["result"].items():
        #         if isinstance(value, list):
        #             formatted_results[key] = [format_value(v) for v in value]
        #         else:
        #             formatted_results[key] = format_value(value)

        #     if "value" in formatted_results:
        #         indicator_value = formatted_results["value"]
        #     else:
        #         indicator_value = formatted_results
        #     indicators[indicator_name] = indicator_value

        self.indicator_history.appendleft(indicator_history)

    def _get_taapi_indicators(self, result_count: int = 1) -> Any:
        # Define the construct
        construct = {
            "exchange": self.exchange,
            "symbol": self.symbol,
            "interval": self.interval,
            "indicators": [
                {
                    "id": "candle",
                    "indicator": "candle",
                    "results": result_count,
                    "addResultTimestamp": False,
                },
                {
                    "id": "price",
                    "indicator": "price",
                    "results": result_count,
                },
                {
                    "id": "50EMA",
                    "indicator": "ema",
                    "period": 50,
                    "results": result_count,
                    "addResultTimestamp": False,
                },
                {
                    "id": "200EMA",
                    "indicator": "ema",
                    "period": 200,
                    "results": result_count,
                    "addResultTimestamp": False,
                },
                {
                    "id": "800EMA",
                    "indicator": "ema",
                    "period": 800,
                    "results": result_count,
                    "addResultTimestamp": False,
                },
                {
                    "id": "RSI",
                    "indicator": "rsi",
                    "period": 14,
                    "results": result_count,
                    "addResultTimestamp": False,
                },
                {
                    "id": "MACD",
                    "indicator": "macd",
                    "exchange": "binance",
                    "results": result_count,
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

    def _get_alternative_me_indicators(self, result_count: int = 1):
        # note: the greed index is only updated once a day
        response = requests.get(
            "https://api.alternative.me/fng/",
            params={"limit": result_count, "date_format": "uk"},
        )
        data = response.json()

        # collect the fear/greed index values
        values = []
        for result in data["data"]:
            values.append(int(result["value"]))

        # TODO: take into account timestamps

        return {"fear/greed index": values}

    def _format_indicator_set(self, indicators: Dict[str, Any]) -> str:
        # TODO: consider more than one value per indicator
        # TODO: volume seems off?
        formatted_indicators = ""
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

        return formatted_indicators[:-2]


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    hourly_crypto_indicators = CryptoIndicators()
    hourly_crypto_indicators.fetch_indicators()
    hourly_crypto_indicators.fetch_indicators()

    logger.log_info(f"Indicators: {hourly_crypto_indicators.get_formatted_latest_indicator_set()}")

    logger.log_info(f"Formatted indicator history: {hourly_crypto_indicators.get_formatted_indicator_history()}")

    daily_crypto_indicators = CryptoIndicators(interval="1d")
    daily_crypto_indicators.fetch_indicators()

    # also contains fear/greed index
    logger.log_info(f"Indicators: {daily_crypto_indicators.get_formatted_latest_indicator_set()}")
