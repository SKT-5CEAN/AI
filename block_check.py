import requests

url = 'https://www.jobkorea.co.kr'  # 차단이 의심되는 사이트 URL
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
}

response = requests.get(url, headers=headers)

if response.status_code == 403:
    print("IP가 차단되었습니다. (403 Forbidden)")
elif response.status_code == 429:
    print("요청이 너무 많습니다. (429 Too Many Requests)")
else:
    print(f"응답 코드: {response.status_code}, IP가 차단되지 않았습니다.")
