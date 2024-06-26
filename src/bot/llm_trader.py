# pylint: disable=line-too-long
# disable while prompts are long and manual

import os
import time

import dspy

from logger import logger
from typess.trader_input_data import TraderInputData
from typess.trader_response import TraderResponse


class TradeDecisionSig(dspy.Signature):
    """
    You are an advanced swing trader with a medium-high risk appetite, trading Bitcoin. Your decisions are driven by a blend of technical analysis, market trends, and the latest news, with a strict policy against succumbing to FOMO and FUD. Decisions should be made as a percentage of portfolio to hold in bitcoin. The rest will be held as GBP. Your strategy involves capitalizing on short to medium-term fluctuations and managing risks by adjusting the position size according to the provided context.

    Consider that trading fees are 0.6% for takers and 0.4% for makers, so avoid unecessary trades, by opting for slightly longer term strategies (days to weeks).

    Question: What percentage of your porfolio you wish to be in bitcoin?
    """

    context = dspy.InputField()

    answer = dspy.OutputField(
        desc="A single number representing the percentage of your portfolio you wish to be in bitcoin. given as an int (between 0 and 100)."
    )


class DataRequestSig(dspy.Signature):
    """
    You are an advanced swing trader with a medium-high risk appetite, trading Bitcoin. Be succinct in your answer.

    Question: "What additional data that isn't included in the context which would be helpful for making trade decisions?"
    """

    context = dspy.InputField()

    answer = dspy.OutputField()


class DataQualityCheckSig(dspy.Signature):
    """
    You are a highly skilled data error checker, use your knowledge of data and trading in general to answer the following question. Be succinct in your answer.

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

        self.get_trade_decision = dspy.ChainOfThought(TradeDecisionSig)
        self.get_best_trade_decision = dspy.MultiChainComparison(TradeDecisionSig, M=trader_count, temperature=0.5)
        self.get_data_request = dspy.ChainOfThought(DataRequestSig)

        self.get_data_issue_checker = dspy.ChainOfThought(DataQualityCheckSig)

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

        Current portfolio breakdown: {trading_input_data.portfolio_breakdown.formatted}

        Your current bitcoin holding percentage is: {trading_input_data.portfolio_breakdown.btc_percentage}%

        Last 10 orders you have made on Coinbase: {trading_input_data.last_orders}

        Hourly price and indicators of Bitcoin: {trading_input_data.indicator_history_hourly}

        Daily price and indicators of Bitcoin: {trading_input_data.indicator_history_daily}

        Latest Bitcoin and cryptocurrency news via google news feed: {trading_input_data.news}
        """

        logger.log_info("Context to be sent to LLM: " + context)
        return context
