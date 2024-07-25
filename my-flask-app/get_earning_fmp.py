import os
import requests
import pandas as pd
from dotenv import load_dotenv

# .env 파일의 환경 변수를 로드합니다.
load_dotenv()

API_KEY = os.getenv('FMP_API_KEY')  # .env 파일에서 API 키를 가져옵니다
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')  # .env 파일에서 디스코드 웹훅 URL을 가져옵니다

if not API_KEY:
    raise ValueError("API 키가 설정되지 않았습니다. .env 파일을 확인하세요.")

if not DISCORD_WEBHOOK_URL:
    raise ValueError("DISCORD 웹훅 URL이 설정되지 않았습니다. .env 파일을 확인하세요.")

def get_earnings_data(ticker):
    url = f'https://financialmodelingprep.com/api/v3/earnings-surprises/{ticker}?apikey={API_KEY}'
    
    response = requests.get(url)
    
    if response.status_code != 200:
        raise Exception(f"API 요청 실패: {response.status_code}")
    
    try:
        data = response.json()
        return data
    except ValueError as e:
        print('Error parsing JSON:', e)
        return None

def get_recent_earnings(ticker, num_entries=5):
    earnings_data = get_earnings_data(ticker)
    
    if earnings_data:
        df = pd.DataFrame(earnings_data)
        
        # 최근 num_entries개의 데이터만 선택
        df = df.head(num_entries)
        
        return df
    else:
        return pd.DataFrame()

def send_to_discord(message):
    data = {
        "content": message
    }
    response = requests.post(DISCORD_WEBHOOK_URL, json=data)
    if response.status_code != 204:
        raise Exception(f"Failed to send message to Discord: {response.status_code}, {response.text}")

def main():
    ticker = 'TSLA'
    recent_earnings = get_recent_earnings(ticker)
    
    if not recent_earnings.empty:
        print("Recent Earnings Data:")
        print(recent_earnings)
        
        # 데이터 프레임을 CSV 파일로 저장
        recent_earnings.to_csv(f'{ticker}_recent_earnings.csv', index=False)
        print(f"Data saved to {ticker}_recent_earnings.csv")
        
        # 디스코드로 메시지 보내기
        message = f"Recent Earnings Data for {ticker}:\n{recent_earnings.to_string(index=False)}"
        send_to_discord(message)
        print("Data sent to Discord.")
    else:
        print("No earnings data found.")

if __name__ == "__main__":
    main()


# python get_earning_fmp.py    