## Results_plot_mpl.py

import matplotlib.pyplot as plt
from mplchart.chart import Chart
from mplchart.primitives import Candlesticks, Volume, TradeSpan
from mplchart.indicators import SMA, PPO, RSI
import pandas as pd
import requests
import FinanceDataReader as fdr
from get_ticker import get_ticker_name
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

def save_figure(fig, file_path):
    """파일 경로를 처리하여 그림을 저장하고 닫습니다."""
    file_path = file_path.replace('/', '-')
    fig.savefig(file_path, bbox_inches='tight')
    plt.close(fig)

def plot_results_mpl(ticker, start_date, end_date):
    """주어진 티커와 기간에 대한 데이터를 사용하여 차트를 생성하고, 결과를 Discord로 전송합니다."""
    prices = fdr.DataReader(ticker, start_date, end_date)
    prices.dropna(inplace=True)

    # 이동 평균과 PPO 계산
    SMA20 = prices['Close'].rolling(window=20).mean()
    SMA60 = prices['Close'].rolling(window=60).mean()
    short_ema = prices['Close'].ewm(span=12, adjust=False).mean()
    long_ema = prices['Close'].ewm(span=26, adjust=False).mean()
    ppo = ((short_ema - long_ema) / long_ema) * 100
    ppo_signal = ppo.ewm(span=9, adjust=False).mean()
    ppo_histogram = ppo - ppo_signal

    # 차트 생성
    indicators = [
        Candlesticks(), SMA(20), SMA(60), Volume(),
        RSI(), PPO(), TradeSpan('ppohist>0')
    ]
    name = get_ticker_name(ticker)
    chart = Chart(title=f'{ticker} ({name}) vs VOO', max_bars=250)
    chart.plot(prices, indicators)
    fig = chart.figure
    image_filename = f'result_mpl_{ticker}.png'
    save_figure(fig, image_filename)

    # 메시지 작성
    message = (f"Stock: {ticker} ({name})\n"
               f"Close: {prices['Close'].iloc[-1]:,.2f}\n"
               f"SMA 20: {SMA20.iloc[-1]:,.2f}\n"
               f"SMA 60: {SMA60.iloc[-1]:,.2f}\n"
               f"PPO Histogram: {ppo_histogram.iloc[-1]:,.2f}\n")

    # Discord로 메시지 전송
    response = requests.post(DISCORD_WEBHOOK_URL, data={'content': message})
    if response.status_code != 204:
        print('Discord 메시지 전송 실패')
        print(f"Response: {response.status_code} {response.text}")
    else:
        print('Discord 메시지 전송 성공')

    # Discord로 이미지 전송
    try:
        with open(image_filename, 'rb') as image_file:
            response = requests.post(DISCORD_WEBHOOK_URL, files={'file': image_file})
            if response.status_code in [200, 204]:
                print(f'Graph 전송 성공: {ticker}')
            else:
                print(f'Graph 전송 실패: {ticker}')
                print(f"Response: {response.status_code} {response.text}")
    except Exception as e:
        print(f"Error occurred while sending image: {e}")

if __name__ == "__main__":
    print("Starting test for plotting results.")
    ticker = "AAPL"
    start_date = "2019-01-02"
    end_date = "2024-07-28"
    print(f"Plotting results for {ticker} from {start_date} to {end_date}")

    try:
        plot_results_mpl(ticker, start_date, end_date)
        print("Plotting completed successfully.")
    except Exception as e:
        print(f"Error occurred while plotting results: {e}")


## python Results_plot_mpl.py