import time
from typing_extensions import deprecated

import gspread
from google.auth import default

from logger import logger
from typess.portfolio_breakdown import PortfolioBreakdown
from llm_trader import TraderResponse


@deprecated("In favour of decision_persistance.py")
class DecisionTracker:
    def __init__(self):
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds, _ = default(scopes=scopes)
        sheet_name = "bot-1_trade_history"

        self.client = gspread.authorize(creds)
        self.trades_sheet = self.client.open(sheet_name).sheet1
        self.portfolio_sheet = self.client.open(sheet_name).get_worksheet_by_id(1500161050)

    @deprecated("see class msg")
    def record_trade_instructions(self, trade_resp: TraderResponse) -> None:
        dt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        try:
            trade_data = [
                dt,
                "GBP-BTC",
                "-",  # deprecated
                "-",  # deprecated
                "-",  # deprecated
                trade_resp.decision_rationale,  # decision for the trade amount
                trade_resp.data_requests,
                trade_resp.data_issues,
                trade_resp.trading_decision,
            ]
            self.trades_sheet.append_row(trade_data)

        except gspread.exceptions.APIError as e:
            logger.log_error(f"ERROR: failed to record trade data to Google Sheet (trade data: {trade_resp}). {e}")

        except ValueError as e:
            logger.log_error(f"ERROR: {e}")

    @deprecated("see class msg")
    def record_portfolio(self, portfolio_breakdown: PortfolioBreakdown) -> None:
        dt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        account_data = [
            dt,
            portfolio_breakdown.portfolio["GBP"],
            portfolio_breakdown.portfolio["BTC"],
            "-",
            portfolio_breakdown.total_value_gbp,
        ]

        try:
            self.portfolio_sheet.append_row(account_data)

        except gspread.exceptions.APIError as e:
            logger.log_error(
                f"ERROR: failed to record account data to Google Sheet (data: {portfolio_breakdown.portfolio}). {e}"
            )
        except ValueError as e:
            logger.log_error(f"ERROR: {e}")
