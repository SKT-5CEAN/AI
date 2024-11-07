import pandas as pd
import openai

# OpenAI API 키 설정
openai.api_key = 'sk-YXCnGEZWSEOXUfUTJx2MBxnqq4w8naq48lKe3PkW8uT3BlbkFJPAa38-EO9VHHUYAxnoZ4yLFnzUTDbg3DD1SIodyyMA'

# 질문을 분류하는 함수
def classify_question(question):
    # LLM을 사용해 질문을 전공 관련 질문인지 분류
    messages = [
        {"role": "system", "content": "You are an expert at classifying job application questions."},
        {"role": "user", "content": f"Is the following question related to computer science or technical major? Please answer only with 'Yes' or 'No'. '{question}'"}
    ]
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=50,  # 적절한 토큰 수를 설정
        temperature=0  # 답변의 일관성을 높이기 위해 temperature를 낮게 설정
    )
    
    classification = response['choices'][0]['message']['content'].strip()
    
    if "yes" in classification.lower():
        return "학문적"
    else:
        return "비학문적"

# CSV 파일 불러오기
df = pd.read_csv("/Users/zeegun/5CEAN_MVP/자기소개서/data_code/non_academic_questions.csv")

# 각 질문에 대해 분류 실행
df['분류'] = df['질문'].apply(classify_question)

# 학문적 질문과 비학문적 질문을 각각 다른 CSV 파일로 저장 (열을 '기업명', '직무명', '질문'으로 제한)
df_academic = df[df['분류'] == '학문적'][['기업명', '직무명', '질문']]
df_non_academic = df[df['분류'] == '비학문적'][['기업명', '직무명', '질문']]

# CSV 파일로 저장
df_academic.to_csv("academic_questions2.csv", index=False)
df_non_academic.to_csv("non_academic_questions2.csv", index=False)

print("질문이 분류되어 academic_questions.csv와 non_academic_questions.csv로 저장되었습니다.")

