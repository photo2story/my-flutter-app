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
from Results_plot import plot_comparison_results
from Results_plot_mpl import plot_results_mpl
from github_operations import ticker_path
from backtest_send import backtest_and_send
from get_ticker import is_valid_stock
from gemini import analyze_with_gemini
from gpt import analyze_with_gpt
from get_compare_stock_data import save_simplified_csv, read_and_process_csv  # 추가된 부분

load_dotenv()

TOKEN = os.getenv('DISCORD_APPLICATION_TOKEN')
CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))
H_APIKEY = os.getenv('H_APIKEY')
H_SECRET = os.getenv('H_SECRET')
H_ACCOUNT = os.getenv('H_ACCOUNT')

GITHUB_RAW_BASE_URL = "https://raw.githubusercontent.com/photo2story/my-flutter-app/main/static/images"

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
async def buddy_loop():
    sector_list = list(config.STOCKS.keys())
    for sector in sector_list:
        stock_names = config.STOCKS[sector]
        for stock_name in stock_names:
            channel = bot.get_channel(CHANNEL_ID)
            if channel:
                await channel.send(f'Processing buddy for sector {sector}, stock: {stock_name}')
                await bot.get_command("buddy")(await bot.get_context(channel.last_message), query=stock_name)

processed_message_ids = set()

@bot.command()
async def start_buddy_loop(ctx):
    """Starts the buddy loop task."""
    if not buddy_loop.is_running():
        buddy_loop.start()
        await ctx.send("Buddy loop started.")
    else:
        await ctx.send("Buddy loop is already running.")

@bot.command()
async def stop_buddy_loop(ctx):
    """Stops the buddy loop task."""
    if buddy_loop.is_running():
        buddy_loop.stop()
        await ctx.send("Buddy loop stopped.")
    else:
        await ctx.send("Buddy loop is not running.")

@bot.command()
async def stock(ctx, *, query: str = None):
    if query:
        stock_names = [query.upper()]
    else:
        stock_names = [stock for sector, stocks in config.STOCKS.items() for stock in stocks]

    for stock_name in stock_names:
        stock_analysis_complete = config.is_stock_analysis_complete(stock_name)

        if stock_analysis_complete:
            await ctx.send(f"Stock analysis for {stock_name} is already complete. Displaying results.")
        else:
            await ctx.send(f'Stock analysis for {stock_name} is not complete. Proceeding with analysis.')
            try:
                # Analysis logic
                await backtest_and_send(ctx, stock_name, 'modified_monthly', bot)
            except Exception as e:
                await ctx.send(f'An error occurred while processing {stock_name}: {e}')
                print(f'Error processing {stock_name}: {e}')

        # Display results
        try:
            plot_comparison_results(stock_name, config.START_DATE, config.END_DATE)
            plot_results_mpl(stock_name, config.START_DATE, config.END_DATE)
            await ctx.send(f'Results for {stock_name} displayed successfully.')
        except Exception as e:
            await ctx.send(f"An error occurred while plotting {stock_name}: {e}")
            print(f"Error plotting {stock_name}: {e}")

        await asyncio.sleep(20)

@bot.command()
async def gemini(ctx, *, query: str = None):
    if query:
        tickers = [query.upper()]
    else:
        tickers = [stock for sector, stocks in config.STOCKS.items() for stock in stocks]

    for ticker in tickers:
        gemini_analysis_complete = config.is_gemini_analysis_complete(ticker)

        if gemini_analysis_complete:
            report_file = f'report_{ticker}.txt'
            report_file_url = f"{GITHUB_RAW_BASE_URL}/{report_file}"

            print(f"URL to the report file: {report_file_url}")

            try:
                response = requests.get(report_file_url)
                response.raise_for_status()
                report_text = response.text
                await send_report_to_discord(report_text, ticker)
            except requests.exceptions.RequestException as e:
                await ctx.send(f"Error retrieving report for {ticker}: {e}")
        else:
            try:
                result = await analyze_with_gemini(ticker)
                await ctx.send(result)
            except Exception as e:
                error_message = f'An error occurred while analyzing {ticker} with Gemini: {str(e)}'
                await ctx.send(error_message)
                print(error_message)
@bot.command()
async def buddy(ctx, *, query: str = None):
    if query:
        stock_names = [query.upper()]
    else:
        stock_names = [stock for sector, stocks in config.STOCKS.items() for stock in stocks]

    # stock 명령 실행
    for stock_name in stock_names:
        stock_analysis_complete = config.is_stock_analysis_complete(stock_name)
        gemini_analysis_complete = config.is_gemini_analysis_complete(stock_name)

        # 주식 분석 상태 출력
        await ctx.send(f"Stock analysis complete for {stock_name}: {stock_analysis_complete}")

        if not stock_analysis_complete:
            await ctx.invoke(bot.get_command("stock"), query=stock_name)
            await asyncio.sleep(10)

        # 제미니 분석 상태 출력
        await ctx.send(f"Gemini analysis complete for {stock_name}: {gemini_analysis_complete}")

        if not gemini_analysis_complete:
            await ctx.invoke(bot.get_command("gemini"), query=stock_name)


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
        await plot_comparison_results()
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
# #  python bot.py   
# docker build -t asia.gcr.io/my-flask-app-429017/bot .
# docker push asia.gcr.io/my-flask-app-429017/bot
# gcloud run deploy bot --image asia.gcr.io/my-flask-app-429017/bot --platform managed --region asia-northeast3 --allow-unauthenticated
"""
git fetch origin
git checkout main
git reset --hard origin/main
nix-shell
"""