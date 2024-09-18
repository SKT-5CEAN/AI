import requests
from bs4 import BeautifulSoup
import time
import csv

#메인 페이지 URL(필터링 불가 띠발)
url = 'https://www.jobkorea.co.kr/starter/Review?FavorCo_Stat=0&G_ID=0&OrderBy=0&Page='

# User-Agent 설정 (웹사이트에서 봇을 차단하는 것을 피하기 위해)
headers = { 
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'}

#직무
keywords = ['백엔드개발자','프론트엔드개발자','웹개발자','앱개발자','시스템엔지니어','네트워크엔지니어','DBA','데이터엔지니어','데이터사이언티스트','보안엔지니어','소프트웨어개발자','게임개발자','하드웨어개발자','머신러닝엔지니어','블록체인개발자','클라우드엔지니어','웹퍼블리셔','IT컨설팅','QA', 'IT', 'CS', '네트워크', '웹기획', 'SW', '개발']

with open('jobkorea_questions.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['번호', '기업명', '직무명', '질문'])

    for page in range(1, 131): # 130까지 있음
        page_url = url + str(page)
        response = requests.get(page_url, headers=headers)
        html = response.text
        soup = BeautifulSoup(html, 'html.parser') 

        for idx in range(1, 21): # 한페이지 1-20
            #기업리스트 중에 면접질문 태그
            interveiw_link_selector = f"#container > div.stContainer > div.starListsWrap.ctTarget > div.jaListArea > ul > li:nth-child({idx}) > div.reviewWrap > ul > li:nth-child(2) > a"
            interveiw_link_element = soup.select_one(interveiw_link_selector)

            #기업으로 들어가기 
            if interveiw_link_element:
                interveiw_url = interveiw_link_element['href']
                full_url = 'https://www.jobkorea.co.kr' + interveiw_url

                # 기업상세 페이지 요청
                detail_response = requests.get(full_url, headers=headers)
                detail_html = detail_response.text
                detail_soup = BeautifulSoup(detail_html, 'html.parser')
                q = detail_soup.select_one('div.tplPagination.reviewPg ul') # 기업안에서 질문리스트 1,2,3... one-> all로

                # 기업명 크롤링 (CSS 선택자를 사용하여 기업명 추출)
                company_name_selector = f"#container > div.stContainer > div.viewTitWrap > div > h2 > strong > a"
                company_name_element = detail_soup.select_one(company_name_selector)
                company_name = company_name_element.get_text(strip=True) if company_name_element else '기업명 없음'

                #면접 질문 크롤링(한페이지에 30개 질문 / 각 기업마다 페이지 수는 다름)
                #1. 일반면접 - PO 이렇게 되있다. 어케 구별쓰?
                if q:
                    nth_page = q.find_all('li') # 기업안에서 질문리스트 1,2,3...

                    for n_page in nth_page:
                        link_element = n_page.find('a')
                        if link_element: #2번 이상 페이지
                            list_url = link_element.get('href', None)
                            if list_url: # herf 태그가 있을때만
                                listfull_url = 'https://www.jobkorea.co.kr' + list_url
                                list_response = requests.get(listfull_url, headers=headers)
                                list_html = list_response.text
                                list_soup = BeautifulSoup(list_html , 'html.parser')
                                question = list_soup.select_one('div.reviewQnaWrap ul')
                        else:#1번 페이지
                            question = detail_soup.select_one('div.reviewQnaWrap')

                        if question: # 1번째, 2번째 질문 리스트 페이지 안에서..
                            if not isinstance(question, str):
                                nth = question.find_all('li')
                                for n in nth:
                                    roles = n.select_one('span.tit').get_text(strip = True) #직무 일반면접 - PO
                                    question = n.select_one('span.tx').get_text(strip = True) #질문내용

                                    role = next((keyword for keyword in keywords if keyword in roles), None)
                                    # CSV에 저장
                                    if role is not None:
                                        writer.writerow([idx + (page - 1) * 20, company_name, role, question])
                                        #print(f'[{idx + (page - 1) * 20}] 면접 질문 링크를 찾을 수 없습니다.') #else 뺌 어짜피 개발직군 아니면 다오류메세지 띄우니
        writer.writerow([])
        # 한 페이지의 면접 질문을 모두 크롤링한 후 1초 대기
        time.sleep(1)
print('크롤링이 완료되었습니다.')
