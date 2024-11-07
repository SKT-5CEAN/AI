import torch
import pandas as pd
from transformers import BertModel
from kobert_tokenizer import KoBERTTokenizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import nltk

#file 불러오기
file = pd.read_csv("/Users/zeegun/5CEAN_MVP/자기소개서/data/each_company/qepair_(재)한국문학번역원.csv")
# BERT 모델과 토크나이저 불러오기
tokenizer = get_tokenizer()
model = BertModel.from_pretrained('skt/kobert-base-v1')
#model.to('cpu')

# 질문 임베딩을 계산하는 함수
def get_question_embedding(question):
    inputs = tokenizer(question, return_tensors='pt', truncation=True, padding=True) #텐서로 변환
    with torch.no_grad():
        outputs = model(**inputs)#모델에 넣어 임베딩 백터 계산
    return outputs.last_hidden_state.mean(dim=1).numpy()#평균 임베딩 계산

# 코사인 유사도로 질문의 유사도 계산
def get_most_similar_sentence(new_question, existing_questions, batch_size=10):
    new_question_emb = get_question_embedding(new_question)
    most_similar_sentence = None
    max_similarity = -1

    # 배치 단위로 처리
    for i in range(0, len(existing_questions), batch_size):
        batch_questions = existing_questions[i:i + batch_size]
        existing_question_embs = np.array([get_question_embedding(q) for q in batch_questions])

        # 코사인 유사도 계산
        similarities = cosine_similarity(new_question_emb, existing_question_embs).flatten()
        batch_max_idx = np.argmax(similarities)

        # 현재 배치에서 가장 유사한 질문 업데이트
        if similarities[batch_max_idx] > max_similarity:
            most_similar_sentence = batch_questions[batch_max_idx]
            max_similarity = similarities[batch_max_idx]
    
    return most_similar_sentence, max_similarity


question_answer_pairs = dict(zip(file['질문'], file['답변']))
new_questions = file['q질문']

# 가장 유사한 질문 찾기
# 새로운 질문에 대한 유사한 문장 찾기
for idx, new_question in enumerate(new_questions):
    print(f"q질문: {new_question}")
    
    # 새로운 질문을 문장 단위로 나눔
    new_question_sentences = nltk.sent_tokenize(new_question)
    
    for question, answer in question_answer_pairs.items():
        # 기존 질문과 답변을 문장 단위로 나눔
        question_sentences = nltk.sent_tokenize(question)
        answer_sentences = nltk.sent_tokenize(answer)
        
        for new_question_sentence in new_question_sentences:
            print(f"새로운 질문 문장: {new_question_sentence}")
            
            # 기존 질문의 문장들과 유사도 계산
            similar_question_sentence, question_similarity = get_most_similar_sentence(new_question_sentence, question_sentences)
            similar_answer_sentence, answer_similarity = get_most_similar_sentence(new_question_sentence, answer_sentences)

            if question_similarity > 0.8:
                print(f"가장 유사한 질문 문장: {similar_question_sentence} (유사도: {question_similarity:.2f})")
            
            if answer_similarity > 0.8:
                print(f"가장 유사한 답변 문장: {similar_answer_sentence} (유사도: {answer_similarity:.2f})")
            print("-" * 50)