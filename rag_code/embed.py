from transformers import AutoTokenizer, AutoModel
import torch

# KoBERT 모델과 토크나이저 불러오기
tokenizer = AutoTokenizer.from_pretrained("monologg/kobert", trust_remote_code=True)
model = AutoModel.from_pretrained("monologg/kobert", trust_remote_code=True)

# 텍스트 임베딩 함수 정의
def get_embedding(text):
    if text is None:  # 텍스트가 None인 경우 None 반환
        return None
    
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
    # [CLS] 토큰에 대한 임베딩을 사용 (BERT의 대표적인 문장 벡터)
    embedding = outputs.last_hidden_state[:, 0, :].squeeze().numpy()
    return embedding
