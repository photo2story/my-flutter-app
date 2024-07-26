# get_compare_stock_data.py
import os
import sys
import pandas as pd

# 루트 디렉토리를 sys.path에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'my-flutter-app')))

def load_sector_info():
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'images', 'stock_market.csv')
    sector_df = pd.read_csv(csv_path)
    sector_dict = dict(zip(sector_df['Symbol'], sector_df['Sector']))
    return sector_dict

def read_and_process_csv(file_path):
    df = pd.read_csv(file_path, usecols=['Date', 'rate', 'rate_vs'])
    df['Date'] = pd.to_datetime(df['Date'])  # Date 열을 datetime 형식으로 변환
    file_name_parts = os.path.splitext(os.path.basename(file_path))[0].split('_')
    ticker = file_name_parts[-1]
    new_rate_column = 'rate_' + ticker
    df.rename(columns={'rate': new_rate_column, 'rate_vs': 'rate_VOO'}, inplace=True)
    return df

def save_simplified_csv(folder_path, df, ticker):
    # 'Date' 열을 인덱스로 설정
    df.set_index('Date', inplace=True)

    # 단일 열을 선택하여 이동 평균 계산
    rate_col = df[f'rate_{ticker}'].squeeze()
    rate_5D = rate_col.rolling(window=5).mean()
    rate_20D = rate_col.rolling(window=20).mean()

    rate_voo_col = df['rate_VOO'].squeeze()
    rate_VOO_5D = rate_voo_col.rolling(window=5).mean()
    rate_VOO_20D = rate_voo_col.rolling(window=20).mean()

    # 간단한 데이터프레임 생성
    simplified_df = pd.DataFrame({
        'Date': df.index,  # Date를 인덱스로 설정
        f'rate_{ticker}_5D': rate_5D.values,
        f'rate_{ticker}_20D': rate_20D.values,
        'rate_VOO_5D': rate_VOO_5D.values,
        'rate_VOO_20D': rate_VOO_20D.values
    })

    simplified_file_path = os.path.join(folder_path, f'result_{ticker}_simplified.csv')
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
    folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static', 'images'))
    process_all_csv_files(folder_path)


# python get_compare_stock_data.py