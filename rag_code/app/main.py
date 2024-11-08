from fastapi import FastAPI
import sys
sys.path.append('/Users/zeegun/5CEAN_MVP/자기소개서/rag_code')
from app.services import generate_question, InputData
from app.config import setup_cors


app = FastAPI()

# CORS 설정 적용
setup_cors(app)

@app.post("/generate_questions")
async def generate(input_data: InputData):
    response = generate_question(input_data.self_intro)
    return response
