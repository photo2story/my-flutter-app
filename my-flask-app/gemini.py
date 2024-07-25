# gemini.py

import os
import sys
import pandas as pd
import requests
from dotenv import load_dotenv
import google.generativeai as genai
import shutil
import asyncio

# 루트 디렉토리를 sys.path에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from git_operations import move_files_to_images_folder
from get_earning import get_recent_eps_and_revenue  # 새롭게 추가된 모듈 import

# 환경 변수 로드
load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')
FMP_API_KEY = os.getenv('FMP_API_KEY')
GITHUB_RAW_BASE_URL = "https://raw.githubusercontent.com/photo2story/my-flutter-app/main/static/images"
CSV_PATH = os.getenv('CSV_PATH', 'static/images/stock_market.csv')

# Gemini API 구성
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# CSV 파일에서 티커명과 회사 이름을 매핑하는 딕셔너리 생성
def create_ticker_to_name_dict(csv_path):
    df = pd.read_csv(csv_path)
    ticker_to_name = dict(zip(df['Symbol'], df['Name']))
    return ticker_to_name

ticker_to_name = create_ticker_to_name_dict(CSV_PATH)

def download_csv(ticker):
    ticker_vs_voo_url = f"{GITHUB_RAW_BASE_URL}/result_VOO_{ticker}.csv"
    response_ticker = requests.get(ticker_vs_voo_url)

    if response_ticker.status_code == 200:
        with open(f'result_VOO_{ticker}.csv', 'wb') as f:
            f.write(response_ticker.content)
        return True
    else:
        return False

def format_earnings_text(earnings_data):
    if not earnings_data:
        return "No earnings data available."
    earnings_text = "| 날짜 : EPS / Revenue |\n"
    for end, filed, eps_val, revenue_val in earnings_data:
        earnings_text += f"| {end} (Filed: {filed}): EPS {eps_val}, Revenue {revenue_val / 1e9:.2f} B$ |\n"
    return earnings_text

def analyze_with_gemini(ticker):
    try:
        # 분석 시작 메시지 전송
        print(f"Starting analysis for {ticker}")
        response = requests.post(DISCORD_WEBHOOK_URL, data={'content': f"Gemini API를 사용하여 {ticker} 분석을 시작합니다."})

        # CSV 파일 다운로드 및 로드
        if not download_csv(ticker):
            raise ValueError(f'Error: The file for {ticker} does not exist.')

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

        # 어닝 데이터 가져오기
        recent_earnings = get_recent_eps_and_revenue(ticker)
        if recent_earnings is None:
            raise ValueError("No recent earnings data found.")
        earnings_text = format_earnings_text(recent_earnings)

        # 프롬프트 준비 및 Gemini API 호출
        prompt_voo = f"""..."""  # 전체 프롬프트 내용

        response_ticker = model.generate_content(prompt_voo)
        report_text = response_ticker.text
        print(report_text)

        # 성공 메시지 및 Discord 전송
        success_message = f"Gemini API 분석 완료: {ticker}\n{report_text}"
        response = requests.post(DISCORD_WEBHOOK_URL, json={'content': success_message})

        # 파일 저장 및 이동
        report_file = f'report_{ticker}.txt'
        with open(report_file, 'w', encoding='utf-8') as file:
            file.write(report_text)

        # GitHub에 파일 이동 및 커밋
        move_files_to_images_folder()

        return f'Gemini Analysis for {ticker} (VOO) has been sent to Discord and saved as a text file.'

    except Exception as e:
        error_message = f"{ticker} 분석 중 오류 발생: {e}"
        print(error_message)
        response = requests.post(DISCORD_WEBHOOK_URL, data={'content': error_message})
        return error_message

if __name__ == '__main__':
    ticker = 'TSLA'
    analyze_with_gemini(ticker)


"""
source .venv/bin/activate
python gemini.py    
"""