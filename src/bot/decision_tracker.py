import time

import gspread
from google.auth import default

from src.bot.logger import logger
from src.bot.typess.PortfolioBreakdown import PortfolioBreakdown
from src.bot.llm_trader import TraderResponse


class DecisionTracker:
    def __init__(self):
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds, _ = default(scopes=scopes)
        sheet_name = "bot-1_trade_history"

        self.client = gspread.authorize(creds)
        self.trades_sheet = self.client.open(sheet_name).sheet1
        self.portfolio_sheet = self.client.open(sheet_name).get_worksheet_by_id(1500161050)

    def record_trade_instructions(self, trade_resp: TraderResponse) -> None:
        dt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        try:
            trade_data = [
                dt,
                "GBP-BTC",
                "-",  # deprecated
                "-",  # deprecated
                "-",  # deprecated
                trade_resp.get_decision_rationale(),  # decision for the trade amount
                trade_resp.get_data_requests(),
                trade_resp.get_data_issues(),
                trade_resp.get_trading_decision(),
            ]
            self.trades_sheet.append_row(trade_data)

        except gspread.exceptions.APIError as e:
            logger.log_error(f"ERROR: failed to record trade data to Google Sheet (trade data: {trade_resp}). {e}")

        except ValueError as e:
            logger.log_error(f"ERROR: {e}")

    def record_portfolio(self, portfolio_breakdown: PortfolioBreakdown, latest_bitcoin_price: float) -> None:
        dt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        account_data = [
            dt,
            portfolio_breakdown.raw["GBP"],
            portfolio_breakdown.raw["BTC"],
            "-",
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
