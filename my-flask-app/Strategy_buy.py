# strategy_buy.py
from datetime import datetime


def strategy_buy(current_date, price, mfi_ta, sma20_ta, sma60_ta, recent_high, performance, rsi_ta, stochk_ta, stochd_ta, PPO_BUY,option_strategy):
     
    if option_strategy == 'default':
        # 기본 전략(default): PPO 매수 신호가 발생하면 전체 현금의 100%를 투자하고, 
        # 그렇지 않으면 50%를 투자합니다.
        perform_buy_amount = 1.0 if PPO_BUY else 0.5

    elif option_strategy == 'modified_monthly':
        # 변형 적립식 전략(modified_monthly): 수익률이 양수일 때는 투자하지 않고, 
        # 수익률이 음수일 때만 투자합니다.
        if performance > 0:
            perform_buy_amount = 0
            buy_signal = None
        else:
            perform_buy_amount = 1.0 if PPO_BUY else 0.5

    elif option_strategy == 'monthly':
        # 적립식 투자 전략(monthly): 매월 일정 금액을 정기적으로 투자합니다.
        # PPO 매수 신호가 발생하면 100% 투자하고, 그렇지 않으면 50% 투자합니다.
        perform_buy_amount = 1.0

    else:
        # 위 조건에 해당하지 않는 다른 전략의 경우 기본적으로 50% 투자합니다.
        perform_buy_amount = 0.5

    if perform_buy_amount > 0:
        # 투자 비율에 따라 매수 신호를 생성합니다.
        buy_percent = int(perform_buy_amount * 100)
        buy_signal = 'buy {:,}%'.format(buy_percent)
    else:
        # 투자 금액이 0인 경우 매수 신호가 없습니다.
        buy_signal = None

  
    return perform_buy_amount, buy_signal


