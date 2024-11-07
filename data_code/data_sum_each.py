import os
import pandas as pd

# 파일 읽기
e_file = pd.read_csv('/Users/zeegun/5CEAN_MVP/자기소개서/data/jobkorea_essays.csv')
q_file = pd.read_csv('/Users/zeegun/5CEAN_MVP/자기소개서/data/combined_output.csv')

# 결과를 저장할 디렉토리 경로
save_directory = '/Users/zeegun/5CEAN_MVP/자기소개서/data/each_company'

# 같은 기업명을 기준으로 데이터를 병합하고 저장
for 기업명 in e_file['기업명'].unique():
    e_subset = e_file[e_file['기업명'] == 기업명].reset_index(drop=True)  # 번호, 기업명, 질문, 답변
    q_subset = q_file[q_file['q기업명'] == 기업명].reset_index(drop=True)  # q번호, q기업명, q직무명, q질문
    
    # 두 데이터프레임이 같은 기업명으로 있는 경우만 처리
    if not q_subset.empty:
        # 두 데이터프레임의 길이를 맞춰서 빈 값으로 채우기
        max_length = max(len(e_subset), len(q_subset))  # 둘 중 더 긴 것을 기준으로 함
        
        # e_subset에 빈 행 추가
        if len(e_subset) < max_length:
            empty_rows = pd.DataFrame([[''] * len(e_subset.columns)] * (max_length - len(e_subset)), columns=e_subset.columns)
            e_subset = pd.concat([e_subset, empty_rows], ignore_index=True)
        
        # q_subset에 빈 행 추가
        if len(q_subset) < max_length:
            empty_rows = pd.DataFrame([[''] * len(q_subset.columns)] * (max_length - len(q_subset)), columns=q_subset.columns)
            q_subset = pd.concat([q_subset, empty_rows], ignore_index=True)
        
        # 인덱스를 리셋하여 중복 방지
        e_subset = e_subset.reset_index(drop=True)
        q_subset = q_subset.reset_index(drop=True)
        
        # 두 줄을 병합하여 하나의 데이터프레임으로 만듦
        merged = pd.concat([e_subset[['번호', '기업명', '질문', '답변']],
                            q_subset[['q번호', 'q기업명', 'q직무명', 'q질문']]],axis=1)
        
        # 각 기업별로 CSV 파일 저장
        file_name = f"qepair_{기업명}.csv"  # 파일 이름 지정 (기업명 포함)
        file_path = os.path.join(save_directory, file_name)  # 경로에 파일 저장
        merged.to_csv(file_path, index=False)  # CSV 파일로 저장

print("파일 저장 완료")
