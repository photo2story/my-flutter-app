import os
import asyncio
from flask import Flask, jsonify
from datetime import datetime
from get_ticker import load_tickers, search_tickers, get_ticker_name, get_ticker_from_korean_name
from estimate_stock import estimate_snp, estimate_stock
from Results_plot import plot_comparison_results
from Results_plot_mpl import plot_results_mpl
from get_compare_stock_data import merge_csv_files, load_sector_info

app = Flask(__name__)

# 주식 관련 변수들 설정
stocks = ['QQQ', 'NVDA', 'BAC', 'COIN']
start_date = "2022-01-01"
end_date = datetime.today().strftime('%Y-%m-%d')
initial_investment = 30000000
monthly_investment = 1000000

# 비동기 함수 정의
async def backtest_and_send(stock, option_strategy):
    total_account_balance, total_rate, str_strategy, invested_amount, str_last_signal, min_stock_data_date, file_path, result_df = estimate_stock(
        stock, start_date, end_date, initial_investment, monthly_investment, option_strategy)
    min_stock_data_date = str(min_stock_data_date).split(' ')[0]
    user_stock_file_path1 = file_path

    file_path = estimate_snp(stock, 'VOO', min_stock_data_date, end_date, initial_investment, monthly_investment, option_strategy, result_df)
    user_stock_file_path2 = file_path

    name = get_ticker_name(stock)

    plot_comparison_results(user_stock_file_path1, user_stock_file_path2, stock, 'VOO', total_account_balance, total_rate, str_strategy, invested_amount, min_stock_data_date)

# 플라스크 엔드포인트 정의
@app.route('/run-backtest')
def run_backtest():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    for stock in stocks:
        loop.run_until_complete(backtest_and_send(stock, 'modified_monthly'))
    loop.close()
    return jsonify({"message": "Backtesting completed and results have been processed."})

if __name__ == '__main__':
    app.run(debug=True)
