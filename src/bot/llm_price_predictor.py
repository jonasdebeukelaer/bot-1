# pylint: disable=line-too-long
# disable while prompts are long and manual

import os
from datetime import datetime, timedelta

import dspy

from data_formatter import DataFormatter
from logger import logger
from retrievers.historic_data_retriever import HistoricDataClient
from typess.prediction_input_data import PredictionInputData
from typess.crypto_data import CryptoData


class PricePredictor(dspy.Module):
    def __init__(self, target_td: timedelta):
        super().__init__()

        if os.getenv("GROQ_API_KEY") is None:
            raise ValueError("GROQ_API_KEY is not set in the environment variables")

        if os.getenv("OPENAI_API_KEY") is None:
            raise ValueError("OPENAI_API_KEY is not set in the environment variables")

        self.llama = dspy.GROQ(model="llama3-70b-8192", max_tokens=500, api_key=os.getenv("GROQ_API_KEY", ""))
        self.gpt3_5 = dspy.OpenAI(model="gpt-3.5-turbo", api_key=os.getenv("OPENAI_API_KEY"))

        self.data_retriever = HistoricDataClient("-")

        self.data_formatter = DataFormatter()

        self.price_prediction = dspy.ChainOfThought(PricePredictionSig)
        self.data_request = dspy.ChainOfThought(DataRequestSig)
        self.data_issue_checker = dspy.ChainOfThought(DataQualityCheckSig)

        self.target_td = target_td

    def forward(self, ts: datetime) -> dspy.Prediction:
        retrieved_data: dspy.Prediction = self.data_retriever(query=ts)

        input_data = self._build_input_data(retrieved_data.crypto_data)
        context_str = self._build_context(input_data)

        with dspy.context(lm=self.llama):
            price_prediction = self.price_prediction(context=context_str, timestamp=input_data.target_ts_str)
            llm_data_requests = self.data_request(context=context_str)

        with dspy.context(lm=self.gpt3_5):
            llm_data_complaints = self.data_issue_checker(context=context_str)

        return dspy.Prediction(
            ts=input_data.ts_str,
            target_ts=input_data.target_ts_str,
            target_td=input_data.target_td_str,
            prediction_mean=price_prediction.mean,
            prediction_std_dev=price_prediction.std_dev,
            metadata=dict(
                llm_data_requests=llm_data_requests.answer,
                llm_data_complaints=llm_data_complaints.answer,
            ),
        )

    def _build_input_data(self, crypto_data: CryptoData) -> PredictionInputData:
        return PredictionInputData(
            crypto_data.latest_product_price,
            self.data_formatter.format_hourly_data(crypto_data.taapi_1h),
            self.data_formatter.format_daily_data(crypto_data.taapi_1d, crypto_data.alternative_me),
            self.data_formatter.format_news(crypto_data.google_feed),
            self.target_td,
        )

    def _build_context(self, input_data: PredictionInputData) -> str:
        context = f"""
        Current time: {input_data.ts.strftime("%Y-%m-%d %H:%M:%S")}

        Hourly price and indicators of Bitcoin: {input_data.indicator_history_hourly}

        Daily price and indicators of Bitcoin: {input_data.indicator_history_daily}

        Latest Bitcoin and cryptocurrency news via google news feed: {input_data.news}

        Current bitcoin price: £{str(input_data.product_price)}
        """

        logger.log_info("Context to be sent to LLM: " + context)
        return context


class PricePredictionSig(dspy.Signature):
    """
    You are an advanced swing trader with a medium-high risk appetite, trading Bitcoin.
    Your decisions are driven by a blend of technical analysis, market trends, and the latest news, with a strict policy against succumbing to FOMO and FUD.

    Make a prediction for the price of bitcoin in GBP for the given target timestamp.
    Provide this as a probability distribution, giving a mean and a standard deviation.
    """

    context = dspy.InputField()

    timestamp = dspy.InputField(desc="The timestamp for which you are predicting the price of Bitcoin.")

    mean = dspy.OutputField(desc="Mean GBP price prediction, as a float.")

    std_dev = dspy.OutputField(desc="Standard deviation of the GBP price prediction, as a float.")


class DataRequestSig(dspy.Signature):
    """
    You are an advanced swing trader with a medium-high risk appetite, trading Bitcoin.
    Your decisions are driven by a blend of technical analysis, market trends, and the latest news, with a strict policy against succumbing to FOMO and FUD.

    Question: What additional data that isn't included in the context which would be helpful for making trade decisions?
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
