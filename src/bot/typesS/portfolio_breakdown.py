from typing import Dict, List

from dataclasses import dataclass, field


@dataclass
class PortfolioBreakdown:
    raw_portfolio: List[Dict]
    portfolio: Dict[str, float] = field(init=False)
    bitcoin_price: float

    def __post_init__(self):
        self.portfolio = {entry["currency"]: float(entry["available_balance"]) for entry in self.raw_portfolio}
        if self.bitcoin_price <= 0:
            raise ValueError("Bitcoin price must be positive")

    def get_formatted(self) -> List[str]:
        return [f"{value} {key}" for key, value in self.portfolio.items()]

    def get_bitcoin_price(self) -> float:
        return self.bitcoin_price

    def get_btc_percentage(self) -> float:
        """Returns the percentage of the portfolio that is in BTC by value."""

        btc_amount = self.portfolio.get("BTC", 0)
        gbp_amount = self.portfolio.get("GBP", 0)

        gbp_to_btc = gbp_amount / self.bitcoin_price
        total_portfolio_value_btc = btc_amount + gbp_to_btc

        return (btc_amount / total_portfolio_value_btc) * 100 if total_portfolio_value_btc != 0 else 0

    def get_btc_in_gbp(self) -> float:
        """Returns the value of the BTC in GBP."""

        btc_amount = self.portfolio.get("BTC", 0)
        return btc_amount * self.bitcoin_price

    def get_total_value_gbp(self) -> float:
        """Returns the total value of the portfolio in GBP."""

        btc_amount = self.portfolio.get("BTC", 0)
        gbp_amount = self.portfolio.get("GBP", 0)

        btc_to_gbp = btc_amount * self.bitcoin_price
        return gbp_amount + btc_to_gbp
