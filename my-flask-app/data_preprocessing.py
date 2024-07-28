import datetime

def initialize_variables(initial_investment):
    """
    초기 변수들을 설정하고 반환하는 함수
    """
    return {
        'portfolio_value': 0,
        'cash': initial_investment,
        'deposit': 0,
        'invested_amount': initial_investment,
        'account_balance': 0,
        'shares': 0,
        'recent_high': 0,
        'recent_low': float('inf'),
        'Invest_day': False,
        'Monthly_invested': False,
        'Sudden_fall': False,
        'signal': '',
        'str_strategy': '',
        'recent_signal': '',
        'prev_month': None,
        'currency': 1300
    }

def get_first_trading_day(first_day):
    """
    첫 거래일을 계산하는 함수
    """
    first_trading_day = first_day + datetime.timedelta(days=1)
    if first_trading_day.weekday() >= 1:
        first_trading_day += datetime.timedelta(days=7 - first_trading_day.weekday())
    return first_trading_day
