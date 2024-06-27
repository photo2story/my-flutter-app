from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import asyncio
import nest_asyncio
import socket
import sys
import certifi
import threading

# 콘솔 출력 인코딩을 UTF-8로 설정
sys.stdout.reconfigure(encoding='utf-8')

# 현재 디렉토리 경로를 시스템 경로에 추가
sys.path.append(os.path.join(os.path.dirname(__file__), 'my-flask-app'))

from datetime import datetime
from get_ticker import load_tickers, search_tickers, get_ticker_name, get_ticker_from_korean_name
from estimate_stock import estimate_snp, estimate_stock
from Results_plot import plot_comparison_results
from Results_plot_mpl import plot_results_mpl
from get_compare_stock_data import merge_csv_files, load_sector_info

# SSL 인증서 설정
os.environ['SSL_CERT_FILE'] = certifi.where()

# 환경 변수 로드
load_dotenv()

app = Flask(__name__, static_folder='build')
CORS(app)

@app.route('/')
def serve():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory(app.static_folder, path)

@app.route('/save_search_history', methods=['POST'])
def save_search_history():
    data = request.json
    stock_name = data.get('stock_name')
    # 여기에 검색 기록을 저장하는 로직을 작성합니다.
    print(f'Saved {stock_name} to search history.')  # 실제로는 데이터베이스에 저장 등
    return jsonify({"success": True})

@app.route('/api/get_images', methods=['GET'])
def get_images():
    image_folder = os.path.join(app.static_folder, 'images')
    images = []
    for filename in os.listdir(image_folder):
        if filename.endswith('.png'):
            images.append(filename)
    return jsonify(images)

@app.route('/api/get_tickers', methods=['GET'])
def get_tickers():
    tickers = load_tickers()
    return jsonify(tickers)

@app.route('/api/estimate_stock', methods=['POST'])
def estimate_stock_route():
    data = request.json
    stock_name = data.get('stock_name')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    
    # 주식 데이터를 처리하고 결과를 반환합니다.
    result = estimate_stock(stock_name, start_date, end_date)
    
    return jsonify(result)


# Discord 설정
TOKEN = os.getenv('DISCORD_APPLICATION_TOKEN')
CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    app_info = await bot.application_info()
    if app_info:
        print(f'Bot has applications.commands scope: {app_info.flags.applications_commands}')
    # 로그인되었을 때 메시지 전송
    channel = bot.get_channel(int(CHANNEL_ID))
    if channel:
        await channel.send("Bot has logged in successfully!")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content == "/ping":
        await message.channel.send("pong")

@bot.command()
async def ping(ctx):
    await ctx.send('pong')

@app.route('/execute_discord_command', methods=['POST'])
def execute_discord_command():
    data = request.json
    command = data.get('command')

    if command == '/ping':
        asyncio.run_coroutine_threadsafe(send_ping_command(), bot.loop)
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Invalid command'}), 400

async def send_ping_command():
    channel = bot.get_channel(int(CHANNEL_ID))
    if channel:
        await channel.send("/ping")
    else:
        print(f"Channel not found: {CHANNEL_ID}")

def run_discord_bot():
    bot.run(TOKEN)

# 호스트 이름을 수동으로 설정
hostname = socket.gethostname()
socket.getfqdn = lambda x=hostname: x

# nest_asyncio 적용
nest_asyncio.apply()

# 메인 함수
async def main():
    # 플라스크 앱을 비동기적으로 실행
    app_task = asyncio.create_task(asyncio.to_thread(app.run))
    # 디스코드 봇을 비동기적으로 실행
    bot_task = asyncio.create_task(run_discord_bot())
    await asyncio.gather(app_task, bot_task)

# 이벤트 루프 실행
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())








"""
flutter run -d chrome

.\.venv\Scripts\activate
cd..
cd my-flutter-app/my-flask-app
python app.py 

npm run build
heroku login
git init
heroku git:remote -a he-react-app

git commit -m "react build"
git push heroku main
"""