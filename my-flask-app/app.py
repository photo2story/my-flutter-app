import os
import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask, request
import threading

# 환경 변수에서 Discord 토큰 및 채널 ID 가져오기
TOKEN = os.getenv('DISCORD_APPLICATION_TOKEN')
CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))

# Flask 앱 초기화
app = Flask(__name__)

# Discord 봇 초기화
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='/', intents=intents)
tree = app_commands.CommandTree(bot)

@bot.event
async def on_ready():
    print(f'Bot has logged in as {bot.user}')
    # 명령 트리 동기화
    await tree.sync()
    print('Command tree synced.')

@app.route('/execute_discord_command', methods=['POST'])
def execute_discord_command():
    data = request.json
    message_content = data.get('message')

    if message_content:
        send_message(message_content)

    return 'Message sent to Discord', 200

def send_message(message_content):
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        asyncio.run_coroutine_threadsafe(channel.send(message_content), bot.loop)
    else:
        print(f"Channel not found: {CHANNEL_ID}")

def run_discord_bot():
    bot.run(TOKEN)

if __name__ == '__main__':
    threading.Thread(target=run_discord_bot).start()
    app.run(host='0.0.0.0', port=5000)

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