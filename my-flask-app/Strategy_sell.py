# Strategy_sell.py

from datetime import datetime

# 티커 리스트 정의
HIGH_VOLATILITY_TICKERS = ['SOXL', 'UPRO', 'TQQQ']
LOW_VOLATILITY_TICKERS = ['AAPL', 'TSLA', 'NVDA', 'QQQ', '305540.KS', '005490.KS', 'SPY', 'MSFT', '373220', 'U', 'IONQ', '086520']
# 일반 티커는 따로 리스트로 관리하지 않음

def strategy_sell(date_str, rsi_ta, PPO_SELL, stock_ticker, Sudden_fall, option_strategy):
    # 날짜 문자열을 datetime 객체로 변환
    date = date_str

    # 매도 전략 적용 기간 설정 (예시: 5월 한 달)
    sell_start = datetime(date.year, 5, 1)
    sell_end = datetime(date.year, 5, 30)

    # 초기화
    ta_sell_amount = 0
    sell_signal = None

    # 매도 전략 적용 기간 내에 매도 신호 발생
    if sell_start <= date <= sell_end:
        ta_sell_amount = 0.5
    else:
        # 고변동성 티커에 대한 매도 전략
        if stock_ticker in HIGH_VOLATILITY_TICKERS:
            if rsi_ta > 60 and PPO_SELL:
                ta_sell_amount = 0.5
        
        # 저변동성 티커에 대한 매도 전략
        elif stock_ticker in LOW_VOLATILITY_TICKERS:
            if rsi_ta > 60 and PPO_SELL:
                ta_sell_amount = 0.3

        # 일반적인 매도 전략
        else:
            if rsi_ta > 60 and PPO_SELL:
                ta_sell_amount = 0.3

    # 매도 신호 설정
    if ta_sell_amount > 0:
        sell_percent = int(ta_sell_amount * 100)
        sell_signal = f'sell {sell_percent}%'
        
    # 매도 신호 없음(디폴트)
    ta_sell_amount = 0
    sell_signal = ''
    return ta_sell_amount, sell_signal, Sudden_fall

