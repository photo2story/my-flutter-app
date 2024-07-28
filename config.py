# config.py
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv()

# Discord configuration
DISCORD_APPLICATION_TOKEN = os.getenv('DISCORD_APPLICATION_TOKEN', 'your_token_here')
DISCORD_CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID', 'your_channel_id_here'))
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL', 'your_webhook_url_here')

# Investment and backtest configuration
START_DATE = os.getenv('START_DATE', '2019-01-01')
END_DATE = datetime.today().strftime('%Y-%m-%d')
INITIAL_INVESTMENT = int(os.getenv('INITIAL_INVESTMENT', 30000000))
MONTHLY_INVESTMENT = int(os.getenv('MONTHLY_INVESTMENT', 1000000))

# Data URLs
CSV_URL = os.getenv('CSV_URL', 'https://raw.githubusercontent.com/photo2story/my-flutter-app/main/my-flask-app/stock_market.csv')
GITHUB_API_URL = os.getenv('GITHUB_API_URL', 'https://api.github.com/repos/photo2story/my-flutter-app/contents/static/images')

# Stocks list
STOCKS = {
    'Technology': ['AAPL', 'MSFT', 'AMZN', 'GOOGL', 'NVDA'], 
    'Financials': ['BAC'],
    'Consumer Cyclical': ['TSLA', 'NFLX'],
    'Healthcare': ['LLY','UNH'],
    'Communication Services': ['META', 'VZ'],
    'Industrials': ['GE','UPS'],
    'Consumer Defensive': ['WMT', 'KO'],
    'Energy': ['XOM'],
    'Basic Materials': ['LIN','ALB'],
    'Real Estate': ['DHI', 'ADSK'], 
    'Utilities': ['EXC']
}

# Stock market CSV path
STOCK_MARKET_CSV_PATH = os.getenv('STOCK_MARKET_CSV_PATH', 'path/to/stock_market.csv')

def initialize_trading_days(stock_data):
    first_day = stock_data.index.min()
    first_trading_day = first_day + timedelta(days=1)
    first_saving_day = first_day + timedelta(days=1)

    if first_trading_day.weekday() >= 1:
        first_trading_day += timedelta(days=7 - first_trading_day.weekday())

    return first_trading_day, first_saving_day

def should_invest_today(current_date, first_trading_day):
    if current_date.weekday() == 0 or (current_date.day <= 7 and current_date >= first_trading_day):
        return True
    return False

def monthly_deposit(current_date, prev_month, monthly_investment, cash, invested_amount):
    signal = ''
    if prev_month != f"{current_date.year}-{current_date.month}":
       cash += monthly_investment
       invested_amount += monthly_investment
       signal = 'Monthly invest'
       prev_month = f"{current_date.year}-{current_date.month}"
    return cash, invested_amount, signal, prev_month
