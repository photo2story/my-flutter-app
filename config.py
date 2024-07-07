import os
from datetime import datetime

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
STOCKS = [
    'AAPL', 'MSFT', 'AMZN', 'FB', 'GOOG', 'GOOGL', 'BRK.B', 'JNJ', 'V', 'PG', 'NVDA', 'UNH', 'HD', 'MA', 
    'PYPL', 'DIS', 'NFLX', 'XOM', 'VZ', 'PFE', 'T', 'KO', 'ABT', 'MRK', 'CSCO', 'ADBE', 'CMCSA', 'NKE', 
    'INTC', 'PEP', 'TMO', 'CVX', 'ORCL', 'ABBV', 'AVGO', 'MCD', 'QCOM', 'MDT', 'BMY', 'AMGN', 'UPS', 'CRM', 
    'MS', 'HON', 'C', 'GILD', 'DHR', 'BA', 'IBM', 'MMM', 'TSLA', 'TXN', 'SBUX', 'COST', 'AMD', 'TMUS', 
    'CHTR', 'INTU', 'ADP', 'MU', 'MDLZ', 'ISRG', 'BKNG', 'ADI', 'ATVI', 'LRCX', 'AMAT', 'REGN', 'NXPI', 
    'KDP', 'MAR', 'KLAC', 'WMT', 'JPM',
    'QQQ', 'TQQQ', 'SOXX', 'SOXL', 'UPRO', 'SPY', 'VOO', 'VTI', 'VGT', 'VHT', 'VCR', 'VFH', 'coin'
]
