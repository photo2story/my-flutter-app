# get_compare_stock_data.py
import os
import sys
import pandas as pd
from collections import defaultdict

# 루트 디렉토리를 sys.path에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'my-flutter-app')))

def load_sector_info():
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'images', 'stock_market.csv')
    sector_df = pd.read_csv(csv_path)
    sector_dict = dict(zip(sector_df['Symbol'], sector_df['Sector']))
    return sector_dict

def read_and_process_csv(file_path, sector_dict):
    df = pd.read_csv(file_path, usecols=['Date', 'rate', 'rate_vs'])
    first_date = df['Date'].iloc[0]
    file_name_parts = os.path.splitext(os.path.basename(file_path))[0].split('_')
    ticker = file_name_parts[-1]
    new_rate_column = 'rate_' + ticker
    df.rename(columns={'rate': new_rate_column, 'rate_vs': 'rate_VOO'}, inplace=True)
    
    # Sector 열 추가
    df['Sector'] = sector_dict.get(ticker, 'Unknown')
    return df, first_date

def merge_csv_files(folder_path, sector_dict):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    all_files = os.listdir(folder_path)
    csv_files = [file for file in all_files if file.startswith('result_VOO_') and file.endswith('.csv')]
    date_grouped_dfs = defaultdict(lambda: defaultdict(list))

    for file in csv_files:
        file_path = os.path.join(folder_path, file)
        df_processed, first_date = read_and_process_csv(file_path, sector_dict)
        date_grouped_dfs[first_date][df_processed['Sector'].iloc[0]].append(df_processed)

    total_df = pd.DataFrame()

    for start_date, sector_group in date_grouped_dfs.items():
        for sector, dfs in sector_group.items():
            df_combined = pd.concat(dfs, axis=1)
            df_combined = df_combined.loc[:, ~df_combined.columns.duplicated()]
            filename = f"{start_date.replace('-', '_')}_{sector}.csv"
            df_combined.to_csv(os.path.join(folder_path, filename), index=False)

            # 전체 데이터를 하나의 DataFrame에 추가
            if total_df.empty:
                total_df = df_combined
            else:
                df_combined.drop(columns=['rate_VOO', 'Sector'], inplace=True, errors='ignore')
                try:
                    total_df = pd.merge(total_df, df_combined, on='Date', how='outer')
                except KeyError as e:
                    print(f"Error merging dataframes: {e}")
                    continue

    # NaN 값을 이전 값으로 채우기
    if 'Date' in total_df.columns:
        total_df.ffill(inplace=True)
        total_df.sort_values(by='Date', inplace=True)
        total_output_file = os.path.join(folder_path, f'{start_date.replace("-", "_")}_total.csv')
        total_df.to_csv(total_output_file, index=False)
    else:
        print("Error: 'Date' column not found in the merged DataFrame.")

if __name__ == "__main__":
    folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static', 'images'))
    sector_dict = load_sector_info()
    merge_csv_files(folder_path, sector_dict)


# python get_compare_stock_data.py