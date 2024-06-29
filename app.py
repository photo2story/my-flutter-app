import os
import sys
import asyncio
from datetime import datetime
from flask import Flask
import requests

# 현재 디렉토리 경로를 시스템 경로에 추가
sys.path.append(os.path.join(os.path.dirname(__file__), 'my-flask-app'))

# 필요한 모듈을 가져오기
from datetime import datetime
from get_ticker import load_tickers, search_tickers, get_ticker_name, get_ticker_from_korean_name
from estimate_stock import estimate_snp, estimate_stock
from Results_plot import plot_comparison_results
from Results_plot_mpl import plot_results_mpl
from get_compare_stock_data import merge_csv_files, load_sector_info

app = Flask(__name__)

stocks = ['QQQ', 'NVDA', 'BAC', 'COIN']  # 주식 종목 리스트
start_date = "2022-01-01"  # 시작 날짜
end_date = datetime.today().strftime('%Y-%m-%d')  # 종료 날짜
initial_investment = 30000000  # 초기 투자금
monthly_investment = 1000000  # 월별 투자금

async def backtest_and_send(stock, option_strategy):
    total_account_balance, total_rate, str_strategy, invested_amount, str_last_signal, min_stock_data_date, file_path, result_df = estimate_stock(
        stock, start_date, end_date, initial_investment, monthly_investment, option_strategy)
    min_stock_data_date = str(min_stock_data_date).split(' ')[0]
    user_stock_file_path1 = file_path

    file_path = estimate_snp(stock, 'VOO', min_stock_data_date, end_date, initial_investment, monthly_investment, option_strategy, result_df)
    user_stock_file_path2 = file_path

    name = get_ticker_name(stock)
    DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')
    message = {
        'content': f"Stock: {stock} ({name})\n"
                   f"Total_rate: {total_rate:,.0f} %\n"
                   f"Invested_amount: {invested_amount:,.0f} $\n"
                   f"Total_account_balance: {total_account_balance:,.0f} $\n"
                   f"Last_signal: {str_last_signal} \n"
    }
    response = requests.post(DISCORD_WEBHOOK_URL, json=message)
    if response.status_code != 204:
        print('Failed to send Discord message')
    else:
        print('Successfully sent Discord message')

    plot_comparison_results(user_stock_file_path1, user_stock_file_path2, stock, 'VOO', total_account_balance, total_rate, str_strategy, invested_amount, min_stock_data_date)

@app.route('/')
def home():
    return "Stock Backtesting Home"

@app.route('/run-backtest')
def run_backtest():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def main():
        for stock in stocks:
            await backtest_and_send(stock, 'modified_monthly')
            plot_results_mpl(stock, start_date, end_date)
            await asyncio.sleep(2)

    loop.run_until_complete(main())

    return "Backtesting completed and results plotted."

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
