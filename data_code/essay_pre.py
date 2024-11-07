import pandas as pd
import re

# CSV 파일 불러오기
df = pd.read_csv('jobkorea_essays.csv')

# 번호 열 제거
df = df.drop(columns=['번호'])

# 특수기호 제거하는 함수 정의
def remove_special_chars(text):
    # 정규 표현식으로 " ! () 등의 특수 기호 제거
    return re.sub(r'[!\"()]', '', text)

# 기업명, 질문, 답변 열에서 특수 기호 제거
df['기업명'] = df['기업명'].apply(remove_special_chars)
df['질문'] = df['질문'].apply(remove_special_chars)
df['답변'] = df['답변'].apply(remove_special_chars)

# 처리된 파일 저장
df.to_csv('output.csv', index=False)

print("전처리 완료된 파일이 output.csv로 저장되었습니다.")
