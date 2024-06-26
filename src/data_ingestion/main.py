from venv import logger

from src.data_ingestion.crypto_indicators import CryptoIndicators
from src.data_ingestion.news_extractor import NewsExtractor
from src.data_ingestion.logger import logger

from google.cloud import firestore
from dotenv import load_dotenv

load_dotenv()


def main():
    db = firestore.Client(database="crypto-bot")

    logger.info("Fetching and storing data...")
    crypto_indicators = CryptoIndicators()
    news_extractor = NewsExtractor(limit=10)

    _fetch_and_store_taapi_data(db, crypto_indicators, interval="1h")
    _fetch_and_store_taapi_data(db, crypto_indicators, interval="1d")
    _fetch_and_store_alternative_me_data(db, crypto_indicators)
    _fetch_and_store_news(db, news_extractor)


def _fetch_and_store_taapi_data(db, crypto_indicators, interval):
    logger.info(f"Fetching and storing TAAPI ({interval})...")
    taapi_indicators = crypto_indicators.get_taapi_indicators(interval=interval)
    doc_ref = db.collection(f"indicators__taapi__{interval}").document(taapi_indicators["id"])
    doc_ref.set({"data": taapi_indicators["data"]})
    logger.info("Done")


def _fetch_and_store_alternative_me_data(db, crypto_indicators):
    logger.info("Fetching and storing Alternative.me...")
    alternative_me_indicators = crypto_indicators.get_alternative_me_indicators()
    doc_ref = db.collection("indicators__alternative_me").document(alternative_me_indicators["id"])
    doc_ref.set({"data": alternative_me_indicators["data"]})
    logger.info("Done")


def _fetch_and_store_news(db, news_extractor):
    logger.info("Fetching and storing news...")
    latest_news = news_extractor.get_news()
    for news_item in latest_news:
        doc_ref = db.collection("news__google_feed").document(news_item["published"])
        doc_ref.set({"data": news_item})

    logger.info("Done")


if __name__ == "__main__":
    logger.info("Starting data ingestion...")
    main()
    logger.info("Data ingestion completed.")
