## Results_plot_mpl.py


import yfinance as yf
import matplotlib.pyplot as plt
from mplchart.chart import Chart
from mplchart.primitives import Candlesticks, Volume, TradeSpan
from mplchart.indicators import SMA, PPO, RSI
import pandas_ta as ta
import pandas as pd
import requests
import numpy as np
import FinanceDataReader as fdr
from datetime import datetime
from get_ticker import get_ticker_name
from github_operations import save_csv_to_github, save_image_to_github
import os
from dotenv import load_dotenv

load_dotenv()
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

def save_figure(fig, file_path):
    file_path = file_path.replace('/', '-')
    fig.savefig(file_path, bbox_inches='tight')
    plt.close(fig)

def plot_results_mpl(ticker, start_date, end_date):
    prices = fdr.DataReader(ticker, start_date, end_date)
    max_bars = 250
    prices.dropna(inplace=True)

    SMA20 = prices['Close'].rolling(window=20).mean()
    SMA60 = prices['Close'].rolling(window=60).mean()

    short_ema = prices['Close'].ewm(span=12, adjust=False).mean()
    long_ema = prices['Close'].ewm(span=26, adjust=False).mean()
    ppo = ((short_ema - long_ema) / long_ema) * 100
    ppo_signal = ppo.ewm(span=9, adjust=False).mean()
    ppo_histogram = ppo - ppo_signal

    indicators = [
        Candlesticks(), SMA(20), SMA(60), Volume(),
        RSI(), PPO(), TradeSpan('ppohist>0')
    ]

    name = get_ticker_name(ticker)
    chart = Chart(title=f'{ticker} ({name}) vs VOO', max_bars=max_bars)
    chart.plot(prices, indicators)

    fig = chart.figure
    image_filename = f'result_mpl_{ticker}.png'
    save_figure(fig, image_filename)

    # Discord로 이미지 및 메시지 전송
    message = (f"Stock: {ticker} ({name})\n"
               f"Close: {prices['Close'].iloc[-1]:,.2f}\n"
               f"SMA 20: {SMA20.iloc[-1]:,.2f}\n"
               f"SMA 60: {SMA60.iloc[-1]:,.2f}\n"
               f"PPO Histogram: {ppo_histogram.iloc[-1]:,.2f}\n")
    
    response = requests.post(DISCORD_WEBHOOK_URL, data={'content': message})
    if response.status_code != 204:
        print('Discord 메시지 전송 실패')
        print(f"Response: {response.status_code} {response.text}")
    else:
        print('Discord 메시지 전송 성공')

    # 이미지 파일 전송
    with open(image_filename, 'rb') as image_file:
        response = requests.post(DISCORD_WEBHOOK_URL, files={'file': image_file})
        if response.status_code != 204:
            print(f'Graph 전송 실패: {ticker}')
            print(f"Response: {response.status_code} {response.text}")
        else:
            print(f'Graph 전송 성공: {ticker}')

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