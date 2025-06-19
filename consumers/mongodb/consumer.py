import os
import json
import time
from kafka import KafkaConsumer
from pymongo import MongoClient
from datetime import datetime

print("MongoDB Consumer is starting...")
time.sleep(10)

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
MONGO_URL = os.getenv("MONGO_URL")

mongo_client = MongoClient(MONGO_URL)
mongo_db = mongo_client.guestbook
collection = mongo_db.entries

consumer = KafkaConsumer(
    "guestbook-events",
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    auto_offset_reset='earliest',
    group_id='mongodb-group',
    value_deserializer=lambda v: json.loads(v.decode('utf-8'))
)

print("MongoDB Consumer is ready to consume messages.")

for message in consumer:
    event = message.value
    print(f"Received event in MongoDB Consumer: {event}")

    event_type = event.get("type")
    payload = event.get("payload")

    if event_type == "create":
        doc = {
            "_id": payload["id"],
            "name": payload["name"],
            "content": payload["content"],
            "created_at": datetime.fromisoformat(payload["created_at"])
        }
        collection.insert_one(doc)
        print(f"Inserted into MongoDB: {doc}")
    elif event_type == "delete":
        collection.delete_one({"_id": payload["id"]})
        print(f"Deleted from MongoDB: {payload['id']}")