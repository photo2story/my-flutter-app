from flask import Flask
import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import nest_asyncio
import threading
import asyncio
import logging

# Load environment variables
load_dotenv()

# Flask app setup
app = Flask(__name__)

@app.route('/')
def index():
    return "API is running", 200

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Discord bot setup
TOKEN = os.getenv('DISCORD_APPLICATION_TOKEN')
CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user.name}')
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send(f'Bot has successfully logged in: {bot.user.name}')
    else:
        logger.error(f'Could not find channel with ID: {CHANNEL_ID}')

@bot.command()
async def ping(ctx):
    await ctx.send(f'pong: {bot.user.name}')

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
