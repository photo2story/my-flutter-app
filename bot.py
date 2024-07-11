import os
import asyncio
from dotenv import load_dotenv
import discord
from discord.ext import tasks, commands

# 사용자 정의 모듈 임포트
from get_ticker import get_ticker_from_korean_name, search_tickers_and_respond, update_stock_market_csv
from estimate_stock import estimate_stock
from Results_plot_mpl import plot_results_mpl
from git_operations import move_files_to_images_folder
from github_operations import is_valid_stock, ticker_path
from backtest_send import backtest_and_send
import config

load_dotenv()

TOKEN = os.getenv('DISCORD_APPLICATION_TOKEN')
CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send(f'Bot has successfully logged in as {bot.user.name}')
    else:
        print(f'Failed to get channel with ID {CHANNEL_ID}')

@tasks.loop(minutes=5)
async def send_msg():
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send('Hello')
        print(f'Message sent to channel {CHANNEL_ID}')
    else:
        print(f"Failed to find channel with ID: {CHANNEL_ID}")

# 메시지 수신 ID를 추적하는 세트
processed_message_ids = set()

@bot.command()
async def buddy(ctx):
    loop = asyncio.get_running_loop()

    for stock in config.STOCKS:
        await backtest_and_send(ctx, stock, 'modified_monthly', bot)
        if is_valid_stock(stock):
            try:
                plot_results_mpl(stock, config.START_DATE, config.END_DATE)
            except KeyError as e:
                await ctx.send(f"An error occurred while plotting {stock}: {e}")
                print(f"Error plotting {stock}: {e}")
        await asyncio.sleep(2)

    await loop.run_in_executor(None, update_stock_market_csv, ticker_path, config.STOCKS)
    sector_dict = await loop.run_in_executor(None, load_sector_info)
    path = '.'
    await loop.run_in_executor(None, merge_csv_files, path, sector_dict)

    await ctx.send("백테스팅 결과가 섹터별로 정리되었습니다.")
    move_files_to_images_folder()

@bot.command()
async def ticker(ctx, *, query: str = None):
    if query is None:
        await ctx.send("Please enter ticker stock name or ticker.")
        return

    await search_tickers_and_respond(ctx, query)

@bot.command()
async def stock(ctx, *args):
    stock_name = ' '.join(args)
    await ctx.send(f'Arguments passed by command: {stock_name}')
    try:
        info_stock = str(stock_name).upper()
        if info_stock.startswith('K '):
            korean_stock_name = info_stock[2:].upper()
            korean_stock_code = get_ticker_from_korean_name(korean_stock_name)
            if korean_stock_code is None:
                await ctx.send(f'Cannot find the stock {korean_stock_name}.')
                return
            else:
                info_stock = korean_stock_code

        await backtest_and_send(ctx, info_stock, option_strategy='1', bot=bot)
        plot_results_mpl(info_stock, config.START_DATE, config.END_DATE)
        move_files_to_images_folder()
    except Exception as e:
        await ctx.send(f'An error occurred: {e}')

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

async def run_bot():
    await bot.start(TOKEN)

if __name__ == '__main__':
    asyncio.run(run_bot())
