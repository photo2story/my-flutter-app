import os
import discord
import asyncio
from flask import Flask, request
from flask_cors import CORS
from dotenv import load_dotenv
from threading import Thread
import logging
import socket

logging.basicConfig(level=logging.DEBUG)

# .env 파일에서 환경 변수 로드
load_dotenv()

app = Flask(__name__)
CORS(app)  # CORS 설정 추가

# 환경 변수에서 디스코드 토큰과 채널 ID 가져오기
TOKEN = os.getenv('DISCORD_APPLICATION_TOKEN')
CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')

logging.debug(f'TOKEN: {TOKEN}')
logging.debug(f'CHANNEL_ID: {CHANNEL_ID}')

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    logging.info(f'Bot has logged in as {bot.user.name}')
    channel = bot.get_channel(int(CHANNEL_ID))
    if channel:
        await channel.send('Bot has logged in successfully!')
        logging.info(f'Message sent to channel: {CHANNEL_ID}')
    else:
        logging.error(f'Channel not found: {CHANNEL_ID}')

@app.route('/execute_discord_command', methods=['POST'])
def execute_discord_command():
    data = request.json
    logging.debug(f"Received data: {data}")

    async def send_message():
        channel = bot.get_channel(int(CHANNEL_ID))
        if channel:
            await channel.send(data['message'])
            logging.info(f"Message sent to Discord: {data['message']}")
        else:
            logging.error(f"Channel not found: {CHANNEL_ID}")

    asyncio.run_coroutine_threadsafe(send_message(), bot.loop)
    return 'Message sent', 200

def run_discord_bot():
    bot.run(TOKEN)

if __name__ == '__main__':
    if not TOKEN or not CHANNEL_ID:
        logging.error("Discord bot token or channel ID is not set")
    else:
        Thread(target=run_discord_bot).start()
        app.run(host=socket.gethostbyname(socket.gethostname()), port=5000)


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