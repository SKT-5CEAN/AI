#자기소개서와 면접질문을 기업별로 묶어주는 코드. -> 그후 기업의 자기소개서 질문과 답변, 면접질문과의 유사성 검사를 통해서 이를 순서쌍으로 만들것 -> 만든 데이터를 학습시킬것
#각각의 컬럼은 series
import pandas as pd

# 파일 읽기
e_file = pd.read_csv('/Users/zeegun/5CEAN_MVP/자기소개서/data/jobkorea_essays.csv')
q_file = pd.read_csv('/Users/zeegun/5CEAN_MVP/자기소개서/data/combined_output.csv')

# 열을 맞추기 위해 e 파일에 빈 열 추가
e_file['빈열'] = ''

# 결과를 저장할 빈 데이터프레임 생성
result = pd.DataFrame()

# 같은 기업명을 기준으로 데이터를 병합
for 기업명 in e_file['기업명'].unique():
    e_subset = e_file[e_file['기업명'] == 기업명].reset_index(drop=True)  # 번호, 기업명, 질문, 답변
    q_subset = q_file[q_file['q기업명'] == 기업명].reset_index(drop=True) # q번호,q기업명,q직무명,q질문
    
    # 두 데이터프레임이 같은 기업명으로 있는 경우만 처리
    if not q_subset.empty:
        # 두 데이터프레임의 길이를 맞춰서 빈 값으로 채우기
        max_length = max(len(e_subset), len(q_subset)) # 둘중 어디가 양더 많은지
        
        # e_subset에 빈 행 추가
        if len(e_subset) < max_length:
            empty_rows = pd.DataFrame([[''] * len(e_subset.columns)] * (max_length - len(e_subset)), columns=e_subset.columns)
            e_subset = pd.concat([e_subset, empty_rows], ignore_index=True) #기본 행 밑으로 붙인다. 인덱스를 무시하고 새로운 인덱스를 0부터 할당
        
        # q_subset에 빈 행 추가
        if len(q_subset) < max_length:
            empty_rows = pd.DataFrame([[''] * len(q_subset.columns)] * (max_length - len(q_subset)), columns=q_subset.columns)
            q_subset = pd.concat([q_subset, empty_rows], ignore_index=True)

        # 두 줄을 병합하기 전에 인덱스를 리셋하여 중복 방지
        e_subset = e_subset.reset_index(drop=True)
        q_subset = q_subset.reset_index(drop=True)
        
        # 두 줄을 병합하여 result에 추가
        merged = pd.concat([e_subset[['번호', '기업명', '질문', '답변', '빈열']],q_subset[['q번호', 'q기업명', 'q직무명', 'q질문']]],axis=1)
        result = pd.concat([result, merged], ignore_index=True)
        
        # 기업별로 빈 행 추가(왜인지 점점 컬럼 늘어남.)
        #result = pd.concat([result, pd.DataFrame([[''] * len(result.columns)])], ignore_index=True)

# 결과를 CSV 파일로 저장
result.to_csv('qepair.csv', index=False)
