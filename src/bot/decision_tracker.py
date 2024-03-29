import time
from typing import Dict, Any

import gspread
from google.auth import default

from logger import logger
from typess.PortfolioBreakdown import PortfolioBreakdown


class DecisionTracker:
    def __init__(self):
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds, _ = default(scopes=scopes)
        sheet_name = "bot-1_trade_history"

        self.client = gspread.authorize(creds)
        self.trades_sheet = self.client.open(sheet_name).sheet1
        self.portfolio_sheet = self.client.open(sheet_name).get_worksheet_by_id(1500161050)

    def record_trade_instructions(self, raw_trade_data: Dict[str, Any]) -> None:
        dt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        if type(raw_trade_data) is not dict:
            raise ValueError(f"raw_trade_data must be a dict, not {type(raw_trade_data)}")

        required_keys = ["bitcoin_percentage", "reasoning"]
        if not all(key in raw_trade_data for key in required_keys):
            raise ValueError(f"Missing one or more required keys in trade data: {required_keys}")

        try:
            trade_data = [
                dt,
                "GBP-BTC",
                "-",
                "-",
                "-",
                raw_trade_data["reasoning"],
                raw_trade_data["data_request"] if "data_request" in raw_trade_data else "-",
                raw_trade_data["data_issues"] if "data_issues" in raw_trade_data else "-",
                raw_trade_data["bitcoin_percentage"],
            ]
            self.trades_sheet.append_row(trade_data)

        except gspread.exceptions.APIError as e:
            logger.log_error(f"ERROR: failed to record trade data to Google Sheet (trade data: {raw_trade_data}). {e}")

        except ValueError as e:
            logger.log_error(f"ERROR: {e}")

    def record_portfolio(self, portfolio_breakdown: PortfolioBreakdown, latest_bitcoin_price: float) -> None:
        dt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        account_data = [
            dt,
            portfolio_breakdown.raw["GBP"],
            portfolio_breakdown.raw["BTC"],
            portfolio_breakdown.raw["USDT"],
            portfolio_breakdown.get_total_value_gbp(latest_bitcoin_price),
        ]

        try:
            self.portfolio_sheet.append_row(account_data)

        except gspread.exceptions.APIError as e:
            logger.log_error(
                f"ERROR: failed to record account data to Google Sheet (data: {portfolio_breakdown.raw}). {e}"
            )
        except ValueError as e:
            logger.log_error(f"ERROR: {e}")


if __name__ == "__main__":
    dt = DecisionTracker()

    trade_data = {
        "bitcoin_percentage": 0.00001,
        "reasoning": "TEST REASON",
        "data_request": "TEST DATA REQUEST",
        "data_issues": "TEST DATA ISSUES",
    }
    dt.record_trade_instructions(trade_data)

    raw_portfolio_data = PortfolioBreakdown(
        [
            {"currency": "GBP", "available": "1.62"},
            {"currency": "BTC", "available": "0.00000001"},
            {"currency": "USDT", "available": "0.00000002"},
            {"currency": "GBP", "available": "0"},  # included in response, but gets ignored in here
        ]
    )
    dt.record_portfolio(raw_portfolio_data, 1)
