import os
import sys
import asyncio
from datetime import datetime
from flask import Flask

# 현재 디렉토리 경로를 시스템 경로에 추가
sys.path.append(os.path.join(os.path.dirname(__file__), 'my-flask-app'))

# 필요한 모듈을 가져오기
from Data_export import backtest_and_send
from Results_plot_mpl import plot_results_mpl
from get_ticker import load_tickers, search_tickers, get_ticker_name, get_ticker_from_korean_name
from estimate_stock import estimate_snp, estimate_stock
from Results_plot import plot_comparison_results
from get_compare_stock_data import merge_csv_files, load_sector_info

app = Flask(__name__)

stocks = ['QQQ', 'NVDA', 'BAC', 'COIN']  # 주식 종목 리스트
start_date = "2022-01-01"  # 시작 날짜
end_date = datetime.today().strftime('%Y-%m-%d')  # 종료 날짜
initial_investment = 30000000  # 초기 투자금
monthly_investment = 1000000  # 월별 투자금

@app.route('/')
def home():
    return "Stock Backtesting Home"

@app.route('/run-backtest')
def run_backtest():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def main():
        for stock in stocks:
            await backtest_and_send(stock, 'modified_monthly', start_date, end_date, initial_investment, monthly_investment)
            plot_results_mpl(stock, start_date, end_date)
            await asyncio.sleep(2)

    loop.run_until_complete(main())

    return "Backtesting completed and results plotted."

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
