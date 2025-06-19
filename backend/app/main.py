import os
import json
import uuid
import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import List

from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
from sqlalchemy import create_engine, text, Table, Column, String, MetaData, DateTime

# --- FastAPI 앱 및 CORS 설정 ---
app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 설정값 및 전역 변수 ---
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
MARIADB_URL = os.getenv("MARIADB_URL")

# Producer는 시작 시점에 연결하므로 초기에는 None으로 설정
producer = None

# MariaDB 연결 (GET 요청 처리를 위해 필요)
mariadb_engine = create_engine(MARIADB_URL)
metadata = MetaData()
entries_table = Table(
    "entries",
    metadata,
    Column("id", String(36), primary_key=True),
    Column("name", String(50)),
    Column("content", String(200)),
    Column("created_at", DateTime),
)

# --- FastAPI 시작 이벤트 ---
@app.on_event("startup")
def startup_event():
    global producer
    retry_count = 0
    max_retries = 5
    while retry_count < max_retries:
        try:
            print(f"Connecting to Kafka (Attempt {retry_count + 1}/{max_retries})...")
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            print("Kafka Producer connected successfully.")
            break  # 연결 성공 시 루프 탈출
        except NoBrokersAvailable:
            retry_count += 1
            print(f"Failed to connect to Kafka. Retrying in 5 seconds...")
            time.sleep(5)
    
    if producer is None:
        print("Could not connect to Kafka after multiple retries. The application might not work as expected.")

# --- Pydantic 모델 ---
class GuestbookEntryCreate(BaseModel):
    name: str
    content: str

class GuestbookEntry(GuestbookEntryCreate):
    id: str
    created_at: str

# --- API 엔드포인트 ---

# 글 목록 조회 (GET)
@app.get("/api/entries", response_model=List[GuestbookEntry])
def get_entries():
    # ... (이전 코드와 동일)
    with mariadb_engine.connect() as connection:
        query = entries_table.select().order_by(entries_table.c.created_at.desc())
        result = connection.execute(query)
        entries = result.fetchall()
        return [
            {
                "id": entry.id,
                "name": entry.name,
                "content": entry.content,
                "created_at": entry.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for entry in entries
        ]

# 새 글 작성 (POST)
@app.post("/api/entries")
def create_entry(entry: GuestbookEntryCreate):
    if producer is None:
        raise HTTPException(status_code=503, detail="Kafka producer is not available.")
    
    entry_id = str(uuid.uuid4())
    created_at = datetime.now().isoformat()
    
    message = {
        "type": "create",
        "payload": {
            "id": entry_id,
            "name": entry.name,
            "content": entry.content,
            "created_at": created_at,
        }
    }
    
    producer.send("guestbook-events", value=message)
    producer.flush()
    
    return {"message": "Entry submission received. It will appear shortly."}

# 글 삭제 (DELETE)
@app.delete("/api/entries/{entry_id}")
def delete_entry(entry_id: str):
    if producer is None:
        raise HTTPException(status_code=503, detail="Kafka producer is not available.")
        
    message = {
        "type": "delete",
        "payload": {
            "id": entry_id
        }
    }
    
    producer.send("guestbook-events", value=message)
    producer.flush()

    return {"message": "Deletion request received. The entry will be removed shortly."}