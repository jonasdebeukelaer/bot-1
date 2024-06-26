import os
import time

import dspy

from logger import logger
from typess.TraderInputData import TraderInputData
from typess.TraderResponse import TraderResponse


class TradeDecisionSig(dspy.Signature):
    """
    You are an advanced swing trader with a medium-high risk appetite, trading Bitcoin. Your decisions are driven by a blend of technical analysis, market trends, and the latest news, with a strict policy against succumbing to FOMO and FUD. Decisions should be made as a percentage of portfolio to hold in bitcoin. The rest will be held as GBP. Your strategy involves capitalizing on short to medium-term fluctuations and managing risks by adjusting the position size according to the provided context.

    Take into consideration that trading fees are 0.1% for both buying and selling, and the proportion of your portfolio which is already bitcoin.

    Question: What percentage of your porfolio you wish to be in bitcoin?
    """

    context = dspy.InputField()

    answer = dspy.OutputField(
        desc="A single number representing the percentage of your portfolio you wish to be in bitcoin. given as an int (between 0 and 100)."
    )


class DataRequestSig(dspy.Signature):
    """
    You are an advanced swing trader with a medium-high risk appetite, trading Bitcoin.

    Question: "What additional data that isn't included in the context which would be helpful for making trade decisions?"
    """

    context = dspy.InputField()

    answer = dspy.OutputField()


class DataQualityCheckSig(dspy.Signature):
    """
    You are a very good data error checker, use your knowledge of data and trading in general to answer the following question.

    Question: Are there any issues you can see in the data provided in the context?
    """

    context = dspy.InputField()

    answer = dspy.OutputField()


class Trader(dspy.Module):
    def __init__(self, trader_count: int = 2):
        super().__init__()

        if os.getenv("GROQ_API_KEY") is None:
            raise ValueError("GROQ_API_KEY is not set in the environment variables")

        if os.getenv("OPENAI_API_KEY") is None:
            raise ValueError("OPENAI_API_KEY is not set in the environment variables")

        self.llama = dspy.GROQ(model="llama3-70b-8192", max_tokens=500, api_key=os.getenv("GROQ_API_KEY", ""))
        self.gpt3_5 = dspy.OpenAI(model="gpt-3.5-turbo", api_key=os.getenv("OPENAI_API_KEY"))
        dspy.settings.configure(lm=self.llama)

        # TODO: play around with number of traders etc, possibly automate
        self.get_trade_decision = dspy.ChainOfThought(TradeDecisionSig)
        self.get_best_trade_decision = dspy.MultiChainComparison(TradeDecisionSig, M=trader_count, temperature=0.5)
        self.get_data_request = dspy.ChainOfThought(DataRequestSig)

        self.get_data_issue_checker = dspy.ChainOfThought(DataQualityCheckSig)

        # TODO move outside this class. Doesn't belong here
        self.previous_bitcoin_percentage: int = -1
        self.trader_count = trader_count

    def forward(self, trading_input_data: TraderInputData) -> TraderResponse:
        context = self.build_context(trading_input_data)

        trade_decisions = [self.get_trade_decision(context=context)]

        # to prevent request throtteling from Groq
        with dspy.context(lm=self.gpt3_5):
            trade_decisions.append(self.get_trade_decision(context=context))

        desired_bitcoin_percentage = self.get_best_trade_decision(trade_decisions, context=context)
        data_request_answer = self.get_data_request(context=context)

        # to prevent request throtteling from Groq
        with dspy.context(lm=self.gpt3_5):
            data_issue_checker_answer = self.get_data_issue_checker(context=context)

        # set previous bitcoin percentage for next call
        self.previous_bitcoin_percentage = desired_bitcoin_percentage

        return TraderResponse(
            desired_bitcoin_percentage.answer,
            desired_bitcoin_percentage.rationale,
            data_request_answer.answer,
            data_issue_checker_answer.answer,
        )

    def build_context(self, trading_input_data: TraderInputData) -> str:
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        context = f"""
        Current time: {current_time}

        Current portfolio breakdown: {trading_input_data.portfolio_breakdown.get_formatted()}

        Last 20 trades within 7 days: {trading_input_data.last_trades}

        Hourly price and indicators of Bitcoin: {trading_input_data.indicator_history_hourly}

        Daily price and indicators of Bitcoin: {trading_input_data.indicator_history_daily}

        Kucoin order book (20 entries): {trading_input_data.order_book}

        Latest Bitcoin and cryptocurrency news: {trading_input_data.news}

        Your current bitcoin holding percentage is: {self.previous_bitcoin_percentage if self.previous_bitcoin_percentage != 0 else 'unknown'}%
        """

        logger.log_info("Context to be sent to LLM: " + context)
        return context
