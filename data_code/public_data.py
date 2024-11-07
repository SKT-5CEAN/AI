import json
import os

# 처리할 디렉터리 경로 설정
input_dir = "/Users/zeegun/5CEAN_MVP/129.채용면접 인터뷰 데이터/01-1.정식개방데이터/Training/02.라벨링데이터/TL_04.RND_Female_New"
output_file = "/Users/zeegun/5CEAN_MVP/자기소개서/data/whole_data/train_RND_Female_New.json"

# 새로운 JSON에 저장할 데이터를 추출하는 함수
#일단 함수에 들어와서 try 되기는 함. 문제 없음!
def extract_questions_answers(data):
    try:
        question_text = data["dataSet"]["question"]["raw"].get("text", "")
        answer_text = data["dataSet"]["answer"]["raw"].get("text", "")
        return {"question": question_text, "answer": answer_text}
    except KeyError as e:
        print(f"데이터에서 키 오류 발생: {e}")
        return None

# 디렉터리 내 모든 JSON 파일에서 데이터 추출 및 통합 / 안들어감
all_extracted_data = []

for filename in os.listdir(input_dir):
    if filename.endswith('.json'):
        file_path = os.path.join(input_dir, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                extracted_data = extract_questions_answers(data)
                all_extracted_data.append(extracted_data) # 리스트 안에 리스트로 묶이네.
            except json.JSONDecodeError as e:
                print("JSON Decode Error:", e)
                print(file_path)
                print("f의 내용:", f.read())  # f의 내용을 출력합니다.

# 추출된 데이터를 통합된 JSON 파일로 저장
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(all_extracted_data, f, ensure_ascii=False, indent=4)

print(f"새로운 JSON 파일이 '{output_file}'에 성공적으로 생성되었습니다.")
