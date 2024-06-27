import os
from typing import Dict, Any
import requests


from ingestor_logger import ingestor_logger


class CryptoIndicators:
    def __init__(self, symbol: str = "BTC/GBP", exchange: str = "coinbase"):
        if not os.environ.get("TAAPI_API_KEY"):
            raise EnvironmentError("The TAAPI_API_KEY environment variable is not set.")

        self.taapi_api_key = os.environ.get("TAAPI_API_KEY")
        self.symbol = symbol
        self.exchange = exchange

    def get_taapi_indicators(self, interval: str) -> Dict[str, Any]:
        # Define the construct
        construct = {
            "exchange": self.exchange,
            "symbol": self.symbol,
            "interval": interval,
            "indicators": [
                {
                    "id": "candle",
                    "indicator": "candle",
                    "results": 1,
                    "addResultTimestamp": False,
                },
                {
                    "id": "price",
                    "indicator": "price",
                    "results": 1,
                },
                {
                    "id": "50EMA",
                    "indicator": "ema",
                    "period": 50,
                    "results": 1,
                    "addResultTimestamp": False,
                },
                {
                    "id": "200EMA",
                    "indicator": "ema",
                    "period": 200,
                    "results": 1,
                    "addResultTimestamp": False,
                },
                # { TODO: this is requiring too many candles to generate?
                # error: {"error":"Your request requires too many candles to complete.
                # We do not allow requests to be calculated with a larger candle set than 1000.
                # Your request requires 1400"}
                #     "id": "400EMA",
                #     "indicator": "ema",
                #     "period": 400,
                #     "results": 1,
                #     "addResultTimestamp": False,
                # },
                {
                    "id": "RSI",
                    "indicator": "rsi",
                    "period": 14,
                    "results": 1,
                    "addResultTimestamp": False,
                },
                {
                    "id": "MACD",
                    "indicator": "macd",
                    "exchange": "binance",
                    "results": 1,
                },
            ],
        }

        data = {"secret": self.taapi_api_key, "construct": construct}
        response = requests.post(
            "https://api.taapi.io/bulk",
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=60,
        )
        if response.status_code == 200:
            ts = None
            for indicator in response.json()["data"]:
                if indicator["id"] == "candle":
                    ts = indicator["result"]["timestampHuman"]
                    break
            # if ts missing fail here
            if ts is None:
                raise ValueError("Failed to get timestamp from TAAPI response.")

            return {"id": ts, "data": response.json()["data"]}

        else:
            ingestor_logger.info(response.text)
            response.raise_for_status()
            return {}  # TODO: why linter compains if not included?

    def get_alternative_me_indicators(self, result_count: int = 1) -> Dict[str, Any]:
        # note: the greed index is only updated once a day
        response = requests.get(
            "https://api.alternative.me/fng/",
            params={"limit": result_count, "date_format": "uk"},
            timeout=5,
        )
        resp = response.json()

        ts = resp["data"][0]["timestamp"]
        return {"id": ts, "data": resp["data"][0]}


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    crypto_indicators = CryptoIndicators()

    hourly_taapi_indicators = crypto_indicators.get_taapi_indicators(interval="1h")
    print("TAAPI Indicators:")
    print(hourly_taapi_indicators)

    daily_taapi_indicators = crypto_indicators.get_taapi_indicators(interval="1d")
    print("TAAPI Indicators daily:")
    print(daily_taapi_indicators)

    alternative_me_indicators = crypto_indicators.get_alternative_me_indicators()
    print("Alternative.me Indicators:")
    print(alternative_me_indicators)
