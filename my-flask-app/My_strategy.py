# My_strategy.py
import datetime
from typing import Union, Any
import requests 
import yaml
import os,sys
# 경로 설정
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 사용자 정의 모듈 임포트
from Strategy_sell import strategy_sell
from Strategy_buy import strategy_buy
from get_signal import calculate_ppo_buy_sell_signals
import config  # config.py 모듈 임포트

def my_strategy(stock_data, initial_investment, monthly_investment, option_strategy):
    result = []  # 거래 결과를 초기화, 저장하는 용도
    portfolio_value = 0  # 계좌 잔고
    cash = initial_investment  # 현금
    deposit = 0  # 보관금
    invested_amount = initial_investment
    account_balance = 0
    shares = 0
    recent_high = 0
    recent_low = float('inf')
    Invest_day = False
    Sudden_fall = False
    signal = ''
    recent_signal = ''
    prev_month = None  # 현재 월을 비교하여 다르다면, 이는 새로운 달이 시작
    currency = 1300
    stock_ticker = stock_data.iloc[0]['Stock']

    if '.K' in stock_ticker or (len(stock_ticker) == 6 and stock_ticker.isdigit()):
        currency = 1

    PPO_BUY = False  # Initialize neither buy nor sell signal is active
    PPO_SELL = False

    # Initialize the first trading day and first saving day
    first_trading_day, first_saving_day = config.initialize_trading_days(stock_data)

    # Loop over data
    for i, row in stock_data.iterrows():
        current_date = row.name
        index = stock_data.index.get_loc(i)

        # 매달 적립 수행
        cash, invested_amount, signal, prev_month = config.monthly_deposit(current_date, prev_month, monthly_investment, cash, invested_amount)

        # 투자 결정 확인
        Invest_day = config.should_invest_today(current_date, first_trading_day)

        # Calculate current price and performance
        price = row['Close'] * currency  # 종가(원화환산)
        performance = (price - recent_high) / recent_high if recent_high else 0

        # Update recent high and low
        recent_high = max(recent_high, price)
        recent_low = min(recent_low, price)

        # 사용할 지표들
        rsi_ta = row['RSI_14']

        # PPO 매수 및 매도 신호 계산
        PPO_BUY, PPO_SELL, ppo_histogram = calculate_ppo_buy_sell_signals(stock_data, index, short_window=12, long_window=26, signal_window=9)

        if performance < -0.4:
            Sudden_fall = True
            signal = 'Sudden fall'
            shares_to_sell = 0.5 * shares
            shares -= shares_to_sell
            cash += shares_to_sell * price * 0.5
            deposit += shares_to_sell * price * 0.5
            signal = 'sell 50 %' + ' ' + signal

        if Sudden_fall and PPO_BUY:
            shares_to_buy_depot = 0.5 * max(0, deposit) // price
            shares_to_buy_cash = 1.0 * max(0, cash) // price
            shares += shares_to_buy_depot + shares_to_buy_cash
            deposit -= shares_to_buy_depot * price
            cash -= shares_to_buy_cash * price
            signal = 'sudden fall + sma trend rise'
            Sudden_fall = False

        # Check if portfolio value has doubled and sell 50% stocks
        if portfolio_value >= 2 * invested_amount and cash > invested_amount and not PPO_BUY:
            shares_to_sell = 0.5 * shares
            shares -= shares_to_sell
            cash += shares_to_sell * price * 0.5
            deposit += shares_to_sell * price * 0.5
            signal = 'Act1 end!  sell 50%' + ' ' + signal

        sell_result = strategy_sell(current_date, rsi_ta, PPO_SELL, stock_ticker, Sudden_fall, option_strategy)

        if isinstance(sell_result, tuple):
            ta_sell_amount, sell_signal, Sudden_fall = sell_result
        else:
            ta_sell_amount = sell_result
            sell_signal = '' + ' ' + signal

        if Invest_day and ta_sell_amount > 0:
            shares_to_sell = ta_sell_amount * shares
            shares -= shares_to_sell
            cash += shares_to_sell * price
            signal = sell_signal + ' ' + signal

        buy_result = strategy_buy(current_date, price, performance, PPO_BUY, option_strategy)

        if isinstance(buy_result, tuple):
            perform_buy_amount, buy_signal = buy_result
        else:
            perform_buy_amount = buy_result
            buy_signal = '' + signal

        if Invest_day and PPO_BUY:
            shares_to_buy = 0.5 * min(cash, monthly_investment) // price
            shares += shares_to_buy
            cash -= shares_to_buy * price
            signal = 'weekly trade' + ' ' + signal

        if Invest_day and perform_buy_amount > 0:
            shares_to_buy = perform_buy_amount * cash // price
            shares += shares_to_buy
            cash -= shares_to_buy * price
            signal = 'week +' + buy_signal + ' ' + signal

        # Update portfolio value and save result
        portfolio_value = shares * price
        # Calculate account value
        account_balance = portfolio_value + cash + deposit

        rate = (account_balance / invested_amount - 1) * 100

        result.append([current_date, price / currency, account_balance, deposit, cash, portfolio_value, shares, rate, invested_amount, signal, stock_ticker])

        if signal != '':
            recent_signal = current_date.strftime('%Y-%m-%d') + ":" + signal
        signal = ''

        # Find the next first trading day to invest
        if current_date.weekday() == 0 and current_date >= first_trading_day:
            first_trading_day = current_date + datetime.timedelta(days=7)
            Invest_day = False

    # Create dictionary to store results
    result_dict = {
        'result': result,
        'Total_account_balance': account_balance,
        'Total_rate': rate,
        'Last_signal': {'recent_signal': recent_signal, 'PPO Buy Signal': PPO_BUY, 'PPO Sell Signal': PPO_SELL},
        'Strategy': recent_signal,
        'Invested_amount': invested_amount
    }

    return result_dict

