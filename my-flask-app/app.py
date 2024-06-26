import asyncio
import nest_asyncio
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import threading

# Nest_asyncio 적용
nest_asyncio.apply()

# 환경 변수 로드
load_dotenv()

# Flask 애플리케이션 설정
app = Flask(__name__)
CORS(app)

# Discord 설정
TOKEN = os.getenv('DISCORD_APPLICATION_TOKEN')
CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
bot = commands.Bot(command_prefix='', intents=intents)

@app.route('/execute_discord_command', methods=['POST'])
def execute_discord_command():
    try:
        print("Received request to send ping")
        future = asyncio.run_coroutine_threadsafe(send_ping_command(), bot.loop)
        future.result()  # Wait for the result
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error sending ping: {e}")
        return jsonify({'success': False, 'error': str(e)})

async def send_ping_command():
    print("Sending ping")
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send('ping\n')  # 줄 바꿈 추가
        print(f"Message sent to channel: {CHANNEL_ID}")
    else:
        print(f"Channel not found: {CHANNEL_ID}")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        asyncio.run_coroutine_threadsafe(channel.send(f'Bot has successfully logged in: {bot.user.name}\n'), bot.loop)

@bot.command()
async def ping(ctx):
    print("Received ping command")
    await ctx.send('pong')

@bot.event
async def on_message(message):
    print(f"Message from {message.author}: {message.content}")
    await bot.process_commands(message)

def run_discord_bot():
    bot.run(TOKEN)

if __name__ == '__main__':
    discord_thread = threading.Thread(target=run_discord_bot)
    discord_thread.start()
    app.run()
