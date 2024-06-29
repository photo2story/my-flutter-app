import os
import sys
import asyncio
from datetime import datetime
import matplotlib.pyplot as plt
from flask import Flask

# 현재 디렉토리 경로를 시스템 경로에 추가
sys.path.append(os.path.join(os.path.dirname(__file__), 'my-flask-app'))

# 필요한 모듈을 가져오기
from Data_export import backtest_and_send
from Results_plot_mpl import plot_results_mpl

app = Flask(__name__)

@app.route('/')
def home():
    return "Stock Backtesting Home"

@app.route('/run-backtest')
def run_backtest():
    stocks = ['AAPL', 'MSFT', 'GOOGL']  # 예시로 몇 개의 주식 종목 설정
    start_date = '2020-01-01'
    end_date = datetime.now().strftime('%Y-%m-%d')

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
