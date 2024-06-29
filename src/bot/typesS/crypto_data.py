from typing import Any, Dict, List
from dataclasses import dataclass


@dataclass
class CryptoData:
    taapi_1h: List[Dict[str, Any]]
    taapi_1d: List[Dict[str, Any]]
    alternative_me: List[Dict[str, Any]]
    google_feed: List[Dict[str, Any]]
