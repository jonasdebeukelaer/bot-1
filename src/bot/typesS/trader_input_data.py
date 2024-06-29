from typing import List, Dict, Any

from typess.portfolio_breakdown import PortfolioBreakdown


class TraderInputData:
    def __init__(
        self,
        indicator_history_hourly: str,
        indicator_history_daily: str,
        portfolio_breakdown: PortfolioBreakdown,
        last_orders: List[Dict[str, Any]],
        product_book: List[Dict[str, Any]],
        news: str,
    ):
        self.indicator_history_hourly = indicator_history_hourly
        self.indicator_history_daily = indicator_history_daily
        self.portfolio_breakdown = portfolio_breakdown
        self.last_orders = last_orders
        self.product_book = product_book
        self.news = news

    def get_indicator_history_hourly(self):
        return self.indicator_history_hourly

    def get_indicator_history_daily(self):
        return self.indicator_history_daily

    def get_portfolio_breakdown(self):
        return self.portfolio_breakdown

    def get_last_orders(self):
        return self.last_orders

    def get_product_book(self):
        return self.product_book

    def get_news(self):
        return self.news

    def __str__(self):
        return f"TradingInputData(indicator_history_hourly={self.indicator_history_hourly}, indicator_history_daily={self.indicator_history_daily}, portfolio_breakdown={self.portfolio_breakdown}, last_orders={self.last_orders}, product_book={self.product_book}, news={self.news})"

    def __repr__(self):
        return self.__str__()
