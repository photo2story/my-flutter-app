# Data_export.py

import pandas as pd

def convert_file_path_for_saving(file_path):
    return file_path.replace('/', '-')

def convert_file_path_for_reading(file_path):
    return file_path.replace('-', '/')

def print_results(result, total_account_balance):
    result_df = pd.DataFrame(result, columns=[
        "Date", "price", "Open", "High", "Low", "Close", "Volume", 
        "bb_upper_ta", "bb_lower_ta", "sma05_ta", "sma20_ta", "sma60_ta", 
        "sma120_ta", "sma240_ta", "Recent_high", "aroon_up_ta", 
        "aroon_downp_ta", "ppo_histogram", "SMA_20_turn", "SMA_60_turn", 
        "Recent_low", "account_balance", "deposit", "cash", 
        "portfolio_value", "shares", "rate", "invested_amount", "signal", 
        "rsi_ta", "stochk_ta", "stochd_ta", "stock_ticker"
    ])
    
    pd.set_option('display.float_format', lambda x: f'{x:.2f}')
    print("\nTotal_account_balance: {:,.0f} won".format(total_account_balance))

def export_csv(file_path, result_dict):
    file_path = convert_file_path_for_saving(file_path)
    
    result_df = pd.DataFrame(result_dict['result'], columns=[
        "Date", "price", "Open", "High", "Low", "Close", "Volume", 
        "bb_upper_ta", "bb_lower_ta", "sma05_ta", "sma20_ta", "sma60_ta", 
        "sma120_ta", "sma240_ta", "Recent_high", "aroon_up_ta", 
        "aroon_downp_ta", "ppo_histogram", "SMA_20_turn", "SMA_60_turn", 
        "Recent_low", "account_balance", "deposit", "cash", 
        "portfolio_value", "shares", "rate", "invested_amount", "signal", 
        "rsi_ta", "stochk_ta", "stochd_ta", "stock_ticker"
    ])
    
    # 누락된 값을 0으로 채우기
    result_df.fillna(0, inplace=True)
    
    result_df.to_csv(file_path, float_format='%.2f', index=False)
    return result_df

# # 예제 데이터
# result_dict = {
#     "result": [
#         ["2022-01-01", 100, 102, 105, 99, 101, 1000, 106, 98, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, "AAPL"],
#         # 추가 데이터
#     ]
# }

# # 파일 경로
# file_path = 'results/stock_results.csv'

# # CSV 파일로 내보내기
# df = export_csv(file_path, result_dict)
# print(df)
