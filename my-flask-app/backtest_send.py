# backtest_and_send.py
import requests
import os
import pandas as pd
import matplotlib.pyplot as plt
from discord.ext import commands
import discord  # discord 모듈 추가
from Results_plot import plot_comparison_results
from get_ticker import get_ticker_name, is_valid_stock
from estimate_stock import estimate_stock, estimate_snp

# Import configuration
import config

# backtest_and_send.py

async def backtest_and_send(ctx, stock, option_strategy='1', bot=None):
    if bot is None:
        raise ValueError("bot 변수는 None일 수 없습니다.")

    await ctx.send(f"backtest_and_send.command1: {stock}")
    await ctx.send(f"backtest_and_send.command2: {stock}")

    if not is_valid_stock(stock):
        message = f"Stock market information updates needed. {stock}"
        await ctx.send(message)
        print(message)
        return

    try:
        total_account_balance, total_rate, str_strategy, invested_amount, str_last_signal, min_stock_data_date, file_path, result_df = estimate_stock(
            stock, config.START_DATE, config.END_DATE, config.INITIAL_INVESTMENT, config.MONTHLY_INVESTMENT, option_strategy)
    # 이하 코드

        await ctx.send(f'backtest_and_send.command2: {stock}')  # 주식 이름을 출력

        min_stock_data_date = str(min_stock_data_date).split(' ')[0]
        user_stock_file_path1 = file_path

        file_path = estimate_snp(stock, 'VOO', min_stock_data_date, config.END_DATE, config.INITIAL_INVESTMENT, config.MONTHLY_INVESTMENT, option_strategy, result_df)
        user_stock_file_path2 = file_path

        name = get_ticker_name(stock)
        message = {
            'content': f"Stock: {stock} ({name})\n"
                    f"Total_rate: {total_rate:,.0f} %\n"
                    f"Invested_amount: {invested_amount:,.0f} $\n"
                    f"Total_account_balance: {total_account_balance:,.0f} $\n"
                    f"Last_signal: {str_last_signal} \n"
        }
        response = requests.post(config.DISCORD_WEBHOOK_URL, json=message)
        if response.status_code != 204:
            print('Failed to send Discord message')
        else:
            print('Successfully sent Discord message')

        plot_comparison_results(user_stock_file_path1, user_stock_file_path2, stock, 'VOO', total_account_balance, total_rate, str_strategy, invested_amount, min_stock_data_date)
        await bot.change_presence(status=discord.Status.online, activity=discord.Game("Waiting"))
    except Exception as e:
        await ctx.send(f"An error occurred while processing {stock}: {e}")
        print(f"Error processing {stock}: {e}")


