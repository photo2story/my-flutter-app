## Results_plot_mpl.py

async def plot_results_mpl(ticker, start_date, end_date):
    """주어진 티커와 기간에 대한 데이터를 사용하여 차트를 생성하고, 결과를 Discord로 전송합니다."""
    # 전체 기간의 데이터를 가져옵니다
    prices = fdr.DataReader(ticker, start_date, end_date)
    
    # 이동 평균과 PPO 계산 (전체 데이터를 사용)
    prices['SMA20'] = prices['Close'].rolling(window=20).mean()
    prices['SMA60'] = prices['Close'].rolling(window=60).mean()
    short_ema = prices['Close'].ewm(span=12, adjust=False).mean()
    long_ema = prices['Close'].ewm(span=26, adjust=False).mean()
    prices['PPO_value'] = ((short_ema - long_ema) / long_ema) * 100
    prices['PPO_signal'] = prices['PPO_value'].ewm(span=9, adjust=False).mean()
    prices['PPO_histogram'] = prices['PPO_value'] - prices['PPO_signal']
    
    # 최신 6개월 데이터로 필터링
    end_date = pd.to_datetime(end_date)
    start_date_6m = end_date - pd.DateOffset(months=6)
    filtered_prices = prices[prices.index >= start_date_6m]
    
    # NaN 값 제거
    filtered_prices.dropna(inplace=True)
    
    # 차트 생성
    indicators = [
        Candlesticks(), SMA(20), SMA(60), Volume(),
        RSI(), PPO(), TradeSpan('ppohist>0')
    ]
    name = get_ticker_name(ticker)
    chart = Chart(title=f'{ticker} ({name}) vs VOO', max_bars=len(filtered_prices))  # max_bars를 데이터 길이로 설정
    chart.plot(filtered_prices, indicators)
    fig = chart.figure
    fig.tight_layout()  # 레이아웃 조정 추가
    
    image_filename = f'result_mpl_{ticker}.png'
    save_figure(fig, image_filename)
    
    # 메시지 작성
    message = (f"Stock: {ticker} ({name})\n"
               f"Close: {filtered_prices['Close'].iloc[-1]:,.2f}\n"
               f"SMA 20: {filtered_prices['SMA20'].iloc[-1]:,.2f}\n"
               f"SMA 60: {filtered_prices['SMA60'].iloc[-1]:,.2f}\n"
               f"PPO Histogram: {filtered_prices['PPO_histogram'].iloc[-1]:,.2f}\n")
    
    # Discord로 메시지 전송
    response = requests.post(DISCORD_WEBHOOK_URL, data={'content': message})
    if response.status_code != 204:
        print('Discord 메시지 전송 실패')
        print(f"Response: {response.status_code} {response.text}")
    else:
        print('Discord 메시지 전송 성공')
    
    # Discord로 이미지 전송
    try:
        with open(image_filename, 'rb') as image_file:
            response = requests.post(DISCORD_WEBHOOK_URL, files={'file': image_file})
            if response.status_code in [200, 204]:
                print(f'Graph 전송 성공: {ticker}')
            else:
                print(f'Graph 전송 실패: {ticker}')
                print(f"Response: {response.status_code} {response.text}")
                
        await move_files_to_images_folder()              
    except Exception as e:
        print(f"Error occurred while sending image: {e}")

"""
python3 -m venv .venv
source .venv/bin/activate
.\.venv\Scripts\activate
cd my-flask-app
python Results_plot_mpl.py
"""