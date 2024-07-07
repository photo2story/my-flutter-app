# app.py
import os
from dotenv import load_dotenv
import discord
from discord.ext import tasks, commands
import logging
import sys
from datetime import datetime
import pandas as pd
import numpy as np
from flask import Flask, render_template, send_from_directory, jsonify, request
from flask_cors import CORS
import requests
import io
import git

# Add my-flask-app directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), 'my-flask-app'))

# Import custom modules
from get_ticker import load_tickers, search_tickers, get_ticker_name, update_stock_market_csv
from estimate_stock import estimate_snp, estimate_stock
from Results_plot import plot_comparison_results, plot_results_all
from get_compare_stock_data import merge_csv_files, load_sector_info
from Results_plot_mpl import plot_results_mpl
from get_ticker import get_ticker_from_korean_name
from git_operations import move_files_to_images_folder
from github_operations import save_csv_to_github, save_image_to_github, is_valid_stock, ticker_path
from backtest_send import backtest_and_send  # 추가된 부분

# Load configuration from config.py
import config

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="", intents=intents)

@bot.event
async def on_ready():
    send_msg.start()
    print(f"Logged in as {bot.user.name}")

@tasks.loop(minutes=5)
async def send_msg():
    channel = bot.get_channel(config.DISCORD_CHANNEL_ID)
    if channel:
        await channel.send('Hello')
    else:
        print("Failed to find channel with ID:", config.DISCORD_CHANNEL_ID)

# Assign configuration values
stocks = config.STOCKS
start_date = config.START_DATE
end_date = config.END_DATE
initial_investment = config.INITIAL_INVESTMENT
monthly_investment = config.MONTHLY_INVESTMENT
csv_url = config.CSV_URL
github_api_url = config.GITHUB_API_URL

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
    channel = bot.get_channel(int(config.DISCORD_CHANNEL_ID))
    if channel:
        await channel.send(f'Bot has successfully logged in: {bot.user.name}')
    else:
        print(f'Failed to get channel with ID {config.DISCORD_CHANNEL_ID}')

@bot.command()
async def ping(ctx):
    if ctx.message.id not in processed_message_ids:
        processed_message_ids.add(ctx.message.id)
        await ctx.send(f'pong: {bot.user.name}')

def fetch_csv_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        csv_data = response.content.decode('utf-8')
        return pd.read_csv(io.StringIO(csv_data))
    except requests.exceptions.RequestException as e:
        print(f'Error fetching CSV data: {e}')
        return None

bot.run(config.DISCORD_APPLICATION_TOKEN)

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

@app.route('/data')
def data():
    df = fetch_csv_data(config.CSV_URL)
    if df is None:
        return "Error fetching data", 500

    return df.to_html()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
     
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
# heroku logs --tail -a he-flutter-app

