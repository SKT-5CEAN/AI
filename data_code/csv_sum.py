import pandas as pd
import os

print(os.getcwd())

# CSV 파일들이 저장된 디렉토리 경로
directory = "/Users/zeegun/5CEAN_MVP/자기소개서"

# 여러 CSV 파일을 저장할 리스트, "jobkorea_essays.csv"는 제외
csv_files = [f for f in os.listdir(directory) if f.endswith('.csv') and f != "jobkorea_essays.csv"]

# 빈 데이터프레임을 생성
combined_csv = pd.DataFrame()

# 모든 CSV 파일을 하나씩 읽어와서 합치기
for file in csv_files:
    file_path = os.path.join(directory, file)
    df = pd.read_csv(file_path)
    combined_csv = pd.concat([combined_csv, df])

# 합쳐진 데이터를 새로운 CSV 파일로 저장
combined_csv.to_csv("combined_output.csv", index=False)
