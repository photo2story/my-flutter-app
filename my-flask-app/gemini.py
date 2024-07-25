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
from get_earning import get_recent_eps_and_revenue

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

async def analyze_with_gemini(ticker):
    try:
        # 시작 메시지 전송
        start_message = f"Starting analysis for {ticker}"
        print(start_message)
        requests.post(DISCORD_WEBHOOK_URL, data={'content': start_message})

        # CSV 파일 다운로드
        if not download_csv(ticker):
            error_message = f'Error: The file for {ticker} does not exist.'
            print(error_message)
            requests.post(DISCORD_WEBHOOK_URL, data={'content': error_message})
            return

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
        if recent_earnings is None:
            raise Exception("No recent earnings data found.")
        earnings_text = format_earnings_text(recent_earnings)

        # 프롬프트 준비
        prompt_voo = f"""
        1) 제공된 자료의 수익율(rate)와 S&P 500(VOO)의 수익율(rate_vs)과 비교해서 이격된 정도를 알려줘 (간단하게 자료 맨마지막날의 누적수익율차이):
           리뷰할 주식티커명 = {ticker}
           회사이름과 회사 개요 설명해줘(1줄로)
           리뷰주식의 누적수익률 = {final_rate}
           기준이 되는 비교주식(S&P 500, VOO)의 누적수익율 = {final_rate_vs}
        2) 제공된 자료의 최근 주가 변동(간단하게: 5일, 20일, 60일 이동평균 수치로):
           5일이동평균 = {sma_5}
           20일이동평균 = {sma_20}
           60일이동평균 = {sma_60}
        3) 제공된 자료의 RSI, PPO 인덱스 지표를 분석해줘 (간단하게):
           RSI = {rsi}
           PPO = {ppo}
        4) 최근 실적 및 전망: 제공된 자료의 실적을 분석해줘(간단하게)
           실적 = {earnings_text}
           가장 최근 실적은 예상치도 함께 포함해서 검토해줘
        5) 종합적으로 분석해줘(1~4번까지의 요약)
        6) 레포트는 한글로 만들어줘
        """

        # Gemini API 호출
        response_ticker = model.generate_content(prompt_voo)

        # 리포트 내용 확인
        report_text = response_ticker.text
        print(f"Generated report for {ticker}: {report_text}")

        # Discord로 리포트 전송 전에 빈 메시지인지 확인
        # Gemini API를 사용하여 report_text를 생성한 후
        if report_text.strip():  # 내용이 비어 있거나 공백만 있는지 확인
            requests.post(DISCORD_WEBHOOK_URL, data={'content': report_text})
        else:
            print(f"{ticker}에 대한 보낼 내용이 없습니다.")
            requests.post(DISCORD_WEBHOOK_URL, data={'content': f"{ticker}에 대한 분석 결과를 생성할 수 없습니다."})


        # 리포트를 static/images 폴더로 이동 및 커밋
        await move_files_to_images_folder()

    except Exception as e:
        error_message = f"{ticker} 분석 중 오류 발생: {e}"
        print(error_message)
        requests.post(DISCORD_WEBHOOK_URL, data={'content': error_message})


if __name__ == '__main__':
    # 분석할 티커 설정
    ticker = 'TSLA'
    asyncio.run(analyze_with_gemini(ticker))



# source .venv/bin/activate
# python gemini.py    
