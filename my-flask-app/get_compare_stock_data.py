# get_compare_stock_data.py

import os
import sys
import pandas as pd
import numpy as np

# 루트 디렉토리를 sys.path에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'my-flutter-app')))

def read_and_process_csv(file_path):
    df = pd.read_csv(file_path)
    df['Date'] = pd.to_datetime(df['Date'])  # Date 열을 datetime 형식으로 변환
    file_name_parts = os.path.splitext(os.path.basename(file_path))[0].split('_')
    ticker = file_name_parts[-1]
    
    # 필요한 열이 존재하는지 확인하고 처리
    if 'rate' in df.columns and 'rate_vs' in df.columns:
        result_df = df[['Date', 'rate', 'rate_vs']].copy()
        result_df = result_df.rename(columns={'rate': f'rate_{ticker}_5D', 'rate_vs': 'rate_VOO_20D'})
    else:
        raise KeyError(f"'rate' or 'rate_vs' columns not found in file: {file_path}")
    
    return result_df

def calculate_divergence(df, ticker):
    # Divergence 계산
    divergence = df[f'rate_{ticker}_5D'] - df['rate_VOO_20D']
    return divergence

def save_simplified_csv(folder_path, df, ticker):
    # Divergence 계산
    divergence = calculate_divergence(df, ticker)
    df['Divergence'] = np.round(divergence, 2)  # 소수점 두 자리로 반올림

    # 최대 및 최소 divergence를 이용하여 Relative_Divergence 계산
    max_divergence = df['Divergence'].max()
    min_divergence = df['Divergence'].min()
    df['Relative_Divergence'] = ((df['Divergence'] - min_divergence) / (max_divergence - min_divergence)) * 100
    df['Relative_Divergence'] = np.round(df['Relative_Divergence'], 2)

    # 간단한 데이터프레임 생성 (20 간격으로 축소)
    simplified_df = df.iloc[::20].reset_index(drop=True)

    simplified_file_path = os.path.join(folder_path, f'result_{ticker}.csv')
    simplified_df.to_csv(simplified_file_path, index=False)
    print(f"Simplified CSV saved: {simplified_file_path}")

def process_all_csv_files(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    all_files = os.listdir(folder_path)
    csv_files = [file for file in all_files if file.startswith('result_VOO_') and file.endswith('.csv')]

    for file in csv_files:
        file_path = os.path.join(folder_path, file)
        print(f"Processing file: {file_path}")
        df_processed = read_and_process_csv(file_path)
        ticker = os.path.splitext(os.path.basename(file_path))[0].split('_')[-1]
        save_simplified_csv(folder_path, df_processed, ticker)

def process_single_ticker(folder_path, ticker):
    file_path = os.path.join(folder_path, f'result_VOO_{ticker}.csv')
    print(f"Processing single ticker: {ticker}")
    df_processed = read_and_process_csv(file_path)
    save_simplified_csv(folder_path, df_processed, ticker)

    # 현재 Divergence와 Relative_Divergence 출력
    latest_entry = df_processed.iloc[-1]
    current_divergence = latest_entry['Divergence']
    max_divergence = df_processed['Divergence'].max()
    min_divergence = df_processed['Divergence'].min()
    current_relative_divergence = latest_entry['Relative_Divergence']
    
    print(f"Current Divergence for {ticker}: {current_divergence} (max {max_divergence}, min {min_divergence})")
    print(f"Current Relative Divergence for {ticker}: {current_relative_divergence}")

if __name__ == "__main__":
    # 루트 디렉토리 경로를 기준으로 설정
    root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    folder_path = os.path.join(root_path, 'static', 'images')
    ticker_to_test = 'TSLA'
    process_single_ticker(folder_path, ticker_to_test)



# python get_compare_stock_data.py