### get_compare_stock_data.py

import os
import pandas as pd
from collections import defaultdict

# 환경 변수에서 CSV URL 가져오기
ticker_path = os.getenv('CSV_URL', 'https://raw.githubusercontent.com/photo2story/my-flutter-app/main/my-flask-app/stock_market.csv')

def load_sector_info():
    sector_df = pd.read_csv(ticker_path, na_values=['', 'NaN'])
    sector_dict = dict(zip(sector_df['Symbol'], sector_df['Sector']))
    return sector_dict

def get_ticker_sector(ticker):
    sector_dict = load_sector_info()
    sector = sector_dict.get(ticker)
    return sector

def read_and_process_csv(file_path, sector_dict):
    df = pd.read_csv(file_path, usecols=['Date', 'rate', 'rate_vs'])
    first_date = df['Date'].iloc[0]
    file_name_parts = os.path.splitext(os.path.basename(file_path))[0].split('_')
    voo_index = file_name_parts.index('VOO')
    new_rate_column = 'rate_' + file_name_parts[voo_index + 1]
    df.rename(columns={'rate': new_rate_column, 'rate_vs': 'rate_VOO'}, inplace=True)

    df['Sector'] = sector_dict.get(file_name_parts[voo_index + 1], 'Unknown')
    return df, first_date

def merge_csv_files(folder_path, sector_dict):
    all_files = os.listdir(folder_path)
    csv_files = [file for file in all_files if file.startswith('result_VOO_') and file.endswith('.csv')]
    date_grouped_dfs = defaultdict(lambda: defaultdict(list))

    for file in csv_files:
        file_path = os.path.join(folder_path, file)
        print(f"Processing file: {file_path}")  # 디버깅 메시지 추가
        df_processed, first_date = read_and_process_csv(file_path, sector_dict)
        date_grouped_dfs[first_date][df_processed['Sector'].iloc[0]].append(df_processed)

    for start_date, sector_group in date_grouped_dfs.items():
        for sector, dfs in sector_group.items():
            df_combined = pd.concat(dfs, axis=1)
            df_combined = df_combined.loc[:, ~df_combined.columns.duplicated()]
            filename = f"{start_date.replace('-', '_')}_{sector}.csv"
            print(f"Saving merged file: {filename}")  # 디버깅 메시지 추가
            df_combined.to_csv(os.path.join(folder_path, filename), index=False)

if __name__ == "__main__":
    ticker = 'NVDA'  # 알고 싶은 특정 티커
    sector = get_ticker_sector(ticker)
    print(f"The sector of {ticker} is {sector}")
    df = pd.read_csv(ticker_path, na_values=['', 'NaN'])
    print(df[df['Symbol'] == 'NVDA'])

