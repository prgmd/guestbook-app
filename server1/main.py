import os
import json
import uuid
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

# SQLAlchemy 관련 임포트
from sqlalchemy import create_engine, Table, Column, String, MetaData, DateTime, Integer, JSON, Enum
from sqlalchemy.orm import sessionmaker

# --- FastAPI 앱 설정 ---
app = FastAPI()

# --- DB 설정 ---
MARIADB_URL = os.getenv("MARIADB_URL")
mariadb_engine = create_engine(MARIADB_URL)
metadata = MetaData()

# 비즈니스 데이터 테이블
entries_table = Table(
    "entries", metadata,
    Column("id", String(36), primary_key=True),
    Column("name", String(50)),
    Column("content", String(200)),
    Column("created_at", DateTime),
)
# 이벤트 저장을 위한 아웃박스 테이블
outbox_table = Table(
    "outbox", metadata,
    Column("event_id", Integer, primary_key=True, autoincrement=True),
    Column("topic", String(255), nullable=False),
    Column("payload", JSON, nullable=False),
    Column("status", Enum('new', 'processed'), default='new', nullable=False),
    Column("created_at", DateTime, default=datetime.now),
)
metadata.create_all(mariadb_engine) # 테이블이 없으면 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=mariadb_engine)

# --- Pydantic 모델 ---
class GuestbookEntryCreate(BaseModel):
    name: str
    content: str

# --- API 엔드포인트 ---

@app.post("/api/entries") # Nginx 경로에 맞춰 수정
def create_entry(entry: GuestbookEntryCreate):
    entry_id = str(uuid.uuid4())
    created_at = datetime.now()
    
    event_payload = {
        "type": "create",
        "payload": {
            "id": entry_id, "name": entry.name, "content": entry.content,
            "created_at": created_at.isoformat(),
        }
    }
    
    with SessionLocal() as session:
        # 1. entries 테이블에 데이터 저장
        session.execute(entries_table.insert().values(
            id=entry_id, name=entry.name, content=entry.content, created_at=created_at
        ))
        # 2. outbox 테이블에 이벤트 저장 (이것이 핵심!)
        session.execute(outbox_table.insert().values(
            topic="guestbook-events", payload=event_payload
        ))
        session.commit() # 두 작업이 하나의 트랜잭션으로 실행됨
        
    return {"message": "Entry submission received."}

@app.delete("/api/entries/{entry_id}") # Nginx 경로에 맞춰 수정
def delete_entry(entry_id: str):
    event_payload = { "type": "delete", "payload": {"id": entry_id} }
    with SessionLocal() as session:
        session.execute(entries_table.delete().where(entries_table.c.id == entry_id))
        session.execute(outbox_table.insert().values(
            topic="guestbook-events", payload=event_payload
        ))
        session.commit()
    return {"message": "Deletion request received."}