import os
import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask, request
from flask_cors import CORS
from dotenv import load_dotenv
from threading import Thread
import asyncio
import socket

# .env 파일에서 환경 변수 로드
load_dotenv()

app = Flask(__name__)
CORS(app)  # CORS 설정 추가

# 환경 변수에서 디스코드 토큰과 채널 ID 가져오기
TOKEN = os.getenv('DISCORD_APPLICATION_TOKEN')
GUILD_ID = os.getenv('DISCORD_GUILD_ID')

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f'Bot has logged in as {bot.user.name}')
    await tree.sync(guild=discord.Object(id=GUILD_ID))
    print(f'Synced slash commands for guild ID {GUILD_ID}')

@bot.command()
async def ping(ctx):
    await ctx.send('pong')

# 슬래시 커맨드 등록
tree = app_commands.CommandTree(bot)

@tree.command(name="ping", description="Responds with pong", guild=discord.Object(id=GUILD_ID))
async def slash_ping(interaction: discord.Interaction):
    await interaction.response.send_message('pong')

@app.route('/execute_discord_command', methods=['POST'])
def execute_discord_command():
    data = request.json
    print(f"Received data: {data}")

    async def send_message():
        channel = bot.get_channel(int(CHANNEL_ID))
        if channel:
            await channel.send(data['message'])
            print(f"Message sent to Discord: {data['message']}")
        else:
            print(f"Channel not found: {CHANNEL_ID}")

    asyncio.run_coroutine_threadsafe(send_message(), bot.loop)
    return 'Message sent', 200

def run_discord_bot():
    bot.run(TOKEN)

if __name__ == '__main__':
    if not TOKEN or not GUILD_ID:
        print("Discord bot token or guild ID is not set")
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