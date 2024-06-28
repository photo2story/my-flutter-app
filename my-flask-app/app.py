# app.py
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import asyncio
import nest_asyncio
import threading

# Nest_asyncio 적용
nest_asyncio.apply()

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

@app.route('/execute_discord_command', methods=['POST'])
def execute_discord_command():
    data = request.json
    command = data.get('command')
    stock_name = data.get('stock_name')
    asyncio.run_coroutine_threadsafe(send_discord_command(command, stock_name), bot.loop)
    return jsonify({'success': True})

async def send_discord_command(command, stock_name):
    channel = bot.get_channel(int(CHANNEL_ID))
    await channel.send(f'{command} {stock_name}')

# Discord 설정
TOKEN = os.getenv('DISCORD_APPLICATION_TOKEN')
CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')

intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    if not hasattr(bot, 'is_logged_in'):
        bot.is_logged_in = True
        print(f'Logged in as {bot.user.name}')
        channel = bot.get_channel(int(CHANNEL_ID))
        if channel:
            await channel.send(f'Bot has successfully logged in: {bot.user.name}')

@bot.command()
async def ping(ctx):
    await ctx.send(f'pong: {bot.user.name}')

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
    except Exception as e:
        await ctx.send(f'An error occurred: {e}')

def run_discord_bot():
    if not getattr(bot, 'is_running', False):
        bot.is_running = True
        bot.run(TOKEN)

# Discord Bot을 별도의 스레드에서 실행
if not hasattr(threading, 'discord_thread'):
    discord_thread = threading.Thread(target=run_discord_bot)
    discord_thread.start()
    threading.discord_thread = discord_thread

if __name__ == '__main__':
    app.run()



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