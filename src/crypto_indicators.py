import os
import requests
from typing import Dict, Any
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

INSTANTANEOUS_RESULT_COUNT = 1
MAX_INDICTAOR_HISTORY = 20


class CryptoIndicators:
    def __init__(self, symbol: str = "BTC/USDT", exchange: str = "binance", interval: str = "4h"):
        self.taapi_api_key = os.environ.get("TAAPI_API_KEY")
        self.symbol = symbol
        self.exchange = exchange
        self.interval = interval

        self.indicator_history = []

    def get_taapi_indicators(self):
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
            print(response.text)
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

    def get_indicators(self) -> None:
        # Get taapi indicators
        taapi_results = self.get_taapi_indicators()

        # Parse and return the taapi_results
        indicators = {}
        for result in taapi_results:
            indicator_name = result["id"]

            # TODO: not working rn
            formatted_results = {}
            for key, value in result["result"].items():
                if (
                    isinstance(value, float)
                    or isinstance(value, int)
                    or (isinstance(value, str) and value.replace(".", "", 1).isdigit())
                ):
                    formatted_results[key] = f"{float(value):.5g}"
                else:
                    formatted_results[key] = value

            if "value" in result["result"]:
                indicator_value = formatted_results["value"]
            else:
                indicator_value = formatted_results
            indicators[indicator_name] = indicator_value

        # Get alternative.me indicators
        alternative_me_indicators = self.get_alternative_me_indicators()

        # Parse and return the alternative_me_results
        indicators.update(alternative_me_indicators)

        self.indicator_history.append(indicators)

        # if indictor history too long, remove the oldest entry
        if len(self.indicator_history) > MAX_INDICTAOR_HISTORY:
            self.indicator_history.pop(0)

    def get_latest(self) -> Dict[str, Any]:
        return self.indicator_history[-1]


if __name__ == "__main__":
    crypto_indicators = CryptoIndicators()
    indicators = crypto_indicators.get_indicators()
    print(indicators)
