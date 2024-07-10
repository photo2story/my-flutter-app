import os
import sys
import asyncio
import threading
import requests
import io
from dotenv import load_dotenv
import discord
from discord.ext import tasks, commands
from datetime import datetime
import pandas as pd
import numpy as np
from quart import Quart, render_template, send_from_directory, jsonify, request
from quart_cors import cors
NaN = np.nan

# my-flask-app 디렉토리를 sys.path에 추가
sys.path.append(os.path.join(os.path.dirname(__file__), 'my-flask-app'))


# 사용자 정의 모듈 임포트
from get_ticker import get_ticker_name, get_ticker_from_korean_name, search_tickers_and_respond, update_stock_market_csv
from estimate_stock import estimate_snp, estimate_stock
from Results_plot import plot_comparison_results, plot_results_all
from get_compare_stock_data import merge_csv_files, load_sector_info
from Results_plot_mpl import plot_results_mpl
from git_operations import move_files_to_images_folder
from github_operations import save_csv_to_github, save_image_to_github, is_valid_stock, ticker_path
from backtest_send import backtest_and_send

# config.py에서 설정값 로드
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

# 설정값 할당
stocks = config.STOCKS
start_date = config.START_DATE
end_date = config.END_DATE
initial_investment = config.INITIAL_INVESTMENT
monthly_investment = config.MONTHLY_INVESTMENT
csv_url = config.CSV_URL
github_api_url = config.GITHUB_API_URL

@bot.command()
async def buddy(ctx):
    loop = asyncio.get_running_loop()

    for stock in stocks:
        await backtest_and_send(ctx, stock, 'modified_monthly', bot)
        if is_valid_stock(stock):
            try:
                plot_results_mpl(stock, start_date, end_date)
            except KeyError as e:
                await ctx.send(f"An error occurred while plotting {stock}: {e}")
                print(f"Error plotting {stock}: {e}")
        await asyncio.sleep(2)

    await loop.run_in_executor(None, update_stock_market_csv, ticker_path, stocks)
    sector_dict = await loop.run_in_executor(None, load_sector_info)
    path = '.'
    await loop.run_in_executor(None, merge_csv_files, path, sector_dict)

    await ctx.send("백테스팅 결과가 섹터별로 정리되었습니다.")
    move_files_to_images_folder()

@bot.command()
async def ticker(ctx, *, query: str = None):
    if query is None:
        await ctx.send("Please enter ticker stock name or ticker.")
        return

    await search_tickers_and_respond(ctx, query)

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

        await backtest_and_send(ctx, info_stock, option_strategy='1', bot=bot)
        plot_results_mpl(info_stock, start_date, end_date)
        move_files_to_images_folder()
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
        await channel.send(f'Bot has successfully logged in as {bot.user.name}')
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
        df = pd.read_csv(io.StringIO(csv_data))
        
        # NaN 값을 빈 문자열로 대체
        df.fillna('', inplace=True)
        
        return df
    except requests.exceptions.RequestException as e:
        print(f'Error fetching CSV data: {e}')
        return None


app = Quart(__name__)
app = cors(app)

@app.route('/')
async def index():
    return await render_template('index.html')

@app.route('/<path:path>')
async def static_proxy(path):
    return await send_from_directory(app.static_folder, path)

@app.route('/generate_description', methods=['POST'])
async def generate_description():
    data = await request.get_json()
    stock_ticker = data.get('stock_ticker')
    description = f"Description for {stock_ticker}"
    return jsonify({"description": description})

@app.route('/save_search_history', methods=['POST'])
async def save_search_history():
    data = await request.json
    stock_name = data.get('stock_name')
    print(f'Saved {stock_name} to search history.')
    return jsonify({"success": True})

@app.route('/api/get_images', methods=['GET'])
async def get_images():
    image_folder = os.path.join(app.static_folder, 'images')
    images = []
    for filename in os.listdir(image_folder):
        if filename.endswith('.png'):
            images.append(filename)
    return jsonify(images)

@app.route('/api/get_reviewed_tickers', methods=['GET'])
async def get_reviewed_tickers():
    image_folder = os.path.join(app.static_folder, 'images')
    tickers = []
    for filename in os.listdir(image_folder):
        if filename.startswith('comparison_') and filename.endswith('_VOO.png'):
            ticker = filename.split('_')[1]
            tickers.append(ticker)
    return jsonify(tickers)

sent_messages = {}

def reset_sent_messages():
    global sent_messages
    sent_messages = {}
    threading.Timer(10.0, reset_sent_messages).start()

reset_sent_messages()

@app.route('/data')
async def data():
    df = fetch_csv_data(config.CSV_URL)
    if df is None:
        return "Error fetching data", 500

    # 데이터프레임에 NaN 값이 있는지 확인
    print("NaN count per column:")
    print(df.isna().sum())
    
    # NaN 값을 빈 문자열로 대체
    df.fillna('', inplace=True)
    
    return df.to_html()

@app.route('/execute_stock_command', methods=['POST'])
async def execute_stock_command():
    data = await request.get_json()
    stock_ticker = data.get('stock_ticker')
    if not stock_ticker:
        return jsonify({'error': 'No stock ticker provided'}), 400

    try:
        global bot  # bot 변수를 전역으로 선언
        channel = bot.get_channel(config.DISCORD_CHANNEL_ID)
        if channel is None:
            return jsonify({'error': 'Discord channel not found'}), 500

        async def send_stock_command():
            class Context:
                async def send(self, message):
                    await channel.send(message)

            ctx = Context()
            try:
                await backtest_and_send(ctx, stock_ticker, option_strategy='1', bot=bot)  # bot 변수를 전달
                plot_results_mpl(stock_ticker, config.START_DATE, config.END_DATE)
                move_files_to_images_folder()
            except Exception as e:
                await ctx.send(f'An error occurred: {e}')

        # 비동기 태스크 실행
        asyncio.create_task(send_stock_command())

        return jsonify({'message': 'Command executed successfully'}), 200
    except Exception as e:
        print(f"Error while executing stock command: {str(e)}")  # 구체적인 에러 메시지를 로그에 출력
        return jsonify({'error': str(e)}), 500

    
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL', 'your_webhook_url_here')

@app.route('/send_discord_command', methods=['POST'])
def send_discord_command():
    data = request.json
    command = data.get('command')
    if command:
        response = requests.post(
            DISCORD_WEBHOOK_URL,
            json={'content': command},
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code == 204:
            return jsonify({'message': 'Command sent successfully'}), 200
        else:
            return jsonify({'message': 'Failed to send command'}), 500
    return jsonify({'message': 'Invalid command'}), 400

async def main():
    async with bot:
        bot.loop.create_task(app.run_task(host='0.0.0.0', port=int(os.environ.get('PORT', 5000))))
        await bot.start(config.DISCORD_APPLICATION_TOKEN)

if __name__ == '__main__':
    asyncio.run(main())


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

