import numpy as np
import pandas as pd

def calculate_EMA(data, window):
  # Use pandas to calculate EMA
  df = pd.DataFrame(data)
  ema = df.ewm(span=window).mean().values[-1]
  return ema

def calculate_RSI(data):
  # Calculate RSI using pandas
  df = pd.DataFrame(data)
  delta = df.diff()
  up, down = delta.copy(), delta.copy()
  up[up < 0] = 0
  down[down > 0] = 0

  average_gain = up.ewm(com=14, adjust=False).mean()
  average_loss = abs(down.ewm(com=14, adjust=False).mean())
  rs = average_gain / average_loss
  rsi = 100 - (100 / (1 + rs))
  
  return rsi.values[-1]

def calculate_Fear_Greed_Index(data):
  # Simple implementation, replace with actual calculation
  return np.random.randint(0, 100)