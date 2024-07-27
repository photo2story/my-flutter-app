# estimate_stock.py

from Get_data import get_stock_data
import My_strategy
from Data_export import export_csv
import os, sys
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv

# 루트 디렉토리를 sys.path에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import configuration
import config

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

def estimate_snp(stock1, stock2, min_stock_data_date, end_date, initial_investment, monthly_investment, option_strategy, result_df):
    stock_data, min_stock_data_date = get_stock_data(stock2, min_stock_data_date, end_date)
    print(VOO_PERFORMANCE_FILE_PATH)
    try:
        # 기존 VOO 퍼포먼스 데이터가 유효한 경우
        voo_performance_data = pd.read_csv(VOO_PERFORMANCE_FILE_PATH, index_col='Date', parse_dates=True)
        if not is_date_range_matching(VOO_PERFORMANCE_FILE_PATH, min_stock_data_date, end_date):
            raise ValueError("Date range mismatch")
        voo_performance_data = voo_performance_data[['rate_vs']]
        print("Loaded existing VOO performance data.")
    except (FileNotFoundError, ValueError):
        print("Generating new VOO performance data...")
        # VOO 데이터 가져오기 및 백테스트 수행
        result_dict2 = My_strategy.my_strategy(stock_data, initial_investment, monthly_investment, option_strategy)



    # 결과 CSV 파일로 저장하기
    safe_ticker = stock1.replace('/', '-')
    file_path = 'result_VOO_{}.csv'.format(safe_ticker)  # VOO_TSLA(stock1).csv
    result_df2 = export_csv(file_path, result_dict2)
    
    # result_df2의 'rate' 컬럼 이름을 'rate_vs'로 변경
    result_df2.rename(columns={'rate': 'rate_vs'}, inplace=True)
    
    # 누락된 값을 0으로 채우기
    result_df2.fillna(0, inplace=True)
  
    # result_df와 result_df2를 합치기 (여기서는 인덱스를 기준으로 합침)
    combined_df = result_df.join(result_df2['rate_vs'])
    combined_df.fillna(0, inplace=True)  # 누락된 값을 0으로 채우기
    combined_df.to_csv(file_path, float_format='%.2f', index=False)

    return file_path

# 테스트 코드
if __name__ == "__main__":
    print(config.VOO_PERFORMANCE_FILE_PATH)
    
    
# python estimate_stock.py    