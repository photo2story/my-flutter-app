# gemini.py
import os
import pandas as pd
import requests
from dotenv import load_dotenv
import google.generativeai as genai
import shutil
import matplotlib.pyplot as plt
from git_operations import move_files_to_images_folder

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')
GITHUB_RAW_BASE_URL = "https://raw.githubusercontent.com/photo2story/my-flutter-app/main/static/images"

# Configure the Gemini API
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def download_csv(ticker):
    ticker_vs_voo_url = f"{GITHUB_RAW_BASE_URL}/result_VOO_{ticker}.csv"
    response_ticker = requests.get(ticker_vs_voo_url)

    if response_ticker.status_code == 200:
        with open(f'result_VOO_{ticker}.csv', 'wb') as f:
            f.write(response_ticker.content)
        return True
    else:
        return False

def analyze_with_gemini(ticker):
    try:
        # 시작 메시지 전송
        start_message = f"Gemini API를 사용하여 {ticker} 분석을 시작합니다."
        print(start_message)
        response = requests.post(DISCORD_WEBHOOK_URL, data={'content': start_message})

        # CSV 파일 다운로드
        if not download_csv(ticker):
            error_message = f'Error: The file for {ticker} does not exist.'
            print(error_message)
            response = requests.post(DISCORD_WEBHOOK_URL, data={'content': error_message})
            return error_message

        # CSV 파일 로드
        voo_file = f'result_VOO_{ticker}.csv'
        df_voo = pd.read_csv(voo_file)

        # CSV 데이터를 문자열로 변환
        voo_data_str = df_voo.to_csv(index=False)

        # Gemini API 호출을 위한 프롬프트 준비
        prompt_voo = f"""
        1) 제공된 자료의 수익율(rate)와 S&P 500(VOO)의 수익율(rate_vs)과 비교해서 이격된 정도를 알려줘_
           (간단하게 자료 맨마지막날의 수익율차이)_
            대상주식의 rate필드(누적수익률) 값과 기초지수인 S&P 500의 rate_vs 필드(VOO누적수익률)값으로 비교{ticker}:\n{voo_data_str}
        2) 제공된 자료의 최근 주가 변동(간단하게: 5일, 20일, 60일 이동평균 수치로)
        3) 제공된 자료의 RSI, PPO 인덱스 지표를 분석해줘 (간단하게: RSI 40 과매도)
        4) 최근 실적 및 전망(웹검색해서 간단하게: 최근 매출,영업이익, 다음분기 전망 매출, 영업이익)
        5) 애널리스트 의견(웹검색해서 간단하게: 추천의견..)
        6) 레포트는 ["candidates"][0]["content"]["parts"][0]["text"]의 구조의 텍스트로 만들어줘
        7) 레포트는 한글로 만들어줘
        """

        # Gemini API 호출
        response_ticker = model.generate_content(prompt_voo)

        # 리포트를 텍스트로 저장
        report_text = response_ticker.text        
        # report_text = response_ticker.result["candidates"][0]["content"]["parts"][0]["text"]
        print(report_text)

        # 디스코드 웹훅 메시지로 전송
        success_message = f"Gemini API 분석 완료: {ticker}\n{report_text}"
        print(success_message)
        response = requests.post(DISCORD_WEBHOOK_URL, data={'content': success_message})

        # 리포트를 텍스트 파일로 저장
        report_file = f'report_{ticker}.txt'
        with open(report_file, 'w', encoding='utf-8') as file:
            file.write(report_text)

        # 리포트를 static/images 폴더로 이동
        destination_folder = os.path.join('static', 'images')
        os.makedirs(destination_folder, exist_ok=True)
        # shutil.move(report_file, os.path.join(destination_folder, os.path.basename(report_file)))
        move_files_to_images_folder()

        return f'Gemini Analysis for {ticker} (VOO) has been sent to Discord and saved as a text file.'

    except Exception as e:
        error_message = f"{ticker} 분석 중 오류 발생: {e}"
        print(error_message)
        response = requests.post(DISCORD_WEBHOOK_URL, data={'content': error_message})
        return error_message

if __name__ == '__main__':
    ticker = 'AAPL'  # Example ticker
    report = analyze_with_gemini(ticker)
    print(report)




"""
source .venv/bin/activate
python gemini.py    
"""