import os
import json
import time
from kafka import KafkaConsumer
from pymongo import MongoClient
from datetime import datetime

print("MongoDB Consumer (Query Service) is starting...")
time.sleep(15) 

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
MONGO_URL = os.getenv("MONGO_URL")

# Kafka Consumer 연결
while True:
    try:
        consumer = KafkaConsumer(
            "guestbook-events",
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            auto_offset_reset='earliest',
            group_id='mongodb-query-group-v2',
            value_deserializer=lambda v: v.decode('utf-8') # <--- 중요! 일단 바이트를 문자열로만 변환
        )
        print("MongoDB Consumer connected to Kafka with new group ID.")
        break
    except Exception as e:
        print(f"Failed to connect to Kafka, retrying in 5 seconds... Error: {e}")
        time.sleep(5)

mongo_client = MongoClient(MONGO_URL)
mongo_db = mongo_client.guestbook
collection = mongo_db.entries
print("MongoDB Consumer connected to MongoDB.")

print("MongoDB Consumer is ready to process messages.")
for message in consumer:
    try:
        # --- 여기가 핵심 수정 부분 ---
        # 1. 받은 메시지(문자열)를 딕셔너리로 변환
        event_data = json.loads(message.value)

        # 2. 혹시 데이터가 이중으로 싸여 문자열일 경우, 한 번 더 변환
        if isinstance(event_data, str):
            event = json.loads(event_data)
        else:
            event = event_data
        # --- 여기까지 핵심 수정 부분 ---

        print(f"Received and parsed event in MongoDB Consumer: {event}")
        event_type = event.get("type")
        payload = event.get("payload")

        if event_type == "create":
            payload["created_at"] = datetime.fromisoformat(payload["created_at"])
            doc = {"_id": payload.pop("id"), **payload}
            
            collection.replace_one({"_id": doc["_id"]}, doc, upsert=True)
            print(f"Upserted document in MongoDB with _id: {doc['_id']}")

        elif event_type == "delete":
            collection.delete_one({"_id": payload["id"]})
            print(f"Deleted document from MongoDB with _id: {payload['id']}")
            
    except json.JSONDecodeError:
        print(f"Could not decode JSON from message: {message.value}")
    except Exception as e:
        print(f"Failed to process message: {message.value}. Error: {e}")