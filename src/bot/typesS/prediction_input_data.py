from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass
class PredictionInputData:
    product_price: float
    indicator_history_hourly: str
    indicator_history_daily: str
    news: str
    target_timedelta: timedelta
    ts: datetime = field(default_factory=datetime.now)
    ts_str: str = field(init=False)
    target_ts_str: str = field(init=False)
    target_td_str: str = field(init=False)

    def __post_init__(self):
        if not isinstance(self.target_timedelta, timedelta):
            raise ValueError(f"Target timedelta must be a datetime.timedelta object, got {type(self.target_timedelta)}")

        if not isinstance(self.ts, datetime):
            raise ValueError(f"Timestamp must be a datetime object, got {type(self.ts)}")

        self.ts_str = self.ts.strftime("%Y-%m-%d %H:%M:%S")
        self.target_ts_str = (self.ts + self.target_timedelta).strftime("%Y-%m-%d %H:%M:%S")
        self.target_td_str = str(self.target_timedelta)
