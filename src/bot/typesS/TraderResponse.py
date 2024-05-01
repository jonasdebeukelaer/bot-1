class TraderResponse:
    def __init__(self, trading_decision: str, decision_rationale: str, data_requests: str, data_issues: str):
        self.trading_decision = int(trading_decision)
        self.decision_rationale = decision_rationale
        self.data_requests = data_requests
        self.data_issues = data_issues

    def get_trading_decision(self) -> int:
        return self.trading_decision
    
    def get_decision_rationale(self) -> str:
        return self.decision_rationale if self.decision_rationale else "-"

    def get_data_requests(self) -> str:
        return self.data_requests if self.data_requests else "-"

    def get_data_issues(self) -> str:
        return self.data_issues if self.data_issues else "-"

    def __str__(self) -> str:
        return f"TraderResponse(trading_decision={self.get_trading_decision()}, decision_rationale={self.get_decision_rationale()} data_requests={self.get_data_requests()}, data_issue_checker={self.get_data_issues()})"
