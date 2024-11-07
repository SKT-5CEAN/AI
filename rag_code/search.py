from chromadb import PersistentClient
from transformers import T5ForConditionalGeneration, T5Tokenizer
import sys
# '5CEAN_MVP/자기소개서' 경로를 Python 경로에 추가
sys.path.append('/Users/zeegun/5CEAN_MVP/자기소개서')
#파일 연결
from rag_code.embed import get_embedding

# ChromaDB 클라이언트 연결 및 컬렉션 설정
client = PersistentClient(path="./data/chromadb_storage")
collection = client.get_collection("interview_data")
#자기소개서 질문과 답변, 면접질문, 자소서문장과 면접질문, 면접대화

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

def generate_question(question, answer, tokenizer, model, collection):
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
    return question

# 모델 및 토크나이저 로드
model_path = "/Users/zeegun/5CEAN_MVP/fine_tuned_ET5"
model = T5ForConditionalGeneration.from_pretrained(model_path)
tokenizer = T5Tokenizer.from_pretrained(model_path)

# 사용자 입력 요청
input_text = input("자기소개서를 입력해주세요! (예: 1.내가 인생에서 제일 몰두해본 기억은?:저는 ~~~입니다.)")

# 숫자, 질문, 답변으로 분리
try:
    number, rest = input_text.split('.', 1)
    question, answer = rest.split(':', 1)

    # 변수 할당
    number = number.strip()  # 숫자
    question = question.strip()  # 자기소개서 질문
    answer = answer.strip()  # 자기소개서 답변

    # 결과 출력 확인
    print("번호:", number)
    print("질문:", question)
    print("답변:", answer)

except ValueError:
    #잘못된 형식을 설명해주는 멘트!
    print("올바른 형식으로 입력해주세요. 예: 1.내가 인생에서 제일 몰두해본 기억은?:저는 ~~~입니다.")

print("예상질문: " + generate_question(question, answer, tokenizer, model, collection))