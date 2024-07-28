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
START_DATE = os.getenv('START_DATE', '2019-01-02')
END_DATE = datetime.today().strftime('%Y-%m-%d')
INITIAL_INVESTMENT = int(os.getenv('INITIAL_INVESTMENT', 30000000))
MONTHLY_INVESTMENT = int(os.getenv('MONTHLY_INVESTMENT', 1000000))

# Data URLs
CSV_URL = os.getenv('CSV_URL', 'https://raw.githubusercontent.com/photo2story/my-flutter-app/main/my-flask-app/stock_market.csv')
GITHUB_API_URL = os.getenv('GITHUB_API_URL', 'https://api.github.com/repos/photo2story/my-flutter-app/contents/static/images')

STOCKS = {
    'Technology': ['AAPL', 'MSFT', 'NVDA', 'GOOG', 'AMZN', 'META', 'CRM', 'ADBE', 'AMD', 'ACN', 'QCOM', 'CSCO', 'INTU', 'IBM', 'PDD', 'NOW', 'MS', 'ARM', 'INTC', 'ANET', 'ADI', 'KLAC', 'PANW', 'AMT'],
    'Financials': [ 'V', 'MA', 'BAC', 'WFC', 'BLK', 'BX', 'GS', 'C', 'KKR'],
    'Consumer Cyclical': ['TSLA', 'AMZN', 'HD', 'NKE', 'MCD', 'SBUX', 'TJX', 'BKNG', 'CMG', 'TGT', 'LOW', 'EXPE', 'DG', 'JD'],
    'Healthcare': ['LLY', 'UNH', 'ABBV', 'JNJ', 'MRK', 'TMO', 'ABT', 'PFE', 'DHR', 'CVS', 'CI', 'GILD', 'AMGN', 'ISRG', 'REGN', 'VRTX', 'HCA'],
    'Communication Services': ['META', 'GOOGL', 'NFLX', 'DIS', 'VZ', 'T', 'CMCSA', 'SPOT', 'TWTR', 'ROKU', 'LYFT', 'UBER', 'EA'],
    'Industrials': ['GE', 'UPS', 'BA', 'CAT', 'MMM', 'HON', 'RTX', 'DE', 'LMT', 'NOC', 'UNP', 'WM', 'ETN', 'CSX', 'FDX'],
    'Consumer Defensive': ['WMT', 'KO', 'PEP', 'PG', 'COST', 'MDLZ', 'CL', 'PM', 'MO', 'KHC', 'HSY', 'KR', 'GIS', 'EL', 'STZ', 'MKC'],
    'Energy': ['XOM', 'CVX', 'COP', 'EOG', 'PSX', 'MPC', 'VLO', 'OKE', 'KMI', 'WMB', 'SLB', 'HAL', 'BKR'],
    'Basic Materials': ['LIN', 'ALB', 'NEM', 'FMC', 'APD', 'CF', 'ECL', 'LYB', 'PPG', 'SHW', 'CE', 'DD'],
    'Real Estate': ['AMT', 'PLD', 'EQIX', 'PSA', 'AVB', 'SPG', 'O', 'VICI', 'EXR', 'MAA', 'EQR'],
    'Utilities': ['NEE', 'DUK', 'SO', 'AEP', 'EXC', 'D', 'SRE', 'XEL', 'ED', 'ES', 'PEG', 'WEC']
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

# 추가된 함수: 분석 검증
def is_stock_analysis_complete(ticker):
    result_file_path = os.path.join('static', 'images', f'result_VOO_{ticker}.csv')
    if not os.path.exists(result_file_path):
        return False
    
    df = pd.read_csv(result_file_path, parse_dates=['Date'])
    if df['Date'].min().strftime('%Y-%m-%d') != START_DATE:
        return False
    if df['Date'].max().strftime('%Y-%m-%d') != END_DATE:
        return False
    
    return True

def is_gemini_analysis_complete(ticker):
    report_file_path = os.path.join('static', 'images', f'report_{ticker}.txt')
    return os.path.exists(report_file_path)