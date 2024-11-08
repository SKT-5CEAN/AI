import chromadb
from chromadb.config import Settings
import json
import sys

# '5CEAN_MVP/자기소개서' 경로를 Python 경로에 추가
sys.path.append('/Users/zeegun/5CEAN_MVP/자기소개서')
#파일 연결
from 자기소개서.rag_code.app.embed import get_embedding

# 각 데이터셋 JSON 파일 경로
single_pairs_path = "/Users/zeegun/5CEAN_MVP/자기소개서/data/final_data.json"
full_essay_path= "/Users/zeegun/5CEAN_MVP/자기소개서/data/whole_data/jobkorea_essays.json" #자소서 질문과 답변(기업도?)
full_question_path= "/Users/zeegun/5CEAN_MVP/자기소개서/data/whole_data/jobkorea_questions.json" #면접 질문들..
qa_pairs_path = "/Users/zeegun/5CEAN_MVP/자기소개서/data/whole_data/train_total.json" # 데이터 다 json으로 조절후 통합한 1개 파일만. 

# 원격 ChromaDB 서버에 HttpClient로 연결
client = chromadb.PersistentClient(path="./data/chromadb_storage")

# 하나의 컬렉션 생성 / 한번 만들어서 get
collection = client.create_collection("interview_data")

'''
# 컬렉션 생성
single_collection = client.create_collection("single_intro")
essay_collection = client.create_collection("essay_intro")
question_collection = client.create_collection("question_intro")
qa_collection = client.create_collection("qa_pairs")
'''

# 데이터 추가 함수
#item은 data의 각 요소.
def add_data_to_collection(collection, data, id_prefix):
    for i, item in enumerate(data):
        # 고유 ID 생성
        doc_id = f"{id_prefix}_{i}"
        
        # 텍스트에 따라 적절히 분리하여 임베딩과 메타데이터 저장
        if id_prefix == "single":
            #final_data.json
            text = item["질문"] + " " + item["답변"]  # 질문과 답변을 결합하여 임베딩
            metadata = {
                "type": "paired_question",
                "질문": item["질문"],
                "답변": item["답변"],
                "유사도": item["유사도"]
            }
        elif id_prefix == "question":
            text = item["q질문"]
            metadata = {
                "type": "question",
                "기업명": item["q기업명"],
                "직무명": item["q직무명"],
                "질문": item["q질문"]
            }
        elif id_prefix == "essay":
            text = item["질문"] + " " + item["답변"]  # 질문과 답변을 결합하여 임베딩
            metadata = {
                "type": "essay",
                "기업명": item["기업명"],
                "질문": item["질문"],
                "답변": item["답변"]
            }
        elif id_prefix == "qa":
            # train_total.json의 면접 대화
            text = item["question"] + " " + item["answer"]  # 질문과 답변을 결합하여 임베딩
            metadata = {
                "type": "dialogue",
                "질문": item["question"],
                "답변": item["answer"]
            }
        
        # 임베딩 생성 및 컬렉션에 추가
        embedding = get_embedding(text)
        # embedding이 None이 아닌 경우에만 tolist()를 호출
        if embedding is not None:
            embedding = embedding.tolist()  # .tolist()는 None이 아닐 때만 호출
            collection.add(documents=[text], metadatas=[metadata], embeddings=[embedding], ids=[doc_id])
        else:
            print(f"Embedding for question '{text}' is None and was not added.")

# 데이터 로드

with open(single_pairs_path, "r", encoding="utf-8") as f:
    single_pairs = json.load(f)
    add_data_to_collection(collection, single_pairs, "single")

with open(full_essay_path, "r", encoding="utf-8") as f:
    essays = json.load(f)
    add_data_to_collection(collection, essays, "essay")

with open(full_question_path, "r", encoding="utf-8") as f:
    questions = json.load(f)
    add_data_to_collection(collection, questions, "question")

with open(qa_pairs_path, "r", encoding="utf-8") as f:
    qa_pairs = json.load(f)
    add_data_to_collection(collection, qa_pairs, "qa")


def search(query, k=3):
    query_embedding = get_embedding(query).tolist()
    results = collection.query(query_embeddings=[query_embedding], n_results=k)
    return [(res["question"], res["distance"]) for res in results["metadatas"][0]]
