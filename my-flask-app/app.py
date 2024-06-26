from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
import asyncio
import requests
import sys
import certifi
import threading
import nest_asyncio

nest_asyncio.apply()

# 콘솔 출력 인코딩을 UTF-8로 설정
sys.stdout.reconfigure(encoding='utf-8')

# 현재 디렉토리 경로를 시스템 경로에 추가
sys.path.append(os.path.join(os.path.dirname(__file__), 'my-flask-app'))

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

@app.route('/execute_discord_command', methods=['POST'])
def execute_discord_command():
    data = request.json
    command = data.get('command')
    if command == '/ping':
        asyncio.run_coroutine_threadsafe(send_ping_command(), bot.loop)
        return jsonify({'success': True})
    return jsonify({'error': 'Invalid command'}), 400

async def send_ping_command():
    channel = bot.get_channel(int(CHANNEL_ID))
    if channel:
        await channel.send('/ping')
    else:
        print(f"Channel not found: {CHANNEL_ID}")

TOKEN = os.getenv('DISCORD_APPLICATION_TOKEN')
CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='', intents=intents)
slash = SlashCommand(bot, sync_commands=True)

@slash.slash(name="ping")
async def _ping(ctx: SlashContext):
    await ctx.send(content="pong")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    channel = bot.get_channel(int(CHANNEL_ID))
    if channel:
        asyncio.run_coroutine_threadsafe(channel.send(f'Bot has successfully logged in: {bot.user.name}'), bot.loop)

def run_discord_bot():
    bot.run(TOKEN)

if __name__ == '__main__':
    discord_thread = threading.Thread(target=run_discord_bot)
    discord_thread.start()
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