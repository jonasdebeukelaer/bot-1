from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class TraderResponse:
    trading_decision: int | str
    decision_rationale: str
    data_requests: str
    data_issues: str
    trade_ts: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def __post_init__(self):
        if not isinstance(self.trading_decision, int):
            self.trading_decision = int(self.trading_decision)
