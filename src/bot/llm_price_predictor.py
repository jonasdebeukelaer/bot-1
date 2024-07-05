# pylint: disable=line-too-long
# disable while prompts are long and manual

import os

import dspy

from logger import logger
from typess.prediction_input_data import PredictionInputData


class PricePredictor(dspy.Module):
    def __init__(self):
        super().__init__()

        if os.getenv("GROQ_API_KEY") is None:
            raise ValueError("GROQ_API_KEY is not set in the environment variables")

        if os.getenv("OPENAI_API_KEY") is None:
            raise ValueError("OPENAI_API_KEY is not set in the environment variables")

        self.llama = dspy.GROQ(model="llama3-70b-8192", max_tokens=500, api_key=os.getenv("GROQ_API_KEY", ""))
        self.gpt3_5 = dspy.OpenAI(model="gpt-3.5-turbo", api_key=os.getenv("OPENAI_API_KEY"))

        self.price_prediction = dspy.ChainOfThought(PricePredictionSig)
        self.data_request = dspy.ChainOfThought(DataRequestSig)
        self.data_issue_checker = dspy.ChainOfThought(DataQualityCheckSig)

    def forward(self, input_data: PredictionInputData) -> dspy.Prediction:
        context_str = self._build_context(input_data)

        with dspy.context(lm=self.llama):
            price_prediction = self.price_prediction(context=context_str, timestamp=input_data.target_ts_str)
            llm_data_requests = self.data_request(context=context_str)

        with dspy.context(lm=self.gpt3_5):
            llm_data_complaints = self.data_issue_checker(context=context_str)

        return dspy.Prediction(
            prediction_mean=price_prediction.mean,
            prediction_std_dev=price_prediction.std_dev,
            metadata=dict(
                llm_data_requests=llm_data_requests.answer,
                llm_data_complaints=llm_data_complaints.answer,
            ),
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

    mean = dspy.OutputField(desc="A single number representing the mean of your price prediction in GBP.")

    std_dev = dspy.OutputField(desc="A single number representing the standard deviation of your price prediction.")


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