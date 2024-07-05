from datetime import timedelta

from data_retriever import CryptoData
from typess.prediction_input_data import PredictionInputData
from logger import logger
from coinbase_interface import CoinbaseInterface
from llm_trader import Trader
from llm_price_predictor import PricePredictor
from decision_persistance import DecisionPersistance
from data_formatter import DataFormatter


class TradingStrategy:
    def __init__(self, _coinbase_interface: CoinbaseInterface, crypto_data: CryptoData):
        self.crypto_data = crypto_data

        self.trader = Trader()
        self.price_predictor = PricePredictor()
        self.decision_persistance = DecisionPersistance()
        self.data_formatter = DataFormatter()

        self.target_timedelta = timedelta(hours=1)

    def execute(self):
        logger.log_info("Starting new trading strategy execution...")

        formatted_indicators_hourly = self.data_formatter.format_hourly_data(self.crypto_data.taapi_1h)
        formatted_indicators_daily = self.data_formatter.format_daily_data(
            self.crypto_data.taapi_1d, self.crypto_data.alternative_me
        )
        formatted_news = self.data_formatter.format_news(self.crypto_data.google_feed)

        price_prediction_input_data = PredictionInputData(
            self.crypto_data.latest_product_price,
            formatted_indicators_hourly,
            formatted_indicators_daily,
            formatted_news,
            self.target_timedelta,
        )

        price_prediction = self.price_predictor(price_prediction_input_data)

        prediction_record_data = dict(
            ts=price_prediction_input_data.ts_str,
            target_ts=price_prediction_input_data.target_ts_str,
            target_td=price_prediction_input_data.target_td_str,
            **price_prediction.toDict(),
        )

        self.decision_persistance.store_prediction_data(prediction_record_data)

        logger.log_info("Finished execution\n")
