# estimate_stock.py
import requests
from Get_data import get_stock_data
import My_strategy
from Data_export import export_csv
import os, sys
import certifi
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv

# 루트 디렉토리를 sys.path에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import configuration
import config

os.environ['SSL_CERT_FILE'] = certifi.where()

def estimate_stock(stock, start_date, end_date, initial_investment, monthly_investment, option_strategy):
    stock_data, min_stock_data_date = get_stock_data(stock, start_date, end_date)
    print('estimate_stock.1:', stock)
    
    result_dict = My_strategy.my_strategy(stock_data, initial_investment, monthly_investment, option_strategy)

    total_account_balance = result_dict['Total_account_balance']
    invested_amount = result_dict['Invested_amount']
    total_rate = result_dict['Total_rate']
    str_strategy = result_dict['Strategy']
    str_last_signal = result_dict['Last_signal']

    # 결과 CSV 파일로 저장하기
    safe_ticker = stock.replace('/', '-')  # 슬래시를 하이픈으로 변경
    file_path = 'result_VOO_{}.csv'.format(safe_ticker)  # VOO_TSLA.csv
    print('file_path:', file_path)
    result_df = export_csv(file_path, result_dict)
    print('estimate_stock:', stock)

    return total_account_balance, total_rate, str_strategy, invested_amount, str_last_signal, min_stock_data_date, file_path, result_df

def is_date_range_matching(file_path, min_stock_data_date, end_date):
    """파일에 저장된 데이터의 날짜 범위가 주어진 날짜 범위와 일치하는지 확인합니다."""
    df = pd.read_csv(file_path, parse_dates=['Date'])
    file_min_date = df['Date'].min()
    file_max_date = df['Date'].max()
    return file_min_date == min_stock_data_date and file_max_date == end_date

def estimate_snp(stock1, stock2, min_stock_data_date, end_date, initial_investment, monthly_investment, option_strategy, result_df):
    stock_data, min_stock_data_date = get_stock_data(stock2, min_stock_data_date, end_date)

    print(config.VOO_PERFORMANCE_FILE_PATH)

    try:
        # 기존 VOO 퍼포먼스 데이터가 유효한 경우
        result_df2 = pd.read_csv(config.VOO_PERFORMANCE_FILE_PATH, index_col='Date', parse_dates=True)
        if not is_date_range_matching(config.VOO_PERFORMANCE_FILE_PATH, min_stock_data_date, end_date):
            raise ValueError("Date range mismatch")
        print("Date range VOO performance data ok.")
        result_df2 = result_df2[['rate_vs']]  # 'rate_vs' 열만 선택하여 사용
        print("Loaded existing VOO performance data.")
    except (FileNotFoundError, ValueError):
        print("Generating new VOO performance data...")
        stock_data, _ = get_stock_data(stock2, min_stock_data_date, end_date)
        result_dict2 = My_strategy.my_strategy(stock_data, initial_investment, monthly_investment, option_strategy)
        result_df2 = pd.DataFrame(result_dict2['result'])
        result_df2['rate_vs'] = result_df2['rate']
        result_df2.to_csv(config.VOO_PERFORMANCE_FILE_PATH)  # 새 데이터 저장

    # 결과 CSV 파일로 저장하기
    safe_ticker = stock1.replace('/', '-')
    file_path = 'result_comparison_{}.csv'.format(safe_ticker)  # VOO_TSLA(stock1).csv
    result_df2.to_csv(file_path)  # 'rate_vs' 열 포함하여 저장
    
    # result_df와 result_df2를 합치기 (여기서는 인덱스를 기준으로 합침)
    combined_df = result_df.join(result_df2['rate_vs'])
    combined_df.fillna(0, inplace=True)  # 누락된 값을 0으로 채우기
    combined_df.to_csv(file_path, float_format='%.2f', index=False)

    return file_path

    # result_df와 result_df2를 합치기 (여기서는 인덱스를 기준으로 합침)
    combined_df = result_df.join(result_df2['rate_vs'])
    combined_df.fillna(0, inplace=True)  # 누락된 값을 0으로 채우기
    combined_df.to_csv(file_path, float_format='%.2f', index=False)

    return file_path

# 테스트 코드
if __name__ == "__main__":
    try:
        print(f"VOO Performance File Path: {config.VOO_PERFORMANCE_FILE_PATH}")
        voo_performance_data = pd.read_csv(config.VOO_PERFORMANCE_FILE_PATH, index_col='Date', parse_dates=True)
        print("Successfully loaded VOO performance data.")
        print(voo_performance_data.head())  # 데이터의 일부를 출력하여 제대로 로드되었는지 확인
    except FileNotFoundError:
        print(f"File not found: {config.VOO_PERFORMANCE_FILE_PATH}")
    except ValueError as ve:
        print(f"ValueError: {ve}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    
# python estimate_stock.py    