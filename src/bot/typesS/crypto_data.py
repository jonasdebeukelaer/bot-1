from typing import Any, Dict, List
from dataclasses import dataclass


@dataclass
class CryptoData:
    taapi_1h: List[Dict[str, Any]]
    taapi_1d: List[Dict[str, Any]]
    alternative_me: List[Dict[str, Any]]
    google_feed: List[Dict[str, Any]]

    @property
    def latest_product_price(self) -> float:
        latest_taapi_data = self.taapi_1h[-1]["data"]
        price_data = latest_taapi_data[1]

        if price_data["id"] != "price":
            raise ValueError(f"Expected price data, but got {price_data['id']}")

        return price_data["result"]["value"][0]
