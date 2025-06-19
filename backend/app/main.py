import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import List

# SQLAlchemy (MariaDB) 관련 임포트
from sqlalchemy import create_engine, text, Table, Column, Integer, String, MetaData, DateTime

# PyMongo (MongoDB) 관련 임포트
from pymongo import MongoClient

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

# --- 데이터베이스 연결 설정 ---
# Docker Compose에서 설정한 환경변수 가져오기
MARIADB_URL = os.getenv("MARIADB_URL")
MONGO_URL = os.getenv("MONGO_URL")

# MariaDB (SQLAlchemy) 연결
mariadb_engine = create_engine(MARIADB_URL)
metadata = MetaData()
# 'entries' 테이블 스키마 정의
entries_table = Table(
    "entries",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String(50)),
    Column("content", String(200)),
    Column("created_at", DateTime, default=datetime.now),
)

# MongoDB (PyMongo) 연결
mongo_client = MongoClient(MONGO_URL)
mongo_db = mongo_client.guestbook
mongo_collection = mongo_db.entries

# --- FastAPI 시작 시 DB 테이블 생성 ---
@app.on_event("startup")
def on_startup():
    # MariaDB에 'entries' 테이블이 없으면 생성
    with mariadb_engine.connect() as connection:
        metadata.create_all(connection, checkfirst=True)
    print("Database tables checked/created.")

# --- Pydantic 모델 정의 ---
class GuestbookEntryCreate(BaseModel):
    name: str
    content: str

class GuestbookEntry(GuestbookEntryCreate):
    id: int
    created_at: str

# --- API 엔드포인트 ---

# 모든 방명록 글 가져오기 (GET) - MariaDB에서 조회
@app.get("/api/entries", response_model=List[GuestbookEntry])
def get_entries():
    with mariadb_engine.connect() as connection:
        query = entries_table.select().order_by(entries_table.c.id.desc())
        result = connection.execute(query)
        entries = result.fetchall()
        # SQLAlchemy Result 객체를 Pydantic 모델과 호환되는 dict 리스트로 변환
        return [
            {
                "id": entry.id,
                "name": entry.name,
                "content": entry.content,
                "created_at": entry.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for entry in entries
        ]

# 새 방명록 글 추가하기 (POST) - MariaDB와 MongoDB에 동시 저장
@app.post("/api/entries", response_model=GuestbookEntry)
def create_entry(entry: GuestbookEntryCreate):
    created_time = datetime.now()
    
    # 1. MariaDB에 저장하고 새로 생성된 ID를 가져옴
    with mariadb_engine.connect() as connection:
        query = entries_table.insert().values(
            name=entry.name,
            content=entry.content,
            created_at=created_time
        )
        result = connection.execute(query)
        connection.commit()
        new_id = result.lastrowid # 방금 삽입된 행의 id

    if new_id is None:
        raise HTTPException(status_code=500, detail="Failed to create entry in MariaDB")

    # 2. MariaDB의 ID를 포함하여 MongoDB에 저장
    mongo_doc = {
        "_id": new_id,  # MariaDB의 ID를 MongoDB의 _id로 사용
        "name": entry.name,
        "content": entry.content,
        "created_at": created_time,
    }
    mongo_collection.insert_one(mongo_doc)

    return GuestbookEntry(
        id=new_id,
        name=entry.name,
        content=entry.content,
        created_at=created_time.strftime("%Y-%m-%d %H:%M:%S"),
    )

# 방명록 글 삭제하기 (DELETE) - MariaDB와 MongoDB에서 동시 삭제
@app.delete("/api/entries/{entry_id}", status_code=200)
def delete_entry(entry_id: int):
    # 1. MariaDB에서 삭제
    with mariadb_engine.connect() as connection:
        query = entries_table.delete().where(entries_table.c.id == entry_id)
        result = connection.execute(query)
        connection.commit()
        # 삭제된 행이 없으면 404 에러 발생
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Entry not found in MariaDB")

    # 2. MongoDB에서 삭제
    mongo_collection.delete_one({"_id": entry_id})
    
    return {"message": "Entry deleted successfully"}