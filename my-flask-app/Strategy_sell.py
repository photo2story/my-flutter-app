# strategy_sell.py
from datetime import datetime

def strategy_sell(date_str, rsi_ta, ppo, ppo_signal, option_strategy):
    # 날짜 문자열을 datetime 객체로 변환
    date = date_str

    # 매도 전략 적용 기간 설정 (예: 8월 한 달 동안)
    sell_start = datetime(date.year, 8, 1)
    sell_end = datetime(date.year, 8, 30)

    # 날짜가 매도 전략 적용 기간 내에 있는지 확인
    if sell_start <= date <= sell_end:
        return 0.5, 'sell 50%', Sudden_fall

    # 변동성이 높은 종목 리스트
    high_volatility_stocks = ['SOXL', 'UPRO', 'TQQQ']
    # 변동성이 낮은 종목 리스트
    low_volatility_stocks = ['AAPL', 'MSFT', 'SPY', 'TSLA', 'NVDA', 'QQQ', '305540.KS', '005490.KS', '373220', 'U', 'IONQ', '086520']

    # PPO와 RSI 조건을 기반으로 매도 전략 설정
    if PPO < PPO_Signal and rsi_ta > 60:
        if stock_ticker in high_volatility_stocks:
            # 변동성이 높은 종목: 50% 매도
            ta_sell_amount = 0.5
        elif stock_ticker in low_volatility_stocks:
            # 변동성이 낮은 종목: 30% 매도
            ta_sell_amount = 0.3
        else:
            # 리스트에 없는 종목에 대한 기본 설정: 30% 매도
            ta_sell_amount = 0.3

        if ta_sell_amount > 0:
            sell_percent = int(ta_sell_amount * 100)
            sell_signal = 'sell {:,}%'.format(sell_percent)
        else:
            sell_signal = None
    else:
        ta_sell_amount = 0
        sell_signal = None

    return ta_sell_amount, sell_signal, Sudden_fall

