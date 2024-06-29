from dataclasses import dataclass


@dataclass
class TraderResponse:
    trading_decision: int | str
    decision_rationale: str
    data_requests: str
    data_issues: str

    def __post_init__(self):
        if not isinstance(self.trading_decision, int):
            self.trading_decision = int(self.trading_decision)
