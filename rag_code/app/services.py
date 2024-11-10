from fastapi import FastAPI
from pydantic import BaseModel
from transformers import T5Tokenizer, T5ForConditionalGeneration
import chromadb
import re

import sys
sys.path.append('/Users/zeegun/5CEAN_MVP/자기소개서/rag_code')
from app.embed import get_embedding

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
    
    # 검색 시스템을 통해 유사한 문서 검색 (id 필터 추가)
    results = collection.query(
        query_embeddings=[input_embedding],
        n_results=top_k
    )
    # 상위 검색 결과의 텍스트 부분만 반환
    #[doc["metadata"]["질문"] for doc in results["documents"][0][:top_k]]
    return results

def get_top_similar_questions(similar_question, similar_answers, top_k=3):
    all_distances = []
    all_questions = []

    # similar_question에서 거리와 질문 추출
    for distance, metadata in zip(similar_question["distances"][0], similar_question["metadatas"][0]):
        all_distances.append(distance)
        all_questions.append(metadata["질문"])

    # similar_answers에서 거리와 질문 추출
    for result in similar_answers:
        for distance, metadata in zip(result["distances"][0], result["metadatas"][0]):
            all_distances.append(distance)
            all_questions.append(metadata["질문"])

    # 거리값을 기준으로 정렬하여 상위 top_k 인덱스 추출
    top_indices = sorted(range(len(all_distances)), key=lambda i: all_distances[i])[:top_k]
    top_questions = [all_questions[i] for i in top_indices]

    return top_questions

def prepare_prompt(input_question, input_answers, prompt_question):
    # 검색된 텍스트를 입력 문장과 결합
    prompt = """당신은 기업의 면접관입니다.
    면접자의 자기소개서를 읽고 그에게 질문하세요.
    해당 자기소개서와 유사한 자기소개서에선 다음과 같은 유사질문이 면접에 출제되었습니다. 
    예상질문을 3개 생성하세요.
    출력형식은 다음과 같습니다. (숫자).(예상질문)
    출력예시는 다음과 같습니다. 1.당신의 강점은 무엇입니까?
    자기소개서 문항: {} 
    자기소개서 답변: {} 
    유사 질문:\n""".format(input_question, input_answers)
    
    for text in prompt_question:
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

        #답변을 한문장씩 리스트로 자름.
        sentences = re.split(r'[.!?]\s*', answer)

    except ValueError:
        #잘못된 형식을 설명해주는 멘트!
        print("올바른 형식으로 입력해주세요. 예: 1.내가 인생에서 제일 몰두해본 기억은?:저는 ~~~입니다.")

    #각각 비슷한 질문과 답변 찾기(results객체)
    similar_question = retrieve_similar_documents(question, collection)
    similar_answers = []
    for sentence in sentences:
        similar_answers.append(retrieve_similar_documents(sentence, collection))

    prompt_question = get_top_similar_questions(similar_question, similar_answers, top_k=3)
    # 프롬프트 준비
    prompt = prepare_prompt(question, answer, prompt_question)
    print(prompt)

    # 프롬프트 토큰화 및 생성 모델에 입력
    input_ids = tokenizer(prompt, return_tensors="pt").input_ids
    outputs = model.generate(input_ids=input_ids, max_length=200)
    
    # 생성된 질문을 디코딩
    question = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return {"question":question}