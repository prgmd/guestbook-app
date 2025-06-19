from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import List

# FastAPI 앱 생성
app = FastAPI()

# CORS 설정: 모든 출처에서의 요청을 허용합니다.
# 실제 프로덕션 환경에서는 '*' 대신 프론트엔드 주소를 명시하는 것이 안전합니다.
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 데이터베이스 대신 사용할 인메모리 리스트
# { "id": 1, "name": "이름", "content": "내용", "created_at": "2025-06-18 11:30:00" }
db = []

# Pydantic 모델 정의 (데이터 유효성 검사)
class GuestbookEntryCreate(BaseModel):
    name: str
    content: str

class GuestbookEntry(GuestbookEntryCreate):
    id: int
    created_at: str

# 루트 엔드포인트
@app.get("/")
def read_root():
    return {"message": "Guestbook API is running"}

# 모든 방명록 글 가져오기 (GET)
@app.get("/api/entries", response_model=List[GuestbookEntry])
def get_entries():
    # 최신 글이 위로 오도록 정렬하여 반환
    return sorted(db, key=lambda x: x['id'], reverse=True)

# 새 방명록 글 추가하기 (POST)
@app.post("/api/entries", response_model=GuestbookEntry)
def create_entry(entry: GuestbookEntryCreate):
    new_id = len(db) + 1
    new_entry = {
        "id": new_id,
        "name": entry.name,
        "content": entry.content,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    db.append(new_entry)
    return new_entry

# 방명록 글 삭제하기 (DELETE)
@app.delete("/api/entries/{entry_id}", status_code=200)
def delete_entry(entry_id: int):
    global db # 전역 변수인 db를 수정하기 위해 global 키워드 사용

    # entry_id에 해당하는 글을 찾습니다.
    entry_to_delete = next((entry for entry in db if entry["id"] == entry_id), None)
    
    # 해당 ID의 글이 없으면 404 에러를 발생시킵니다.
    if not entry_to_delete:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    # 리스트 컴프리헨션을 사용하여 해당 id를 제외한 새로운 리스트를 만듭니다.
    db = [entry for entry in db if entry["id"] != entry_id]
    
    return {"message": "Entry deleted successfully"}