# bot.py
# bot.py
import os
import sys
import asyncio
from dotenv import load_dotenv
import discord
from discord.ext import tasks, commands
import certifi
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import config  # config.py 임포트

os.environ['SSL_CERT_FILE'] = certifi.where()

# Add my-flask-app directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'my-flask-app')))

# 사용자 정의 모듈 임포트
from git_operations import move_files_to_images_folder
from get_ticker import load_tickers, search_tickers_and_respond, get_ticker_name, update_stock_market_csv, get_ticker_from_korean_name
from estimate_stock import estimate_stock
from Results_plot import plot_results_all
from Results_plot_mpl import plot_results_mpl
from github_operations import ticker_path
from backtest_send import backtest_and_send
from get_ticker import is_valid_stock
from gpt import analyze_with_gpt  # 이 부분을 수정

# get_account_balance 모듈 임포트
from get_account_balance import get_balance, get_ticker_price, get_market_from_ticker
from get_compare_stock_data import load_sector_info, merge_csv_files

load_dotenv()

TOKEN = os.getenv('DISCORD_APPLICATION_TOKEN')
CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))
H_APIKEY = os.getenv('H_APIKEY')
H_SECRET = os.getenv('H_SECRET')
H_ACCOUNT = os.getenv('H_ACCOUNT')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='', intents=intents)

bot_started = False

@bot.event
async def on_ready():
    global bot_started
    if not bot_started:
        print(f'Logged in as {bot.user.name}')
        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            await channel.send(f'Bot has successfully logged in as {bot.user.name}')
        else:
            print(f'Failed to get channel with ID {CHANNEL_ID}')
        bot_started = True

@tasks.loop(minutes=5)
async def send_msg():
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send('Hello')
        print(f'Message sent to channel {CHANNEL_ID}')
    else:
        print(f"Failed to find channel with ID: {CHANNEL_ID}")

processed_message_ids = set()

@bot.command()
async def buddy(ctx):
    for sector, stocks in config.STOCKS.items():
        await ctx.send(f'Processing sector: {sector}')
        for stock in stocks:
            await ctx.invoke(bot.get_command("stock"), query=stock)
            await asyncio.sleep(10)  # 각 호출 간에 10초 대기

@bot.command()
async def stock(ctx, query: str):
    stock_name = query.upper()
    await ctx.send(f'Processing stock: {stock_name}')
    try:
        # 백테스팅 및 결과 플로팅
        await backtest_and_send(ctx, stock_name, 'modified_monthly', bot)
        if is_valid_stock(stock_name):
            try:
                plot_results_mpl(stock_name, config.START_DATE, config.END_DATE)
            except KeyError as e:
                await ctx.send(f"An error occurred while plotting {stock_name}: {e}")
                print(f"Error plotting {stock_name}: {e}")
                    # 파일 이동
            move_files_to_images_folder()    
        await asyncio.sleep(10)

        # GPT 분석
        result = analyze_with_gpt(stock_name)
        await ctx.send(result)
        
        # 파일 이동
        # move_files_to_images_folder()
        
    except Exception as e:
        await ctx.send(f'An error occurred while processing {stock_name}: {e}')
        print(f'Error processing {stock_name}: {e}')

@bot.command()
async def ticker(ctx, *, query: str = None):
    print(f'Command received: ticker with query: {query}')
    if query is None:
        await ctx.send("Please enter ticker stock name or ticker.")
        return

    await search_tickers_and_respond(ctx, query)

@bot.command()
async def show_all(ctx):
    try:
        await plot_results_all()
        await ctx.send("All results have been successfully displayed.")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")
        print(f"Error: {e}")

@bot.command()
async def ping(ctx):
    if ctx.message.id not in processed_message_ids:
        processed_message_ids.add(ctx.message.id)
        await ctx.send(f'pong: {bot.user.name}')
        print(f'Ping command received and responded with pong.')

@bot.command()
async def account(ctx, ticker: str):
    try:
        ticker = ticker.upper()  # 티커를 대문자로 변환
        exchange = get_market_from_ticker(ticker)
        last_price = get_ticker_price(H_APIKEY, H_SECRET, H_ACCOUNT, exchange, ticker)
        await ctx.send(f'The exchange for {ticker} is {exchange}')
        await ctx.send(f'Last price of {ticker} is {last_price}')
    except Exception as e:
        await ctx.send(f'An error occurred: {e}')
        print(f'Error processing account for {ticker}: {e}')

@bot.command()
async def gemini(ctx, ticker: str):
    try:
        ticker = ticker.upper()  # 티커를 대문자로 변환
        report = analyze_with_gpt(ticker)  # 이 부분을 수정
        await ctx.send(report)
    except Exception as e:
        await ctx.send(f'An error occurred while analyzing {ticker} with GPT API: {e}')
        print(f'Error processing GPT analysis for {ticker}: {e}')

async def run_bot():
    await bot.start(TOKEN)

def run_server():
    port = int(os.environ.get('PORT', 8080))
    server_address = ('', port)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print(f'Starting server on port {port}')
    httpd.serve_forever()

if __name__ == '__main__':
    # HTTP 서버 시작
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # 봇 실행
    asyncio.run(run_bot())


#  .\.venv\Scripts\activate
# source .venv/bin/activate
# #     
# docker build -t asia.gcr.io/my-flask-app-429017/bot .
# docker push asia.gcr.io/my-flask-app-429017/bot
# gcloud run deploy bot --image asia.gcr.io/my-flask-app-429017/bot --platform managed --region asia-northeast3 --allow-unauthenticated
"""
git fetch origin
git checkout main
git reset --hard origin/main
nix-shell
"""
