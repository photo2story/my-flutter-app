# app.py
import os, sys
from dotenv import load_dotenv
import discord
from discord.ext import tasks, commands
from Results_plot import plot_comparison_results, plot_results_all
import yfinance as yf
import matplotlib.pyplot as plt


sys.stdout.reconfigure(encoding='utf-8')

sys.path.append(os.path.join(os.path.dirname(__file__), 'my-flask-app'))
# Load environment variables from .env file
load_dotenv()

TOKEN = os.getenv('DISCORD_APPLICATION_TOKEN')
CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="", intents=intents)

@bot.event
async def on_ready():
    send_msg.start()
    print(f"Logged in as {bot.user.name}")

@tasks.loop(minutes=5)
async def send_msg():
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send('Hello')
    else:
        print("Failed to find channel with ID:", CHANNEL_ID)

@bot.command(name='ping')
async def ping(ctx):
    await ctx.send('pong')

@bot.command(name='stock')
async def stock(ctx, symbol: str):
    try:
        # 주식 데이터 가져오기
        stock_data = yf.download(symbol, period='1y')
        stock_data['Close'].plot(title=f'{symbol} Stock Price')
        
        # 그래프 저장
        plt.savefig('stock_price.png')
        plt.close()

        # 그래프를 디스코드 채널로 전송
        with open('stock_price.png', 'rb') as f:
            picture = discord.File(f)
            await ctx.send(file=picture)
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")
        print(f"Error: {e}")

@bot.command(name='show_all')
async def show_all(ctx):
    try:
        # 모든 결과를 표시하는 함수 호출
        plot_results_all()
        await ctx.send("All results have been successfully displayed.")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")
        print(f"Error: {e}")

@bot.command(name='compare')
async def compare(ctx, symbol1: str, symbol2: str):
    try:
        # 주식 데이터를 가져와 비교 분석하는 함수 호출
        plot_comparison_results(symbol1, symbol2)
        
        # 비교 분석 결과 그래프를 디스코드 채널로 전송
        with open('comparison_results.png', 'rb') as f:
            picture = discord.File(f)
            await ctx.send(file=picture)
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")
        print(f"Error: {e}")

bot.run(TOKEN)
 
# #  .\.venv\Scripts\activate
# #  python app.py 
# pip install huggingface_hub
# huggingface-cli login
# EEVE-Korean-Instruct-10.8B-v1.0-GGUF
# ollama create EEVE-Korean-Instruct-10.8B -f Modelfile-V02
# ollama create EEVE-Korean-10.8B -f EEVE-Korean-Instruct-10.8B-v1.0-GGUF/Modelfile
# pip install ollama
# pip install chromadb
# pip install langchain
# ollama create EEVE-Korean-10.8B -f Modelfile
# git push heroku main
# heroku logs --tail
