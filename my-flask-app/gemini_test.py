import asyncio
import time
import sys
from gemini import analyze_with_gemini

STOCKS = [
    'AAPL', 'MSFT', 'AMZN', 
    'FB', 'GOOG', 'GOOGL', 
    'BRK.B', 'JNJ', 'V', 'PG', 'NVDA', 'UNH', 'HD', 'MA', 
    'PYPL', 'DIS', 'NFLX', 'XOM', 'VZ', 'PFE', 'T', 'KO', 'ABT', 'MRK', 'CSCO', 'ADBE', 'CMCSA', 'NKE', 
    'INTC', 'PEP', 'TMO', 'CVX', 'ORCL', 'ABBV', 'AVGO', 'MCD', 'QCOM', 'MDT', 'BMY', 'AMGN', 'UPS', 'CRM', 
    'MS', 'HON', 'C', 'GILD', 'DHR', 'BA', 'IBM', 'MMM', 'TSLA', 'TXN', 'SBUX', 'COST', 'AMD', 'TMUS', 
    'CHTR', 'INTU', 'ADP', 'MU', 'MDLZ', 'ISRG', 'BKNG', 'ADI', 'ATVI', 'LRCX', 'AMAT', 'REGN', 'NXPI', 
    'KDP', 'MAR', 'KLAC', 'WMT', 'JPM','SPY', 'VOO', 'VTI', 'VGT', 'VHT', 'VCR', 'VFH',
    'QQQ', 'TQQQ', 'SOXX', 
    'SOXL', 'UPRO'
]

def print_progress_bar(seconds):
    total_ticks = 30
    interval = seconds / total_ticks
    for i in range(total_ticks + 1):
        bar = '[' + '>' * i + ' ' * (total_ticks - i) + ']'
        sys.stdout.write(f'\rWaiting {seconds} seconds: {bar}')
        sys.stdout.flush()
        time.sleep(interval)
    print()

async def analyze_stocks():
    for ticker in STOCKS:
        print(f"Analyzing {ticker}")
        result = analyze_with_gemini(ticker)
        print(result)
        print_progress_bar(20)  # 20초 대기

if __name__ == "__main__":
    asyncio.run(analyze_stocks())

# python gemini_test.py  