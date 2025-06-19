import os
import json
import time
from kafka import KafkaConsumer
from sqlalchemy import create_engine, text, Table, Column, String, MetaData, DateTime
from datetime import datetime
    
print("MariaDB Consumer is starting...")
time.sleep(10) # Kafka와 DB가 완전히 시작될 때까지 잠시 대기

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
MARIADB_URL = os.getenv("MARIADB_URL")

engine = create_engine(MARIADB_URL)
metadata = MetaData()
entries_table = Table(
    "entries",
    metadata,
    Column("id", String(36), primary_key=True),
    Column("name", String(50)),
    Column("content", String(200)),
    Column("created_at", DateTime),
)
# 테이블이 없으면 생성
with engine.connect() as connection:
    metadata.create_all(connection, checkfirst=True)

consumer = KafkaConsumer(
    "guestbook-events",
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    auto_offset_reset='earliest',
    group_id='mariadb-group',
    value_deserializer=lambda v: json.loads(v.decode('utf-8'))
)

print("MariaDB Consumer is ready to consume messages.")

for message in consumer:
    event = message.value
    print(f"Received event in MariaDB Consumer: {event}")

    event_type = event.get("type")
    payload = event.get("payload")

    with engine.connect() as connection:
        if event_type == "create":
            query = entries_table.insert().values(
                id=payload["id"],
                name=payload["name"],
                content=payload["content"],
                created_at=datetime.fromisoformat(payload["created_at"])
            )
            print(f"Inserting into MariaDB: {payload}")
        elif event_type == "delete":
            query = entries_table.delete().where(entries_table.c.id == payload["id"])
            print(f"Deleting from MariaDB: {payload['id']}")

        connection.execute(query)
        connection.commit()