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
