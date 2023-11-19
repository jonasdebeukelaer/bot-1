import time
from typing import List

import gspread
from google.auth import default


class DecisionTracker:
    def __init__(self):
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds, _ = default(scopes=scopes)
        self.client = gspread.authorize(creds)
        self.trades_sheet = self.client.open("bot-1_trade_history").sheet1
        self.porfolio_sheet = self.client.open("bot-1_trade_history").get_worksheet_by_id(1500161050)

    def record_trade(self, trade_data: List) -> None:
        try:
            dt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            self.trades_sheet.append_row([dt] + trade_data)
        except Exception as e:
            print(f"Error recording trade data to Google Sheet (trade data: {trade_data}).")
            print(e.args)

    def record_porfolio(self, raw_account_data: List) -> None:
        try:
            dt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            account_data = [
                float(x["balance"])
                for x in raw_account_data
                if (float(x["balance"]) > 0 and x["currency"] in ["GBP", "BTC", "USDT"])
            ]
            self.porfolio_sheet.append_row([dt] + account_data)
        except Exception as e:
            print(f"Error recording account data to Google Sheet (account data: {account_data}).")
            print(e.args)


if __name__ == "__main__":
    dt = DecisionTracker()

    trade_data = ["GBP-BTC", 1.0, 2.00, "buy", "TEST"]
    dt.record_trade(trade_data)

    raw_porfolio_data = [
        {"currency": "GBP", "balance": "1.62"},
        {"currency": "BTC", "balance": "0.00000001"},
        {"currency": "USDT", "balance": "0.00000002"},
        {"currency": "GBP", "balance": "0"}, # included in response, but gets ignored in here
    ]
    dt.record_porfolio(raw_porfolio_data)
