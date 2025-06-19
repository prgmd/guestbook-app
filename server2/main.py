import os
from fastapi import FastAPI
from typing import List
from pydantic import BaseModel
from pymongo import MongoClient

app = FastAPI()

MONGO_URL = os.getenv("MONGO_URL")
mongo_client = MongoClient(MONGO_URL)
db = mongo_client.guestbook
collection = db.entries

class GuestbookEntry(BaseModel):
    id: str
    name: str
    content: str
    created_at: str

@app.get("/api/entries", response_model=List[GuestbookEntry])
def get_entries():
    # MongoDB에서 데이터를 조회. 최신순으로 정렬
    entries_cursor = collection.find().sort("created_at", -1)
    
    # MongoDB의 BSON 형식을 Pydantic 모델과 호환되도록 변환
    result = []
    for entry in entries_cursor:
        result.append({
            "id": entry["_id"],
            "name": entry["name"],
            "content": entry["content"],
            "created_at": entry["created_at"].strftime("%Y-%m-%d %H:%M:%S")
        })
    return result