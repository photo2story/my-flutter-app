# app.py
import os
import logging
import threading
import asyncio
from flask import Flask, render_template, send_from_directory, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from discord.ext import commands
import discord
import requests
import certifi
import sys
import nest_asyncio
import git

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.join(os.path.dirname(__file__), 'my-flask-app'))

from datetime import datetime
import pandas as pd
import numpy as np
from get_ticker import load_tickers, search_tickers, get_ticker_name, update_stock_market_csv
from estimate_stock import estimate_snp, estimate_stock
from Results_plot import plot_comparison_results, plot_results_all
from get_compare_stock_data import merge_csv_files, load_sector_info
from Results_plot_mpl import plot_results_mpl
from get_ticker import get_ticker_from_korean_name
from git_operations import move_files_to_images_folder
from github_operations import save_csv_to_github, save_image_to_github, is_valid_stock, ticker_path

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
    
@bot.command()
async def ticker(ctx, *, query: str = None):
    print(f'Command received: ticker with query: {query}')
    if query is None:
        await ctx.send("Please enter ticker stock name or ticker.")
        return

    ticker_dict = load_tickers()
    matching_tickers = search_tickers(query, ticker_dict)

    if not matching_tickers:
        await ctx.send("No search results.")
        return

    response_message = "Search results:\n"
    response_messages = []
    for symbol, name in matching_tickers:
        line = f"{symbol} - {name}\n"
        if len(response_message) + len(line) > 2000:
            response_messages.append(response_message)
            response_message = "Search results (continued):\n"
        response_message += line

    if response_message:
        response_messages.append(response_message)

    for message in response_messages:
        await ctx.send(message)
    print(f'Sent messages for query: {query}')

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

        await backtest_and_send(ctx, info_stock, option_strategy='1')
        plot_results_mpl(info_stock, start_date, end_date)
        move_files_to_images_folder()  # 모든 백테스트 작업이 완료된 후 파일 이동
    except Exception as e:
        await ctx.send(f'An error occurred: {e}')

@bot.command(name='show_all')
async def show_all(ctx):
    try:
        # 모든 결과를 표시하는 함수 호출
        plot_results_all()
        await ctx.send("All results have been successfully displayed.")
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
