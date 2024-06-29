from dataclasses import dataclass
from typing import List, Dict, Any
from typess.portfolio_breakdown import PortfolioBreakdown


@dataclass
class TraderInputData:
    indicator_history_hourly: str
    indicator_history_daily: str
    portfolio_breakdown: PortfolioBreakdown
    last_orders: List[Dict[str, Any]]
    product_book: List[Dict[str, Any]]
    news: str
