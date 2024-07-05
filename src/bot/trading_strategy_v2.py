from datetime import datetime, timedelta

from logger import logger
from coinbase_interface import CoinbaseInterface
from llm_price_predictor import PricePredictor
from decision_persistance import DecisionPersistance


class TradingStrategy:
    def __init__(self, _coinbase_interface: CoinbaseInterface):

        self.target_timedelta = timedelta(hours=1)

        self.price_predictor = PricePredictor(self.target_timedelta)
        self.decision_persistance = DecisionPersistance()

    def execute(self):
        logger.log_info("Starting new trading strategy execution...")

        ts = datetime.now()

        price_prediction = self.price_predictor(ts)
        self.decision_persistance.store_prediction_data(price_prediction.toDict())

        logger.log_info("Finished execution\n")
