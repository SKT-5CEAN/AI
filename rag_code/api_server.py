# main.py
#embed,vector에 관련된것..
from fastapi import FastAPI
from pydantic import BaseModel
from vector import load_and_add_data, search #파일에서 import

# FastAPI 인스턴스 생성
app = FastAPI()

# API 요청 데이터 형식
class Query(BaseModel):
    text: str

# 데이터베이스 초기화 (서버 시작 시 1회 실행)
load_and_add_data()

@app.post("/search")
def search(query: Query):
    results = search(query.text)
    return {"results": results}

