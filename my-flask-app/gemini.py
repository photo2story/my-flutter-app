# gemini.py
import os
import pandas as pd
import requests
from dotenv import load_dotenv
import google.generativeai as genai
import shutil
import matplotlib.pyplot as plt
from git_operations import move_files_to_images_folder
from googleapiclient.discovery import build

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
GOOGLE_CSE_ID = os.getenv('GOOGLE_CSE_ID')
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

def google_search(query, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=query, cx=cse_id, **kwargs).execute()
    return res['items']

def get_latest_performance(ticker):
    query = f"{ticker} latest earnings"
    results = google_search(query, GOOGLE_API_KEY, GOOGLE_CSE_ID, num=1)
    if results:
        return results[0]['snippet']
    return "No recent performance data found."

def get_analyst_opinions(ticker):
    query = f"{ticker} analyst opinions"
    results = google_search(query, GOOGLE_API_KEY, GOOGLE_CSE_ID, num=1)
    if results:
        return results[0]['snippet']
    return "No analyst opinions found."

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

        # 데이터 추출
        final_rate = df_voo['rate'].iloc[-1]
        final_rate_vs = df_voo['rate_vs'].iloc[-1]
        sma_5 = df_voo['sma05_ta'].iloc[-1]
        sma_20 = df_voo['sma20_ta'].iloc[-1]
        sma_60 = df_voo['sma60_ta'].iloc[-1]
        rsi = df_voo['rsi_ta'].iloc[-1]
        ppo = df_voo['ppo_histogram'].iloc[-1]

        # 웹 검색 결과 가져오기
        latest_performance = get_latest_performance(ticker)
        analyst_opinions = get_analyst_opinions(ticker)

        # 프롬프트 준비
        prompt_voo = f"""
        1) 제공된 자료의 수익율(rate)와 S&P 500(VOO)의 수익율(rate_vs)과 비교해서 이격된 정도를 알려줘 (간단하게 자료 맨마지막날의 누적수익율차이):
           리뷰할 주식티커명 = {ticker}
           리뷰주식의 누적수익률 = {final_rate}
           기준이 되는 비교주식(S&P 500, VOO)의 누적수익율 = {final_rate_vs}
        2) 제공된 자료의 최근 주가 변동(간단하게: 5일, 20일, 60일 이동평균 수치로):
           5일이동평균 = {sma_5}
           20일이동평균 = {sma_20}
           60일이동평균 = {sma_60}
        3) 제공된 자료의 RSI, PPO 인덱스 지표를 분석해줘 (간단하게):
           RSI = {rsi}
           PPO = {ppo}
        4) 최근 실적 및 전망(웹검색해서 간단하게):
           최근 매출 = {latest_performance}
        5) 애널리스트 의견(웹검색해서 간단하게):
           추천의견 = {analyst_opinions}
        6) 레포트는 ["candidates"][0]["content"]["parts"][0]["text"]의 구조의 텍스트로 만들어줘
        7) 레포트는 한글로 만들어줘
        """

        # Gemini API 호출
        response_ticker = model.generate_content(prompt_voo)

        # 리포트를 텍스트로 저장
        report_text = response_ticker.text        
        print(report_text)

        # 디스코드 웹훅 메시지로 전송
        success_message = f"Gemini API 분석 완료: {ticker}\n{report_text}"
        print(success_message)
        response = requests.post(DISCORD_WEBHOOK_URL, data={'content': success_message})

        # 리포트를 텍스트 파일로 저장
        report_file = f'report_{ticker}.txt'
        with open(report_file, 'w', encoding='utf-8') as file:
            file.write(report_text)

        # 리포트를 static/images 폴더로 이동 및 커밋
        destination_folder = os.path.join('static', 'images')
        os.makedirs(destination_folder, exist_ok=True)
        shutil.move(report_file, os.path.join(destination_folder, os.path.basename(report_file)))
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