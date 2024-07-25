# get_compare_stock_data.py

import os
import sys
import pandas as pd
from collections import defaultdict

# 루트 디렉토리를 sys.path에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def load_sector_info():
    sector_df = pd.read_csv('stock_market.csv')
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
    if not os.path.exists(folder_path):
        print(f"Folder path '{folder_path}' does not exist. Creating the directory.")
        os.makedirs(folder_path)  # 폴더 경로가 존재하지 않을 경우 생성
    
    all_files = os.listdir(folder_path)
    csv_files = [file for file in all_files if file.startswith('result_VOO_') and file.endswith('.csv')]
    date_grouped_dfs = defaultdict(lambda: defaultdict(list))

    for file in csv_files:
        file_path = os.path.join(folder_path, file)
        print(f"Processing file: {file_path}")  # 디버깅 메시지 추가
        df_processed, first_date = read_and_process_csv(file_path, sector_dict)
        print(f"Processed DataFrame columns: {df_processed.columns.tolist()}")  # 각 데이터프레임의 열 확인
        date_grouped_dfs[first_date][df_processed['Sector'].iloc[0]].append(df_processed)

    total_df = pd.DataFrame()

    for start_date, sector_group in date_grouped_dfs.items():
        for sector, dfs in sector_group.items():
            df_combined = pd.concat(dfs, axis=1)
            df_combined = df_combined.loc[:, ~df_combined.columns.duplicated()]
            filename = f"{start_date.replace('-', '_')}_{sector}.csv"
            print(f"Saving merged file: {filename}")  # 디버깅 메시지 추가
            df_combined.to_csv(os.path.join(folder_path, filename), index=False)

            # 디버깅 메시지: df_combined의 열 출력
            print(f"Columns in df_combined ({sector}): {df_combined.columns.tolist()}")

            # 전체 데이터를 하나의 DataFrame에 추가
            if total_df.empty:
                total_df = df_combined
            else:
                df_combined.drop(columns=['rate_VOO'], inplace=True, errors='ignore')  # total_df에 이미 포함된 열 제외
                try:
                    total_df = pd.merge(total_df, df_combined, on=['Date', 'Sector'], how='outer')
                except KeyError as e:
                    print(f"Error merging dataframes: {e}")
                    continue

    # 디버깅 메시지 추가: 'Date' 열이 존재하는지 확인
    print(f"Columns in total_df: {total_df.columns.tolist()}")

    # NaN 값을 이전 값으로 채우기
    if 'Date' in total_df.columns:
        total_df.ffill(inplace=True)
        total_df.sort_values(by='Date', inplace=True)
        total_output_file = os.path.join(folder_path, f'{start_date.replace("-", "_")}_total.csv')
        total_df.to_csv(total_output_file, index=False)
        print(f"Total merged file saved as: {total_output_file}")
    else:
        print("Error: 'Date' column not found in the merged DataFrame.")

if __name__ == "__main__":
    # 프로젝트 루트에서의 상대 경로
    folder_path = os.path.join(os.getcwd(), 'static', 'images')
    sector_dict = load_sector_info()
    merge_csv_files(folder_path, sector_dict)



# python get_compare_stock_data.py