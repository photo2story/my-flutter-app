# estimate_stock.py

from Get_data import get_stock_data
import My_strategy
from Data_export import export_csv
import os
from datetime import datetime
import pandas as pd
from git_operations import move_files_to_images_folder  # 함수 임포트 추가

async def estimate_stock(stock, start_date, end_date, initial_investment, monthly_investment, option_strategy):
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

    # 파일 이동 및 깃헙 커밋/푸시
    await move_files_to_images_folder()

    return total_account_balance, total_rate, str_strategy, invested_amount, str_last_signal, min_stock_data_date, file_path, result_df

async def estimate_snp(stock1, stock2, min_stock_data_date, end_date, initial_investment, monthly_investment, option_strategy, result_df):
    stock_data, min_stock_data_date = get_stock_data(stock2, min_stock_data_date, end_date)

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

    # 파일 이동 및 깃헙 커밋/푸시
    await move_files_to_images_folder()

    return file_path

