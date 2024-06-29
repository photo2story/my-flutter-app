from flask import Flask
import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import nest_asyncio
import threading
import asyncio

# 환경 변수 로드
load_dotenv()

# Flask 애플리케이션 설정
app = Flask(__name__)

@app.route('/')
def index():
    return "API is running", 200

# Discord 봇 설정
TOKEN = os.getenv('DISCORD_APPLICATION_TOKEN')
CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')

intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.command()
async def ping(ctx):
    await ctx.send(f'pong: {bot.user.name}')

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    channel = bot.get_channel(int(CHANNEL_ID))
    if channel:
        await channel.send(f'Bot has successfully logged in: {bot.user.name}')

# 비동기 루프 설정
def start_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

if __name__ == '__main__':
    nest_asyncio.apply()
    loop = asyncio.get_event_loop()

    def run_discord_bot():
        asyncio.run(bot.start(TOKEN))

    flask_thread = threading.Thread(target=start_flask)
    flask_thread.start()

    try:
        loop.run_until_complete(run_discord_bot())
    except KeyboardInterrupt:
        loop.run_until_complete(bot.close())
