from typing import Optional
from datetime import datetime

import dspy
from google.cloud import firestore

from logger import logger
from typess.crypto_data import CryptoData


class HistoricDataClient(dspy.Retrieve):
    def __init__(self, _url: str, _port: Optional[int] = None, k: int = 10):
        super().__init__(k=k)

        self.db = firestore.Client(database="crypto-bot")
        self.collections = {
            "indicators__taapi__1h": "taapi_1h",
            "indicators__taapi__1d": "taapi_1d",
            "indicators__alternative_me": "alternative_me",
            "news__google_feed": "google_feed",
        }

    # pylint: disable=arguments-differ
    def forward(self, query: datetime, k: Optional[int] = None) -> dspy.Prediction:
        limit = k if k is not None else self.k
        results = self._fetch_data(ts=query, limit=limit)

        return dspy.Prediction(crypto_data=CryptoData(**results))

    def _fetch_data(self, ts: datetime, limit: int) -> dict:
        results = {data_key: [] for data_key in self.collections.values()}

        for collection_name, data_key in self.collections.items():
            docs = (
                self.db.collection(collection_name)
                .where("extraction_timestamp", "<=", ts)
                .order_by("extraction_timestamp", direction=firestore.Query.ASCENDING)
                .limit(limit)
                .get()
            )

            for doc in docs:
                doc_dict = doc.to_dict()

                if doc_dict is None:
                    logger.log_info(f"WARNING Document {doc.id} is empty")
                    continue

                doc_dict["id"] = doc.id  # Include the document ID in the result

                # Convert any datetime objects to ISO format strings
                for key, value in doc_dict.items():
                    if isinstance(value, datetime):
                        doc_dict[key] = value.isoformat(timespec="seconds")
                results[data_key].append(doc_dict)

        return results


# Usage example:
if __name__ == "__main__":
    retriever = HistoricDataClient("no-url")

    latest_data = retriever.forward(datetime.now())
    print(latest_data)
