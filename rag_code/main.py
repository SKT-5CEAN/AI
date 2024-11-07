from fastapi import FastAPI
from pydantic import BaseModel
from transformers import T5Tokenizer, T5ForConditionalGeneration
import chromadb
import sys
sys.path.append('/Users/zeegun/5CEAN_MVP/자기소개서')
from rag_code.embed import get_embedding
from fastapi.middleware.cors import CORSMiddleware

# 앱 인스턴스 생성
app = FastAPI()

# CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 출처 허용 (또는 특정 출처만 허용하도록 설정 가능)
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

# 모델 및 토크나이저 로드
model_path = "/Users/zeegun/5CEAN_MVP/fine_tuned_ET5"
tokenizer = T5Tokenizer.from_pretrained(model_path)
model = T5ForConditionalGeneration.from_pretrained(model_path)

client = chromadb.PersistentClient(path="./data/chromadb_storage")
collection = client.get_collection("interview_data")

# 요청 데이터 모델 정의
class InputData(BaseModel):
    self_intro: str

def retrieve_similar_documents(input_text, collection, top_k=3):
    # 입력 텍스트를 임베딩
    input_embedding = get_embedding(input_text)
    
    # 검색 시스템을 통해 유사한 문서 검색
    results = collection.query(query_embeddings=[input_embedding], n_results=top_k)
    # 상위 검색 결과를 반환
    return results['documents'][0][:3]


def prepare_prompt(input_question, input_answer, retrieved_texts):
    # 검색된 텍스트를 입력 문장과 결합
    prompt = """당신은 기업의 면접관입니다.
    \n면접자의 자기소개서를 읽고 그에게 질문하세요.
    \n자기소개서의 문항과 답변을 읽고, 유사 자기소개서에 대한 질문예시를 참고하여 질문하세요.
    \n예상질문을 3개 생성하세요
    \n출력형식은 다음과 같습니다. (숫자).(예상질문)\n 
    \n출력예시는 다음과 같습니다. 1.당신의 강점은 무엇입니까?\n"""
    "\n자기소개서 문항: " + input_question + "\n자기소개서 답변: " + input_answer + "\n유사 질문:\n"
    for text in retrieved_texts:
        prompt += "- " + text + "\n"
    prompt += "위의 내용을 참고하여 예상질문을 생성하세요."
    return prompt

def generate_question(input_text):
    # 숫자, 질문, 답변으로 분리
    try:
        number, rest = input_text.split('.', 1)
        question, answer = rest.split(':', 1)

        # 변수 할당
        number = number.strip()  # 숫자
        question = question.strip()  # 자기소개서 질문
        answer = answer.strip()  # 자기소개서 답변
        
    except ValueError:
        #잘못된 형식을 설명해주는 멘트!
        print("올바른 형식으로 입력해주세요. 예: 1.내가 인생에서 제일 몰두해본 기억은?:저는 ~~~입니다.")

    #각각 비슷한 질문과 답변 찾기(사실 질문을 기점으로 찾아야 하나..)
    #ids가 = ()_숫자 이니 이를 고려해서.
    similar_question = retrieve_similar_documents(question, collection)
    similar_answer = retrieve_similar_documents(answer,collection)
    
    # 프롬프트 준비
    prompt = prepare_prompt(question, answer, similar_question)
    
    # 프롬프트 토큰화 및 생성 모델에 입력
    input_ids = tokenizer(prompt, return_tensors="pt").input_ids
    outputs = model.generate(input_ids=input_ids, max_length=200)
    
    # 생성된 질문을 디코딩
    question = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return {"question":question}

# API 엔드포인트 생성
@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/generate_questions")
async def generate(input_data: InputData):
    response = generate_question(input_data.self_intro)
    return response
