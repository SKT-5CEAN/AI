import tiktoken
import pandas as pd

# tiktoken에서 사용할 모델에 맞는 인코딩을 불러오기
encoding = tiktoken.encoding_for_model("gpt-4")  # 또는 gpt-3.5

# CSV 파일 불러오기
df = pd.read_csv('/Users/zeegun/5CEAN_MVP/자기소개서/data/combined_output.csv')

# '질문' 열 전체에서 토큰 수를 계산하는 함수 정의
def calculate_tokens(text):
    if pd.isnull(text):  # text가 None 또는 NaN일 경우
        return 0
    # 문자열이 아닐 경우 문자열로 변환
    if not isinstance(text, str):
        text = str(text)
    
    tokens = encoding.encode(text)
    return len(tokens)

# 각 행의 '질문' 열에 대한 토큰 수 계산 후 합산
total_tokens = df['질문'].apply(calculate_tokens).sum()

# 전체 토큰 수 출력
print(f"전체 질문 열의 토큰 수: {total_tokens}")
