import os
import discord
from discord.ext import commands
from flask import Flask, request, jsonify
import threading
import asyncio
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# Flask 설정
app = Flask(__name__)

# Discord 봇 설정
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

TOKEN = os.getenv('DISCORD_APPLICATION_TOKEN')
CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')

@app.route('/execute_discord_command', methods=['POST'])
def execute_discord_command():
    data = request.get_json()
    command = data.get('command')

    if command == 'ping':
        asyncio.run(send_ping_command())
        return jsonify({'status': 'success', 'message': 'Command executed successfully'}), 200
    else:
        return jsonify({'status': 'error', 'message': 'Unknown command'}), 400

async def send_ping_command():
    channel = bot.get_channel(int(CHANNEL_ID))
    await channel.send('pong')

def run_flask_app():
    app.run(host='0.0.0.0', port=5000)

async def run_discord_bot():
    await bot.start(TOKEN)

if __name__ == "__main__":
    threading.Thread(target=run_flask_app).start()
    asyncio.run(run_discord_bot())


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