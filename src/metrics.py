import requests

import pandas as pd


def calculate_EMA(price_df: pd.DataFrame, window: int) -> float:
    ema = price_df.ewm(span=window).mean().values[-1]
    return float(ema)


def calculate_RSI(price_df: pd.DataFrame) -> float:
    delta = price_df.diff()
    up, down = delta.copy(), delta.copy()
    up[up < 0] = 0
    down[down > 0] = 0

    average_gain = up.ewm(com=14, adjust=False).mean()
    average_loss = abs(down.ewm(com=14, adjust=False).mean())
    rs = average_gain / average_loss
    rsi = 100 - (100 / (1 + rs))

    return float(rsi.values[-1])


def calculate_Fear_Greed_Index() -> int:
    response = requests.get('https://api.alternative.me/fng/')
    data = response.json()

    value = data['data'][0]['value']

    return int(value)
