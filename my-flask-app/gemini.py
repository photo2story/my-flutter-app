# gemini.py
import os
import sys
import pandas as pd
import requests
from dotenv import load_dotenv
import google.generativeai as genai
import shutil
import threading
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
import asyncio

# 루트 디렉토리를 sys.path에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from git_operations import move_files_to_images_folder

# 환경 변수 로드
load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')
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

def get_google_search_links(company_name):
    query1 = quote_plus(f"investing.com {company_name} 최근 발표 실적")
    query2 = quote_plus(f"investing.com {company_name} 최근 의견 예상치")
    link1 = f"https://www.google.com/search?q={query1}"
    link2 = f"https://www.google.com/search?q={query2}"
    return link1, link2

# 웹 스크래핑 함수 수정
def scrape_web(company_name):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    performance_url = f"https://www.google.com/search?q={quote_plus(company_name + ' 최근 발표 실적')}"
    opinions_url = f"https://www.google.com/search?q={quote_plus(company_name + ' 최근 의견 예상치')}"
    
    performance_response = requests.get(performance_url, headers=headers)
    opinions_response = requests.get(opinions_url, headers=headers)
    
    performance_soup = BeautifulSoup(performance_response.text, 'html.parser')
    opinions_soup = BeautifulSoup(opinions_response.text, 'html.parser')
    
    performance = "최근 실적 정보를 찾을 수 없습니다."
    opinions = "애널리스트 의견을 찾을 수 없습니다."
    
    # 구글 검색 결과에서 첫 번째 텍스트 추출
    performance_result = performance_soup.find('div', class_='BNeawe s3v9rd AP7Wnd')
    if performance_result:
        performance = performance_result.text
    
    opinions_result = opinions_soup.find('div', class_='BNeawe s3v9rd AP7Wnd')
    if opinions_result:
        opinions = opinions_result.text
    
    return performance, opinions

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

        # 웹 스크래핑
        company_name = ticker_to_name.get(ticker, ticker)
        performance, opinions = scrape_web(company_name)

        # 프롬프트 준비
        prompt_voo = f"""
        1) 제공된 자료의 수익율(rate)와 S&P 500(VOO)의 수익율(rate_vs)과 비교해서 이격된 정도를 알려줘 (간단하게 자료 맨마지막날의 누적수익율차이):
           리뷰할 주식티커명 = {ticker}
           회사이름과 회사 개요(1줄로)
           리뷰주식의 누적수익률 = {final_rate}
           기준이 되는 비교주식(S&P 500, VOO)의 누적수익율 = {final_rate_vs}
        2) 제공된 자료의 최근 주가 변동(간단하게: 5일, 20일, 60일 이동평균 수치로):
           5일이동평균 = {sma_5}
           20일이동평균 = {sma_20}
           60일이동평균 = {sma_60}
        3) 제공된 자료의 RSI, PPO 인덱스 지표를 분석해줘 (간단하게):
           RSI = {rsi}
           PPO = {ppo}
        4) 최근 실적 및 전망:

           {performance}
        5) 애널리스트 의견:

           {opinions}
        6) 레포트는 ["candidates"][0]["content"]["parts"][0]["text"]의 구조의 텍스트로 만들어줘
        7) 레포트는 한글로 만들어줘
        """

        # Gemini API 호출
        response_ticker = model.generate_content(prompt_voo)

        # 리포트를 텍스트로 저장
        report_text = response_ticker.text
        link1, link2 = get_google_search_links(company_name)
        report_text += f"\nGoogle Search Link 1: [여기를 클릭하세요]({link1})"
        report_text += f"\nGoogle Search Link 2: [여기를 클릭하세요]({link2})"
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
        move_files_to_images_folder()

        return f'Gemini Analysis for {ticker} (VOO) has been sent to Discord and saved as a text file.'

    except Exception as e:
        error_message = f"{ticker} 분석 중 오류 발생: {e}"
        print(error_message)
        response = requests.post(DISCORD_WEBHOOK_URL, data={'content': error_message})
        return error_message

if __name__ == '__main__':
    # HTTP 서버 시작
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # 봇 실행
    asyncio.run(run_bot())

"""
source .venv/bin/activate
python gemini.py    
"""