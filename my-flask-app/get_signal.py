#### get_signal.py


import pandas as pd
import numpy as np

def monthly_deposit(current_date, prev_month, monthly_investment, cash, invested_amount):
    signal = ''
    if prev_month != f"{current_date.year}-{current_date.month}":
       cash += monthly_investment
       invested_amount += monthly_investment
       signal = 'Monthly invest'
       prev_month = f"{current_date.year}-{current_date.month}"
    return cash, invested_amount, signal, prev_month

def make_investment_decision(current_date, first_trading_day):
    return current_date.weekday() == 0 or (current_date.day <= 7 and current_date >= first_trading_day)

def calculate_ppo_buy_sell_signals(stock_data, index, short_window, long_window, signal_window):
    short_ema = stock_data['Close'].ewm(span=short_window, adjust=False).mean()
    long_ema = stock_data['Close'].ewm(span=long_window, adjust=False).mean()
    ppo = ((short_ema - long_ema) / long_ema) * 100
    ppo_signal = ppo.ewm(span=signal_window, adjust=False).mean()
    ppo_histogram = ppo - ppo_signal
    PPO_BUY = ppo_histogram.iloc[index] > 1.1
    PPO_SELL = ppo_histogram.iloc[index] < -1.1
    return PPO_BUY, PPO_SELL, ppo_histogram.iloc[index]
