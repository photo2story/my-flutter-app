# config.py
import os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

# Discord configuration
DISCORD_APPLICATION_TOKEN = os.getenv('DISCORD_APPLICATION_TOKEN', 'your_token_here')
DISCORD_CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID', 'your_channel_id_here'))
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL', 'your_webhook_url_here')

# Investment and backtest configuration
START_DATE = os.getenv('START_DATE', '2022-01-01')
END_DATE = datetime.today().strftime('%Y-%m-%d')
INITIAL_INVESTMENT = int(os.getenv('INITIAL_INVESTMENT', 30000000))
MONTHLY_INVESTMENT = int(os.getenv('MONTHLY_INVESTMENT', 1000000))

# Data URLs
CSV_URL = os.getenv('CSV_URL', 'https://raw.githubusercontent.com/photo2story/my-flutter-app/main/my-flask-app/stock_market.csv')
GITHUB_API_URL = os.getenv('GITHUB_API_URL', 'https://api.github.com/repos/photo2story/my-flutter-app/contents/static/images')

# Stocks list
STOCKS = {
    'Technology': ['AAPL', 'MSFT', 'AMZN', 'GOOGL', 'NVDA'], 
    'Financials': ['BAC', 'SQ'],
    'Consumer Cyclical': ['TSLA', 'NFLX'],
    'Healthcare': ['LLY','UNH'],
    'Communication Services': ['META', 'VZ'],
    'Industrials': ['GE','UPS'],
    'Consumer Defensive': ['WMT', 'COKE'],
    'Energy': ['XOM'],
    'Basic Materials': ['LIN','ALB'],
    'Real Estate': ['DHI', 'ADSK'], 
    'Utilities': ['DHI', 'ADSK']
    # 'ETFs': ['SPY', 'VOO', 'VTI', 'VGT', 'VHT', 'VCR', 'QQQ', 'TQQQ', 'SOXX', 'SOXL', 'UPRO']
}


# Stock market CSV path
STOCK_MARKET_CSV_PATH = os.getenv('STOCK_MARKET_CSV_PATH', 'path/to/stock_market.csv')
