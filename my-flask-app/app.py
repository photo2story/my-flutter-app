import os
import discord
from discord.ext import commands
from flask import Flask, request, jsonify
import nest_asyncio
import socket  # 추가된 부분

nest_asyncio.apply()

app = Flask(__name__)

TOKEN = os.getenv('DISCORD_APPLICATION_TOKEN')
CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))

intents = discord.Intents.default()
intents.message_content = True  # Privileged message content intent 추가
bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot has logged in successfully!')

@bot.command()
async def ping(ctx):
    await ctx.send('pong')
    print('Pong sent!')

@app.route('/execute_discord_command', methods=['POST'])
def execute_discord_command():
    data = request.get_json()
    command = data.get('command')
    print(f"Received command: {command}")
    if command:
        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            asyncio.run_coroutine_threadsafe(channel.send(command), bot.loop)
            return jsonify({'status': 'success'}), 200
        else:
            return jsonify({'error': 'Channel not found'}), 404
    return jsonify({'error': 'No command provided'}), 400

def run_discord_bot():
    bot.run(TOKEN)

if __name__ == '__main__':
    from threading import Thread
    import asyncio

    bot_thread = Thread(target=run_discord_bot)
    bot_thread.start()

    host = socket.gethostbyname(socket.gethostname())
    app.run(host=host, port=5000)




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