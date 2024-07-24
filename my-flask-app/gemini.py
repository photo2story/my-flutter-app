# gemini.py
import os
import sys
import pandas as pd
import requests
from dotenv import load_dotenv
import google.generativeai as genai
import shutil

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
        earnings_text += f"| {end} (Filed: {filed}): EPS {eps_val}, Revenue {revenue_val:.2f} B$ |\n"
    return earnings_text

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

        # 어닝 데이터 가져오기
        recent_earnings = get_recent_eps_and_revenue(ticker)
        if not recent_earnings:
            raise ValueError("No recent earnings data found.")

        # earnings_text 변수 생성
        earnings_text = format_earnings_text(recent_earnings)

        # 프롬프트 준비
        prompt_voo = f"""
        1) Provide a simple comparison between the given stock (ticker) and the S&P 500 (VOO) 
           in terms of cumulative returns up to the most recent date:

            Stock Ticker: {ticker}
            Company name and a brief description
            Cumulative return of the stock: {final_rate}
            Cumulative return of the benchmark (S&P 500, VOO): {final_rate_vs}
        2) Briefly describe the recent stock price trends using the 5-day, 20-day, and 60-day moving averages:

            5-day Moving Average: {sma_5}
            20-day Moving Average: {sma_20}
            60-day Moving Average: {sma_60}
        3) Briefly analyze the technical indicators, including RSI and PPO:

            RSI: {rsi}
            PPO: {ppo}
        4) Briefly analyze the recent earnings and outlook. 
            Provide the last 4 quarters' results in the following format: {earnings_text}. 
            For the most recent quarter, include a comparison between actual results and estimates.

        5) Provide a comprehensive summary analysis (summarizing points 1 to 4).
        """

        # Gemini API 호출
        response_ticker = model.generate_content(prompt_voo)

        # 리포트를 텍스트로 저장
        report_text = response_ticker.text
        print(report_text)

        # 디스코드 웹훅 메시지로 전송
        success_message = f"Gemini API 분석 완료: {ticker}\n{report_text}"
        print(success_message)
        response = requests.post(DISCORD_WEBHOOK_URL, json={'content': success_message})

        # 리포트를 텍스트 파일로 저장
        report_file = f'report_{ticker}.txt'
        with open(report_file, 'w', encoding='utf-8') as file:
            file.write(report_text)

        # 리포트를 static/images 폴더로 이동 및 커밋
        move_files_to_images_folder()

        return f'Gemini Analysis for {ticker} (VOO) has been sent to Discord and saved as a text file.'

    except Exception as e:
        error_message = f"{ticker} 분석 중 오류 발생: {e}"
        print(error_message)
        response = requests.post(DISCORD_WEBHOOK_URL, data={'content': error_message})
        return error_message


if __name__ == '__main__':
    # 분석할 티커 설정
    ticker = 'TSLA'
    analyze_with_gemini(ticker)



"""
source .venv/bin/activate
python gemini.py    
"""