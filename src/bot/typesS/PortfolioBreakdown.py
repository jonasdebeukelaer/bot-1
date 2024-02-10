from typing import Dict, List


class PortfolioBreakdown:
    def __init__(self, raw: List[Dict]):
        # convert list to dict
        self.raw: Dict[str, float] = {entry["currency"]: float(entry["available"]) for entry in raw}

    def get_formatted(self) -> List[str]:
        return [f"{value} {key}" for key, value in self.raw.items()]

    def get_btc_percentage(self, latest_bitcoin_price: float) -> float:
        btc_amount = self.raw.get("BTC", 0)
        gbp_amount = self.raw.get("GBP", 0)

        gbp_to_btc = gbp_amount / latest_bitcoin_price
        total_portfolio_value_btc = btc_amount + gbp_to_btc

        return (btc_amount / total_portfolio_value_btc) * 100 if total_portfolio_value_btc != 0 else 0

    def get_btc_in_gbp(self, latest_bitcoin_price: float) -> float:
        btc_amount = self.raw.get("BTC", 0)

        return btc_amount * latest_bitcoin_price

    def get_total_value(self, latest_bitcoin_price: float) -> float:
        btc_amount = self.raw.get("BTC", 0)
        gbp_amount = self.raw.get("GBP", 0)

        btc_to_gbp = btc_amount * latest_bitcoin_price
        return gbp_amount + btc_to_gbp
