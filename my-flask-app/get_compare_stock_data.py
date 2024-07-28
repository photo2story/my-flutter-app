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

def save_simplified_csv(folder_path, df, ticker):
    # 이동 평균 계산
    rate_ticker = df[f'rate_{ticker}_5D'].rolling(window=5).mean().fillna(0).to_numpy()
    rate_VOO_20D = df['rate_VOO_20D'].rolling(window=20).mean().fillna(0).to_numpy()

    # 소수점 두 자리로 반올림
    rate_ticker = np.round(rate_ticker, 2)
    rate_VOO_20D = np.round(rate_VOO_20D, 2)

    # 간단한 데이터프레임 생성 (20 간격으로 축소)
    simplified_df = pd.DataFrame({
        'Date': df['Date'].iloc[::20].reset_index(drop=True),
        f'rate_{ticker}_5D': rate_ticker[::20],
        'rate_VOO_20D': rate_VOO_20D[::20]
    })

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

if __name__ == "__main__":
    # Set a flag or environment variable for testing
    is_test = os.getenv('TEST_ENV', 'False').lower() in ('true', '1', 't')
    
    if is_test:
        # Folder path for testing
        folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'test_data'))
        print("Running in test mode...")
        process_all_csv_files(folder_path)
    else:
        print("Not running in test mode. Skipping processing.")


# python get_compare_stock_data.py