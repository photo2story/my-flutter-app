import os
import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

TOKEN = os.getenv('DISCORD_APPLICATION_TOKEN')
CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot has logged in as {bot.user}')

@app.route('/execute_discord_command', methods=['POST'])
def execute_discord_command():
    data = request.get_json()
    command = data.get('command')

    if command == '/ping':
        asyncio.run_coroutine_threadsafe(send_ping_command(), bot.loop)
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'invalid command'}), 400

async def send_ping_command():
    channel = bot.get_channel(int(CHANNEL_ID))
    if channel:
        await channel.send('/ping')
    else:
        print(f"Channel not found: {CHANNEL_ID}")

if __name__ == '__main__':
    bot.loop.create_task(bot.start(TOKEN))
    app.run(debug=False, host='0.0.0.0')

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