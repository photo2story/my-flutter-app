# Results_plot.py

import matplotlib.dates as dates
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import os
import requests
import asyncio
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

def plot_comparison_results(file_path1, file_path2, stock1, stock2, total_account_balance, total_rate, str_strategy, invested_amount, min_stock_data_date):
    fig, ax2 = plt.subplots(figsize=(8, 6))

    full_path1 = os.path.abspath(file_path1)
    full_path2 = os.path.abspath(file_path2)
    print(f"Reading full dataset for graph from: {full_path1} and {full_path2}")

    df1_graph = pd.read_csv(full_path1, parse_dates=['Date'], index_col='Date')
    df2_graph = pd.read_csv(full_path2, parse_dates=['Date'], index_col='Date')

    last_signal_row = df1_graph.dropna(subset=['signal']).iloc[-1] if 'signal' in df1_graph.columns else None
    last_signal = last_signal_row['signal'] if last_signal_row is not None else 'N/A'
    current_signal = df1_graph['ppo_histogram'].iloc[-1] if 'ppo_histogram' in df1_graph.columns else 'N/A'

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

    # 이미지 파일 전송
    with open(save_path, 'rb') as image:
        response = requests.post(
            DISCORD_WEBHOOK_URL,
            files={'image': image}
        )
        if response.status_code != 204:
            print(f'Graph 전송 실패: {stock1}')
        else:
            print(f'Graph 전송 성공: {stock1}')


def plot_results_all(ticker):
    DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')
    print(f"Fetching image for ticker: {ticker}")

    image_file = f'comparison_{ticker}_VOO.png'
    image_url = f"{GITHUB_RAW_BASE_URL}/{image_file}"
    print(f"Image URL: {image_url}")

    name = get_ticker_name(ticker)
    print(f"Stock name: {name}")

    full_path1 = f"static/images/result_VOO_{ticker}.csv"
    simplified_df_path1 = os.path.join(os.path.dirname(full_path1), f'static/images/result_{ticker}.csv')

    if os.path.exists(full_path1) and os.path.exists(simplified_df_path1):
        df1_graph = pd.read_csv(full_path1, parse_dates=['Date'], index_col='Date')
        df1 = pd.read_csv(simplified_df_path1, parse_dates=['Date'], index_col='Date')

        total_account_balance = df1_graph['account_balance'].iloc[-1]
        total_rate = df1_graph['rate'].iloc[-1]
        invested_amount = df1_graph['invested_amount'].iloc[-1]
        last_signal_row = df1_graph.dropna(subset=['signal']).iloc[-1] if 'signal' in df1_graph.columns else None
        str_last_signal = last_signal_row['signal'] if last_signal_row is not None else 'N/A'

        max_divergence = df1['Divergence'].max()
        min_divergence = df1['Divergence'].min()
        current_divergence = df1['Divergence'].iloc[-1]
        relative_divergence = df1['Relative_Divergence'].iloc[-1]

        message = f"Stock: {ticker} ({name})\n" \
                  f"Total Rate: {total_rate:.2f}% (VOO: {total_rate:.2f}%), Relative_Divergence: {relative_divergence:.2f}\n" \
                  f"Current Divergence: {current_divergence:.2f} (max: {max_divergence:.2f}, min: {min_divergence:.2f})\n" \
                  f"Current Signal(PPO): {str_last_signal}, Last Signal: {str_last_signal}"
        response = requests.post(DISCORD_WEBHOOK_URL, data={'content': message})
        if response.status_code != 204:
            print('Discord 메시지 전송 실패')
        else:
            print('Discord 메시지 전송 성공')

        print(f"Attempting to download image from URL: {image_url}")
        image_response = requests.get(image_url)
        if image_response.status_code != 200:
            print(f'Graph 전송 실패: {ticker}')
            return

        image_data = image_response.content
        files = {'image': ('image.png', image_data, 'image/png')}
        response = requests.post(DISCORD_WEBHOOK_URL, files=files)
        if response.status_code != 204:
            print(f'Graph 전송 실패: {ticker}')
            print(response.status_code)
            print(response.text)
        else:
            print(f'Graph 전송 성공: {ticker}')

if __name__ == "__main__":
    # 테스트용 예시 데이터 설정
    print("Starting test for plotting results.")
    stock1 = "AAPL"
    print(f"Plotting results for {stock1}")

    try:
        plot_results_all(stock1)
        print("Plotting completed successfully.")
    except Exception as e:
        print(f"Error occurred while plotting results: {e}")


    # python Results_plot.py

