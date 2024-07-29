# Results_plot.py

# Results_plot.py

import matplotlib.dates as dates
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import os
import requests
import glob
import asyncio
import pandas as pd
import time  # 추가

from get_ticker import get_ticker_name, is_valid_stock
from Results_plot_mpl import plot_results_mpl

def convert_file_path_for_saving(file_path):
    return file_path.replace('/', '-')

def convert_file_path_for_reading(file_path):
    return file_path.replace('-', '/')

def save_figure(fig, file_path):
    file_path = convert_file_path_for_saving(file_path)
    fig.savefig(file_path, bbox_inches='tight')
    plt.close(fig)  # 닫지 않으면 메모리를 계속 차지할 수 있음

from PIL import Image

def load_image(file_path):
    file_path = convert_file_path_for_reading(file_path)
    image = Image.open(file_path)
    return image

def plot_comparison_results(file_path1, file_path2, stock1, stock2, total_account_balance, total_rate, str_strategy, invested_amount, min_stock_data_date):
    fig, ax2 = plt.subplots(figsize=(8, 6))

    # 전체 데이터셋 파일 경로
    full_path1 = os.path.abspath(file_path1)
    full_path2 = os.path.abspath(file_path2)
    print(f"Reading full dataset for graph from: {full_path1} and {full_path2}")

    # 그래프용 데이터프레임 로드 (전체 자료)
    df1_graph = pd.read_csv(full_path1, parse_dates=['Date'], index_col='Date')
    df2_graph = pd.read_csv(full_path2, parse_dates=['Date'], index_col='Date')

    # Last Signal을 가져오기 위한 수정된 부분
    last_signal_row = df1_graph.dropna(subset=['signal']).iloc[-1] if 'signal' in df1_graph.columns else None
    last_signal = last_signal_row['signal'] if last_signal_row is not None else 'N/A'

    current_signal = df1_graph['ppo_histogram'].iloc[-1] if 'ppo_histogram' in df1_graph.columns else 'N/A'

    # 간략화된 데이터프레임 로드 (이격 결과)
    simplified_df_path1 = os.path.join(os.path.dirname(full_path1), 'static', 'images', f'result_{stock1}.csv')
    print(f"Attempting to read simplified dataset for divergence from: {simplified_df_path1}")

    try:
        df1 = pd.read_csv(simplified_df_path1, parse_dates=['Date'], index_col='Date')
    except FileNotFoundError as e:
        print(f"Error: {e}")
        raise

    start_date = min_stock_data_date
    end_date = min(df1_graph.index.max(), df2_graph.index.max())

    df1_graph = df1_graph.loc[start_date:end_date]
    df2_graph = df2_graph.loc[start_date:end_date]

    df1_graph['rate_7d_avg'] = df1_graph['rate'].rolling('7D').mean()
    df2_graph['rate_20d_avg'] = df2_graph['rate_vs'].rolling('20D').mean()

    ax2.plot(df1_graph.index, df1_graph['rate_7d_avg'], label=f'{stock1} 7-Day Avg Return')
    ax2.plot(df2_graph.index, df2_graph['rate_20d_avg'], label=f'{stock2} 20-Day Avg Return')
    
    # 레이블, 제목, 범례 설정
    plt.ylabel('rate (%)')
    plt.legend(loc='upper left')

    voo_rate = df2_graph['rate_vs'].iloc[-1] if not df2_graph.empty else 0

    max_divergence = df1['Divergence'].max()
    min_divergence = df1['Divergence'].min()
    current_divergence = df1['Divergence'].iloc[-1]
    relative_divergence = df1['Relative_Divergence'].iloc[-1]
    



    plt.title(f"{stock1} ({get_ticker_name(stock1)}) vs {stock2}\n" +
              f"Total Rate: {total_rate:.2f}% (VOO: {voo_rate:.2f}%)), Relative_Divergence: {relative_divergence:.2f}%\n" +
              f"Current Divergence: {current_divergence:.2f} (max: {max_divergence:.2f}, min: {min_divergence:.2f})\n" +
              f"Current Signal(PPO): {current_signal}, Last Signal: {str_strategy}",
              pad=10)

    ax2.xaxis.set_major_locator(dates.YearLocator())
    plt.xlabel('Year')

    save_path = f'comparison_{stock1}_{stock2}.png'
    plt.subplots_adjust(top=0.8)
    fig.savefig(save_path)
    plt.cla()
    plt.clf()
    plt.close(fig)

    # Discord 메시지
    DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')
    message = f"Stock: {stock1} ({get_ticker_name(stock1)}) vs {stock2}\n" \
              f"Total Rate: {total_rate:.2f}% (VOO: {voo_rate:.2f}%), Relative_Divergence: {relative_divergence:.2f}\n" \
              f"Current Divergence: {current_divergence:.2f} (max: {max_divergence:.2f}, min: {min_divergence:.2f})\n" \
              f"Current Signal(PPO): {current_signal}, Last Signal: {str_strategy}"
    response = requests.post(DISCORD_WEBHOOK_URL, data={'content': message})

    if response.status_code != 204:
       print('Discord 메시지 전송 실패')
    else:
       print('Discord 메시지 전송 성공')

    files = {'file': open(save_path, 'rb')}
    response = requests.post(DISCORD_WEBHOOK_URL, files=files)




async def plot_results_all():
    DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')
    github_api_url = 'https://api.github.com/repos/photo2story/my-flutter-app/contents/static/images'
    
    # GitHub API를 통해 이미지 파일 목록 가져오기
    response = requests.get(github_api_url)
    if response.status_code != 200:
        print('GitHub API 요청 실패')
        return
    
    images = response.json()
    image_files = [img['download_url'] for img in images if img['name'].startswith('comparison_') and img['name'].endswith('.png')]
    
    for image_url in image_files:
        stock = image_url.split('comparison_')[1].split('_VOO.png')[0]
        name = get_ticker_name(stock)
        
        # 해당 주식의 CSV 파일 경로 생성
        csv_file_path = f"static/images/result_VOO_{stock}.csv"
        
        if os.path.exists(csv_file_path):
            df = pd.read_csv(csv_file_path)
            last_row = df.iloc[-1]
            total_account_balance = last_row['account_balance']
            total_rate = last_row['rate']
            invested_amount = last_row['invested_amount']
            str_last_signal = last_row['signal']

            # 결과 메시지 전송
            message = {
                'content': f"Stock: {stock} ({name})\n"
                           f"Invested_amount: {invested_amount:,.0f} $\n"
                           f"Total_account_balance: {total_account_balance:,.0f} $\n"
                           f"Total_rate: {total_rate:,.0f} %\n"
                           f"Last_signal: {str_last_signal}"
            }
            response = requests.post(DISCORD_WEBHOOK_URL, json=message)
            if response.status_code != 204:
                print('Discord 메시지 전송 실패')
                print(response.status_code)
                print(response.text)
            else:
                print('Discord 메시지 전송 성공')

        # GitHub에서 이미지 파일 가져오기
        image_response = requests.get(image_url)
        if image_response.status_code != 200:
            print(f'Graph 전송 실패: {stock}')
            continue

        image_data = image_response.content
        files = {'image': ('image.png', image_data, 'image/png')}
        response = requests.post(DISCORD_WEBHOOK_URL, files=files)
        if response.status_code != 204:
            print(f'Graph 전송 실패: {stock}')
            print(response.status_code)
            print(response.text)
        else:
            print(f'Graph 전송 성공: {stock}')

        await asyncio.sleep(1)  # 1초 대기

if __name__ == "__main__":
    # 테스트용 예시 데이터 설정
    folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static', 'images'))
    stock1 = "AAPL"
    stock2 = "VOO"
    total_account_balance = 1000000  # 예시 값
    total_rate = 25.0  # 예시 값
    str_strategy = "Buy and Hold"  # 예시 전략
    invested_amount = 500000  # 예시 초기 투자금
    min_stock_data_date = "2019-01-02"  # 예시 시작 날짜

    # 파일 경로 설정
    file_path1 = os.path.join(folder_path, f'result_VOO_{stock1}.csv')
    file_path2 = os.path.join(folder_path, f'result_VOO_{stock2}.csv')

    # plot_comparison_results 함수 호출
    plot_comparison_results(file_path1, file_path2, stock1, stock2, total_account_balance, total_rate, str_strategy, invested_amount, min_stock_data_date)

    # python Results_plot.py
