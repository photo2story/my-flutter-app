# Results_plot.py

import matplotlib.dates as dates
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import os
import requests
from dotenv import load_dotenv
from PIL import Image

from get_ticker import get_ticker_name, is_valid_stock
from Results_plot_mpl import plot_results_mpl

load_dotenv()
GITHUB_RAW_BASE_URL = os.getenv('GITHUB_RAW_BASE_URL', 'https://raw.githubusercontent.com/photo2story/my-flutter-app/main/static/images')

def convert_file_path_for_saving(file_path):
    return file_path.replace('/', '-')

def convert_file_path_for_reading(file_path):
    return file_path.replace('-', '/')

def save_figure(fig, file_path):
    file_path = convert_file_path_for_saving(file_path)
    fig.savefig(file_path, bbox_inches='tight')
    plt.close(fig)  # 닫지 않으면 메모리를 계속 차지할 수 있음

def load_image(file_path):
    file_path = convert_file_path_for_reading(file_path)
    image = Image.open(file_path)
    return image

def plot_comparison_results(ticker, start_date=None, end_date=None):
    fig, ax2 = plt.subplots(figsize=(8, 6))
    
    # Define stock2 as the benchmark
    stock2 = 'VOO'

    full_path1 = f"static/images/result_VOO_{ticker}.csv"
    full_path2 = f"static/images/result_VOO_{stock2}.csv"
    simplified_df_path1 = f"static/images/result_{ticker}.csv"

    print(f"Reading full dataset for graph from: {full_path1} and {full_path2}")
    
    df1_graph = pd.read_csv(full_path1, parse_dates=['Date'], index_col='Date')
    df2_graph = pd.read_csv(full_path2, parse_dates=['Date'], index_col='Date')

    last_signal_row = df1_graph.dropna(subset=['signal']).iloc[-1] if 'signal' in df1_graph.columns else None
    last_signal = last_signal_row['signal'] if last_signal_row is not None else 'N/A'
    current_signal = df1_graph['ppo_histogram'].iloc[-1] if 'ppo_histogram' in df1_graph.columns else 'N/A'

    try:
        df1 = pd.read_csv(simplified_df_path1, parse_dates=['Date'], index_col='Date')
    except FileNotFoundError as e:
        print(f"Error: {e}")
        raise

    if start_date is None:
        start_date = df1_graph.index.min()
    if end_date is None:
        end_date = min(df1_graph.index.max(), df2_graph.index.max())

    df1_graph = df1_graph.loc[start_date:end_date]
    df2_graph = df2_graph.loc[start_date:end_date]

    df1_graph['rate_7d_avg'] = df1_graph['rate'].rolling('7D').mean()
    df2_graph['rate_20d_avg'] = df2_graph['rate_vs'].rolling('20D').mean()

    ax2.plot(df1_graph.index, df1_graph['rate_7d_avg'], label=f'{ticker} 7-Day Avg Return')
    ax2.plot(df2_graph.index, df2_graph['rate_20d_avg'], label=f'{stock2} 20-Day Avg Return')
    
    plt.ylabel('rate (%)')
    plt.legend(loc='upper left')

    voo_rate = df2_graph['rate_vs'].iloc[-1] if not df2_graph.empty else 0
    max_divergence = df1['Divergence'].max()
    min_divergence = df1['Divergence'].min()
    current_divergence = df1['Divergence'].iloc[-1]
    relative_divergence = df1['Relative_Divergence'].iloc[-1]

    plt.title(f"{ticker} ({get_ticker_name(ticker)}) vs {stock2}\n" +
              f"Total Rate: {df1_graph['rate'].iloc[-1]:.2f}% (VOO: {voo_rate:.2f}%), Relative_Divergence: {relative_divergence:.2f}%\n" +
              f"Current Divergence: {current_divergence:.2f} (max: {max_divergence:.2f}, min: {min_divergence:.2f})\n" +
              f"Current Signal(PPO): {current_signal}, Last Signal: {last_signal}",
              pad=10)

    ax2.xaxis.set_major_locator(dates.YearLocator())
    plt.xlabel('Year')

    save_path = f'comparison_{ticker}_{stock2}.png'
    plt.subplots_adjust(top=0.8)
    fig.savefig(save_path)
    plt.cla()
    plt.clf()
    plt.close(fig)

    DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')
    message = f"Stock: {ticker} ({get_ticker_name(ticker)}) vs {stock2}\n" \
              f"Total Rate: {df1_graph['rate'].iloc[-1]:.2f}% (VOO: {voo_rate:.2f}%), Relative_Divergence: {relative_divergence:.2f}\n" \
              f"Current Divergence: {current_divergence:.2f} (max: {max_divergence:.2f}, min: {min_divergence:.2f})\n" \
              f"Current Signal(PPO): {current_signal}, Last Signal: {last_signal}"
    response = requests.post(DISCORD_WEBHOOK_URL, data={'content': message})

    if response.status_code != 204:
        print('Discord 메시지 전송 실패')
    else:
        print('Discord 메시지 전송 성공')

    # 이미지 파일 전송
    with open(save_path, 'rb') as image:
        response = requests.post(
            DISCORD_WEBHOOK_URL,
            files={'image': image}
        )
        if response.status_code != 204:
            print(f'Graph 전송 실패: {ticker}')
        else:
            print(f'Graph 전송 성공: {ticker}')

if __name__ == "__main__":
    # 테스트용 예시 데이터 설정
    print("Starting test for plotting results.")
    stock1 = "AAPL"
    start_date = "2022-01-01"
    end_date = "2022-12-31"
    print(f"Plotting results for {stock1} from {start_date} to {end_date}")

    try:
        plot_comparison_results(stock1, start_date, end_date)
        print("Plotting completed successfully.")
    except Exception as e:
        print(f"Error occurred while plotting results: {e}")


    # python Results_plot.py

