import time

import gspread
from google.auth import default


class DecisionTracker:
    def __init__(self):
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds, _ = default(scopes=scopes)
        self.client = gspread.authorize(creds)
        self.sheet = self.client.open("bot-1_trade_history").sheet1

    def record(self, trade_data) -> None:
        try:
            dt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            self.sheet.append_row([dt] + trade_data)
        except Exception as e:
            print(f"Error recording trade data to Google Sheet (trade data: {trade_data}).")
            print(e.args)


if __name__ == "__main__":
    trade_data = ["GBP-BTC", 1.0, 2.00, "buy", "TEST"]
    dt = DecisionTracker()
    dt.record(trade_data)
