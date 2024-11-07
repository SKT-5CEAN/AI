import pandas as pd

# CSV 파일 경로
csv_file_path = '/Users/zeegun/5CEAN_MVP/자기소개서/data/whole_data/jobkorea_questions.csv'  # CSV 파일 경로를 입력하세요
json_file_path = '/Users/zeegun/5CEAN_MVP/자기소개서/data/whole_data/jobkorea_questions.json'   # 출력할 JSON 파일 경로

# CSV 파일 읽기
df = pd.read_csv(csv_file_path)

# 필요한 열만 선택 (기업명, 질문, 답변)
df_filtered = df[['q기업명', 'q직무명', 'q질문']]

# JSON으로 변환
df_filtered.to_json(json_file_path, orient='records', force_ascii=False, indent=4)

print(f"CSV 파일이 JSON 파일로 변환되었습니다: {json_file_path}")
