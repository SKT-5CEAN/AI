#여러개의 자소서 크롤링
import requests
from bs4 import BeautifulSoup
import time
import csv

# 메인 페이지 URL(개발 직군만 필터링)
url = 'https://www.jobkorea.co.kr/starter/PassAssay?FavorCo_Stat=0&Pass_An_Stat=0&OrderBy=0&EduType=0&WorkType=0&schPart=10031&isSaved=1&Page='

# User-Agent 설정 (웹사이트에서 봇을 차단하는 것을 피하기 위해)
headers = { 
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
}

# 각 자소서 상세 페이지로 연결되는 링크들을 추출 (a 태그에서 href 속성 가져오기)
base_url = 'https://www.jobkorea.co.kr'
 
# CSV 파일에 저장할 준비
with open('jobkorea_essays.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['번호','기업명','질문','답변']) 


    for page in range(1, 52):
        # 메인 페이지 요청
        page_url = url + str(page)
        response = requests.get(page_url, headers=headers)
        html = response.text
        soup = BeautifulSoup(html, 'html.parser') 
        links = soup.select('a.logo')

        base_idx = (page - 1) * 20

        for idx, link in enumerate(links, 1): 
            href = link['href']
            full_url = base_url + href

            # 기업명 크롤링 (CSS 선택자를 사용하여 기업명 추출)
            company_name_selector = f"#container > div.stContainer > div.starListsWrap.ctTarget > ul > li:nth-child({idx}) > div.txBx > p > a > span"
            company_name_element = soup.select_one(company_name_selector)
            company_name = company_name_element.get_text(strip=True) if company_name_element else '기업명 없음'

            actual_idx = base_idx + idx

            # 상세 페이지 요청
            detail_response = requests.get(full_url, headers=headers)
            detail_html = detail_response.text
            detail_soup = BeautifulSoup(detail_html, 'html.parser')

            # 질문과 답변 추출 (이 부분은 각 페이지의 구조에 맞게 조정해야 함)
            # 예: 질문과 답변이 특정 태그에 포함되어 있는 경우 해당 태그를 찾음
            # 질문과 답변이 있는 dl 태그 찾기
            qna = detail_soup.select_one('div.selfQnaWrap dl')

            if qna:
                # dt 태그 안에 질문, dd 태그 안에 답변이 위치
                questions = qna.find_all('dt')  # 모든 질문을 가져옴
                answers = qna.find_all('dd')    # 모든 답변을 가져옴

                # 질문과 답변을 각각 매칭하여 출력
                for q,a in zip(questions, answers):
                    question_text = q.select_one('button > span.tx')
                    answer_text = a.select_one('div')
                

                    if question_text and answer_text:
                        # p 태그가 있으면 제거
                        answer_text.find('p', recursive=False) and answer_text.find('p').decompose()
                        #CSV에 저장
                        writer.writerow([actual_idx, company_name, question_text.get_text(strip=True),answer_text.get_text(strip=True)])
                #구분을 위한 빈행 추가
                writer.writerow([])

            else:
                print(f'[{actual_idx}] Q&A 섹션을 찾을 수 없습니다.') #actual_idx로 변경해야함.

            # 크롤링 속도를 조절하기 위해 잠시 대기
            time.sleep(1)
print('크롤링이 완료되었습니다.')
