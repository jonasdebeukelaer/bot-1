import os
from venv import logger

from crypto_indicators import CryptoIndicators
from news_extractor import NewsExtractor
from logger import logger

from google.cloud import firestore
from dotenv import load_dotenv
import functions_framework
from flask import Request


@functions_framework.http
def function_entry_point(request: Request):
    _load_secrets()
    main()
    return "Data ingestion completed.", 200


def main():
    logger.info("Starting data ingestion...")

    logger.info("Initialising firestore connection...")
    db = firestore.Client(database="crypto-bot")

    logger.info("Initialising fetchers...")
    crypto_indicators = CryptoIndicators()
    news_extractor = NewsExtractor(limit=10)

    _fetch_and_store_taapi_data(db, crypto_indicators, interval="1h")
    _fetch_and_store_taapi_data(db, crypto_indicators, interval="1d")
    _fetch_and_store_alternative_me_data(db, crypto_indicators)
    _fetch_and_store_news(db, news_extractor)

    logger.info("Data ingestion completed.")


def _load_secrets():
    with open("/mnt2/secrets.env", "r") as src_file:
        with open(".env", "w") as dest_file:
            dest_file.write(src_file.read())

    load_dotenv()


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
    load_dotenv()
    main()
