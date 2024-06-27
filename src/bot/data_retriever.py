from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime

from google.cloud import firestore
from google.cloud.firestore_v1.field_path import FieldPath

from logger import logger


@dataclass
class CryptoData:
    taapi_1h: List[Dict[str, Any]]
    taapi_1d: List[Dict[str, Any]]
    alternative_me: List[Dict[str, Any]]
    google_feed: List[Dict[str, Any]]


class DataRetriever:
    def __init__(self):
        self.db = firestore.Client(database="crypto-bot")
        self.collections = {
            "indicators__taapi__1h": "taapi_1h",
            "indicators__taapi__1d": "taapi_1d",
            "indicators__alternative_me": "alternative_me",
            "news__google_feed": "google_feed",
        }

    def get_latest(self, limit: int = 10) -> CryptoData:
        result = {"taapi_1h": [], "taapi_1d": [], "alternative_me": [], "google_feed": []}

        for collection_name, data_key in self.collections.items():
            docs = (
                self.db.collection(collection_name)
                .order_by(FieldPath.document_id(), direction=firestore.Query.DESCENDING)
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
                        doc_dict[key] = value.isoformat()
                result[data_key].append(doc_dict)

        return CryptoData(**result)


# Usage example:
if __name__ == "__main__":
    retriever = DataRetriever()

    # Get latest 10 entries for each collection
    latest_data = retriever.get_latest()
    print(latest_data)
