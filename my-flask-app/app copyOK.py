# app.py
# app.py
import os
import logging
import threading
import asyncio
from flask import Flask, render_template, send_from_directory, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from discord.ext import commands
import discord
import requests
import certifi
import sys
import nest_asyncio
import git

logging.basicConfig(level=logging.INFO)  # Set logging level to INFO
sys.stdout.reconfigure(encoding='utf-8') # 한글 출력을 위한 인코딩 설정
sys.path.append(os.path.join(os.path.dirname(__file__), 'my-flutter-app'))

from datetime import datetime
import pandas as pd
import numpy as np
from get_ticker import load_tickers, search_tickers, get_ticker_name, update_stock_market_csv
from estimate_stock import estimate_snp, estimate_stock
from Results_plot import plot_comparison_results, plot_results_all
from get_compare_stock_data import merge_csv_files, load_sector_info
from Results_plot_mpl import plot_results_mpl
from get_ticker import get_ticker_from_korean_name
from git_operations import move_files_to_images_folder
from github_operations import save_csv_to_github, save_image_to_github, is_valid_stock, ticker_path

load_dotenv()

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory(app.static_folder, path)

@app.route('/generate_description', methods=['POST'])
def generate_description():
    data = request.get_json()
    stock_ticker = data.get('stock_ticker')
    description = f"Description for {stock_ticker}"
    return jsonify({"description": description})

@app.route('/save_search_history', methods=['POST'])
def save_search_history():
    data = request.json
    stock_name = data.get('stock_name')
    print(f'Saved {stock_name} to search history.')
    return jsonify({"success": True})

@app.route('/api/get_images', methods=['GET'])
def get_images():
    image_folder = os.path.join(app.static_folder, 'images')
    images = []
    for filename in os.listdir(image_folder):
        if filename.endswith('.png'):
            images.append(filename)
    return jsonify(images)

sent_messages = {}

def reset_sent_messages():
    global sent_messages
    sent_messages = {}
    threading.Timer(10.0, reset_sent_messages).start()

reset_sent_messages()

TOKEN = os.getenv('DISCORD_APPLICATION_TOKEN')
CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix='', intents=intents)

stocks = [
    'AAPL', 'MSFT', 'AMZN', 'FB', 'GOOG', 'GOOGL', 'BRK.B', 'JNJ', 'V', 'PG', 'NVDA', 'UNH', 'HD', 'MA', 
    'PYPL', 'DIS', 'NFLX', 'XOM', 'VZ', 'PFE', 'T', 'KO', 'ABT', 'MRK', 'CSCO', 'ADBE', 'CMCSA', 'NKE', 
    'INTC', 'PEP', 'TMO', 'CVX', 'ORCL', 'ABBV', 'AVGO', 'MCD', 'QCOM', 'MDT', 'BMY', 'AMGN', 'UPS', 'CRM', 
    'MS', 'HON', 'C', 'GILD', 'DHR', 'BA', 'IBM', 'MMM', 'TSLA', 'TXN', 'SBUX', 'COST', 'AMD', 'TMUS', 
    'CHTR', 'INTU', 'ADP', 'MU', 'MDLZ', 'ISRG', 'BKNG', 'ADI', 'ATVI', 'LRCX', 'AMAT', 'REGN', 'NXPI', 
    'KDP', 'MAR', 'KLAC', 'WMT', 'JPM',
    'QQQ', 'TQQQ', 'SOXX', 'SOXL', 'UPRO', 'SPY', 'VOO', 'VTI', 'VGT', 'VHT', 'VCR', 'VFH', 'coin'
]

for stock in stocks:
    try:
        print(f"Processing {stock}...")
    except Exception as e:
        print(f"Error processing {stock}: {e}")

start_date = "2022-01-01"
end_date = datetime.today().strftime('%Y-%m-%d')
initial_investment = 30000000
monthly_investment = 1000000

processed_message_ids = set()
login_once_flag = False

async def backtest_and_send(ctx, stock, option_strategy):
    await ctx.send(f'backtest_and_send.command1: {stock}')  # 주식 이름을 출력
    if not is_valid_stock(stock):
        message = f"Stock market information updates needed. {stock}"
        await ctx.send(message)
        print(message)
        return

    try:
        total_account_balance, total_rate, str_strategy, invested_amount, str_last_signal, min_stock_data_date, file_path, result_df = estimate_stock(
            stock, start_date, end_date, initial_investment, monthly_investment, option_strategy)
        await ctx.send(f'backtest_and_send.command2: {stock}')  # 주식 이름을 출력
        min_stock_data_date = str(min_stock_data_date).split(' ')[0]
        user_stock_file_path1 = file_path

        file_path = estimate_snp(stock, 'VOO', min_stock_data_date, end_date, initial_investment, monthly_investment, option_strategy, result_df)
        user_stock_file_path2 = file_path

        name = get_ticker_name(stock)
        DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')
        message = {
            'content': f"Stock: {stock} ({name})\n"
                    f"Total_rate: {total_rate:,.0f} %\n"
                    f"Invested_amount: {invested_amount:,.0f} $\n"
                    f"Total_account_balance: {total_account_balance:,.0f} $\n"
                    f"Last_signal: {str_last_signal} \n"
        }
        response = requests.post(DISCORD_WEBHOOK_URL, json=message)
        if response.status_code != 204:
            print('Failed to send Discord message')
        else:
            print('Successfully sent Discord message')

        plot_comparison_results(user_stock_file_path1, user_stock_file_path2, stock, 'VOO', total_account_balance, total_rate, str_strategy, invested_amount, min_stock_data_date)
        await bot.change_presence(status=discord.Status.online, activity=discord.Game("Waiting"))
    except Exception as e:
        await ctx.send(f"An error occurred while processing {stock}: {e}")
        print(f"Error processing {stock}: {e}")

@bot.command()
async def buddy(ctx):
    loop = asyncio.get_running_loop()  # Get the current event loop

    for stock in stocks:  # 주식 리스트를 순회하며 백테스팅 수행
        await backtest_and_send(ctx, stock, 'modified_monthly')
        if is_valid_stock(stock):  # 유효한 주식에 대해서만 결과를 플로팅
            try:
                plot_results_mpl(stock, start_date, end_date)
            except KeyError as e:
                await ctx.send(f"An error occurred while plotting {stock}: {e}")
                print(f"Error plotting {stock}: {e}")
        await asyncio.sleep(2)

    # Run synchronous functions in the executor
    await loop.run_in_executor(None, update_stock_market_csv, ticker_path, stocks)
    sector_dict = await loop.run_in_executor(None, load_sector_info)  # run_in_executor returns a future, await it if function is synchronous
    path = '.'  # Assuming folder path
    await loop.run_in_executor(None, merge_csv_files, path, sector_dict)

    await ctx.send("백테스팅 결과가 섹터별로 정리되었습니다.")
    move_files_to_images_folder()  # 모든 백테스트 작업이 완료된 후 파일 이동

@bot.command()
async def ticker(ctx, *, query: str = None):
    print(f'Command received: ticker with query: {query}')
    if query is None:
        await ctx.send("Please enter ticker stock name or ticker.")
        return

    ticker_dict = load_tickers()
    matching_tickers = search_tickers(query, ticker_dict)

    if not matching_tickers:
        await ctx.send("No search results.")
        return

    response_message = "Search results:\n"
    response_messages = []
    for symbol, name in matching_tickers:
        line = f"{symbol} - {name}\n"
        if len(response_message) + len(line) > 2000:
            response_messages.append(response_message)
            response_message = "Search results (continued):\n"
        response_message += line

    if response_message:
        response_messages.append(response_message)

    for message in response_messages:
        await ctx.send(message)
    print(f'Sent messages for query: {query}')

@bot.command()
async def stock(ctx, *args):
    stock_name = ' '.join(args)
    await ctx.send(f'Arguments passed by command: {stock_name}')
    try:
        info_stock = str(stock_name).upper()
        if info_stock.startswith('K '):
            korean_stock_name = info_stock[2:].upper()
            korean_stock_code = get_ticker_from_korean_name(korean_stock_name)
            if korean_stock_code is None:
                await ctx.send(f'Cannot find the stock {korean_stock_name}.')
                return
            else:
                info_stock = korean_stock_code

        await backtest_and_send(ctx, info_stock, option_strategy='1')
        plot_results_mpl(info_stock, start_date, end_date)
        move_files_to_images_folder()  # 모든 백테스트 작업이 완료된 후 파일 이동
    except Exception as e:
        await ctx.send(f'An error occurred: {e}')

@bot.command()
async def show_all(ctx):
    try:
        await plot_results_all()
        await ctx.send("All results have been successfully displayed.")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")
        print(f"Error: {e}")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    channel = bot.get_channel(int(CHANNEL_ID))
    if channel:
        await channel.send(f'Bot has successfully logged in: {bot.user.name}')
    else:
        print(f'Failed to get channel with ID {CHANNEL_ID}')

@bot.command()
async def ping(ctx):
    if ctx.message.id not in processed_message_ids:
        processed_message_ids.add(ctx.message.id)
        await ctx.send(f'pong: {bot.user.name}')

import io

# CSV 파일 URL
csv_url = 'https://raw.githubusercontent.com/photo2story/my-flutter-app/main/my-flask-app/stock_market.csv'

def fetch_csv_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        csv_data = response.content.decode('utf-8')
        return pd.read_csv(io.StringIO(csv_data))
    except requests.exceptions.RequestException as e:
        print(f'Error fetching CSV data: {e}')
        return None

@app.route('/data')
def data():
    df = fetch_csv_data(csv_url)
    if df is None:
        return "Error fetching data", 500

    return df.to_html()

if __name__ == '__main__':
    async def run_bot():
        await bot.start(TOKEN)
    
    def run_flask():
        app.run(debug=True, use_reloader=False)

    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_bot())




# #  .\.venv\Scripts\activate
# #  python app.py 
# pip install huggingface_hub
# huggingface-cli login
# EEVE-Korean-Instruct-10.8B-v1.0-GGUF
# ollama create EEVE-Korean-Instruct-10.8B -f Modelfile-V02
# ollama create EEVE-Korean-10.8B -f EEVE-Korean-Instruct-10.8B-v1.0-GGUF/Modelfile
# pip install ollama
# pip install chromadb
# pip install langchain
# ollama create EEVE-Korean-10.8B -f Modelfile
# git push heroku main
# heroku logs --tail
