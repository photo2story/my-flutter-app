# get_classify_stock.py

import os
import sys
import pandas as pd
import numpy as np
import requests
import io

# 루트 디렉토리를 sys.path에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config
from git_operations import move_files_to_images_folder

GITHUB_RAW_BASE_URL = "https://raw.githubusercontent.com/photo2story/my-flutter-app/main/static/images"

async def fetch_csv(ticker):
    url = f"{GITHUB_RAW_BASE_URL}/result_{ticker}.csv"
    try:
        response = requests.get(url)
        response.raise_for_status()
        df = pd.read_csv(io.StringIO(response.text))
        return df
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch data for {ticker}: {e}")
        return None
    except pd.errors.EmptyDataError:
        print(f"No data found for {ticker}.")
        return None

def classify_stock(rate_avg, divergence_avg, relative_divergence_high_freq):
    if rate_avg > 50:
        if divergence_avg > 10:
            return "HighYieldHighVolatility"
        else:
            return "HighYieldLowVolatility"
    else:
        if divergence_avg > 10:
            return "LowYieldHighVolatility"
        else:
            return "LowYieldLowVolatility"

async def collect_and_classify_stocks():
    tickers = [stock for sector, stocks in config.STOCKS.items() for stock in stocks]
    classification_results = pd.DataFrame(columns=['Ticker', 'Category'])
    
    for ticker in tickers:
        df = await fetch_csv(ticker)
        if df is not None and f'rate_{ticker}_5D' in df.columns:
            rate_avg = df[f'rate_{ticker}_5D'].mean()
            divergence_avg = df['Divergence'].mean()
            relative_divergence_high_freq = df[df['Relative_Divergence'] > 50].shape[0] / df.shape[0]

            category = classify_stock(rate_avg, divergence_avg, relative_divergence_high_freq)
            classification_results = pd.concat([classification_results, pd.DataFrame({'Ticker': [ticker], 'Category': [category]})], ignore_index=True)
        else:
            print(f"Data for {ticker} is not available or missing necessary columns.")
    
    # 결과를 CSV 파일로 저장
    folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static', 'images'))
    classification_results_path = os.path.join(folder_path, f'classification_results.csv')
    classification_results.to_csv(classification_results_path, index=False)

    print(classification_results)
    
    # 파일 이동 및 깃 커밋 푸시 작업
    await move_files_to_images_folder()
    
    return classification_results

if __name__ == "__main__":
    import asyncio
    asyncio.run(collect_and_classify_stocks())

# python get_classify_stock.py