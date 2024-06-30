# pylint: disable=invalid-name
import os
import datetime

from google.cloud import firestore


assert "GOOGLE_APPLICATION_CREDENTIALS" in os.environ, "Google Application Credentials not set."


# Initialize Firestore client
db = firestore.Client(database="crypto-bot")


def update_document_ids(collection_name):
    # Reference to the collection
    collection_ref = db.collection(collection_name)

    # Get all documents in the collection
    docs = collection_ref.get()

    for doc in docs:
        # Check if the current document ID is not a timestamp
        try:
            # Attempt to parse the document ID as a timestamp
            datetime.datetime.strptime(doc.id, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            # If parsing fails, it's not a timestamp ID
            # Get the timestamp from the document
            timestamp = doc.get("timestamp")

            if timestamp:
                # Create a new document with the timestamp as ID
                new_doc_ref = collection_ref.document(timestamp)

                # Copy all fields from the old document to the new one
                new_doc_ref.set(doc.to_dict())

                # Delete the old document
                doc.reference.delete()

                print(f"Updated document in {collection_name}: Old ID: {doc.id}, New ID: {timestamp}")
            else:
                print(f"Document in {collection_name} with ID {doc.id} has no timestamp field")


# Update both collections
update_document_ids("portfolio")
update_document_ids("trades")

print("Document ID update process completed.")

# export GOOGLE_APPLICATION_CREDENTIALS=""
