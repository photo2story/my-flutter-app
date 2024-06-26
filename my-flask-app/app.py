import asyncio
import nest_asyncio
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import threading
import logging

# Nest_asyncio 적용
nest_asyncio.apply()

# 환경 변수 로드
load_dotenv()

# Flask 애플리케이션 설정
app = Flask(__name__)
CORS(app)

# Discord 설정
TOKEN = os.getenv('DISCORD_APPLICATION_TOKEN')
CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')

intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix='', intents=intents)

@app.route('/execute_discord_command', methods=['POST'])
def execute_discord_command():
    data = request.json
    stock_name = data.get('stock_name')
    print(f"Received request to send ping with stock name: {stock_name}")
    try:
        future = asyncio.run_coroutine_threadsafe(send_ping_command(stock_name), bot.loop)
        result = future.result()  # Wait for the result
        print(f"Ping sent successfully: {result}")
    except Exception as e:
        print(f"Error sending ping: {e}")
    return jsonify({'success': True})

async def send_ping_command(stock_name):
    print(f"Sending ping with stock name: {stock_name}")
    channel = bot.get_channel(int(CHANNEL_ID))
    if channel:
        await channel.send(f'ping: {stock_name}')
        print(f"Message sent to channel: {CHANNEL_ID}")
    else:
        print(f"Channel not found: {CHANNEL_ID}")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    channel = bot.get_channel(int(CHANNEL_ID))
    if channel:
        asyncio.run_coroutine_threadsafe(channel.send(f'Bot has successfully logged in: {bot.user.name}'), bot.loop)

def run_discord_bot():
    if not getattr(bot, 'is_running', False):
        bot.is_running = True
        bot.run(TOKEN)

if __name__ == '__main__':
    discord_thread = threading.Thread(target=run_discord_bot)
    discord_thread.start()
    app.run()
"""
flutter run

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