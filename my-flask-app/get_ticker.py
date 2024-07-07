#### get_ticker.py
import pandas as pd
import FinanceDataReader as fdr
import csv, os, io, requests
from github_operations import ticker_path  # stock_market.csv 파일 경로
import yfinance as yf
import investpy

ticker_path = os.getenv('CSV_URL', 'https://raw.githubusercontent.com/photo2story/my-flutter-app/main/my-flask-app/stock_market.csv')

def get_ticker_name(ticker):
    df = pd.read_csv(ticker_path)  # stock_market.csv 파일 경로
    result = df.loc[df['Symbol'] == ticker, 'Name']
    name = result.iloc[0] if not result.empty else None
    return name

def get_ticker_market(ticker):
    df = pd.read_csv(ticker_path)  # stock_market.csv 파일 경로
    result = df.loc[df['Symbol'] == ticker, 'Market']
    market = result.iloc[0] if not result.empty else None
    return market

def get_stock_info(ticker):
    info = yf.Ticker(ticker).info
    return {
        'Stock': ticker,
        'Industry': info.get('industry'),
        'Beta': info.get('beta'),
        'Sector': info.get('sector')
    }

def update_stock_market_csv(file_path, tickers_to_update):
    tickers_info = {ticker: get_stock_info(ticker) for ticker in tickers_to_update}
    df = pd.read_csv(file_path, encoding='utf-8-sig')  # Specify encoding
    for i, row in df.iterrows():
        ticker = row['Symbol']
        if ticker in tickers_to_update:
            stock_info = get_stock_info(ticker)
            for key, value in stock_info.items():
                df.at[i, key] = value
    df.to_csv(file_path, index=False, encoding='utf-8-sig')  # Specify encoding

def load_tickers():
    ticker_dict = {}
    ticker_url = 'https://raw.githubusercontent.com/photo2story/my-flutter-app/main/my-flask-app/stock_market.csv'
    response = requests.get(ticker_url)
    response.raise_for_status()
    csv_data = response.content.decode('utf-8')
    csv_reader = csv.reader(io.StringIO(csv_data))
    for rows in csv_reader:
        if len(rows) >= 2:
            ticker_dict[rows[1]] = rows[0]
    return ticker_dict

def search_tickers(stock_name, ticker_dict):
    stock_name_lower = stock_name.lower()
    return [(ticker, name) for name, ticker in ticker_dict.items() if stock_name_lower in name.lower()]

def search_ticker_list_KR():
    url = 'http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13'
    response = requests.get(url)
    response.encoding = 'euc-kr'  # Korean encoding
    df_listing = pd.read_html(response.text, header=0)[0]
    cols_ren = {
        '회사명': 'Name',
        '종목코드': 'Symbol',
        '업종': 'Sector',
    }
    df_listing = df_listing.rename(columns=cols_ren)
    df_listing['market'] = 'KRX'
    df_listing['Symbol'] = df_listing['Symbol'].apply(lambda x: '{:06d}'.format(x))
    df_KR = df_listing[['Symbol', 'Name', 'market', 'Sector']]
    return df_KR

def search_ticker_list_US():
    df_amex = fdr.StockListing('AMEX')
    df_nasdaq = fdr.StockListing('NASDAQ')
    df_nyse = fdr.StockListing('NYSE')
    try:
        df_ETF_US = fdr.StockListing("ETF/US")
        df_ETF_US['market'] = "us_ETF"
        columns_to_select = ['Symbol', 'Name', 'market']
        df_ETF_US = df_ETF_US[columns_to_select]
    except Exception as e:
        print(f"An error occurred while fetching US ETF listings: {e}")
        df_ETF_US = pd.DataFrame(columns=['Symbol', 'Name', 'market'])
    df_amex['market'] = "AMEX"
    df_nasdaq['market'] = "NASDAQ"
    df_nyse['market'] = "NYSE"
    columns_to_select = ['Symbol', 'Name', 'market']
    df_amex = df_amex[columns_to_select]
    df_nasdaq = df_nasdaq[columns_to_select]
    df_nyse = df_nyse[columns_to_select]
    data_frames_US = [df_nasdaq, df_nyse, df_amex, df_ETF_US]
    df_US = pd.concat(data_frames_US, ignore_index=True)
    df_US['Sector'] = 'none'
    df_US = df_US[['Symbol', 'Name', 'market', 'Sector']]
    return df_US

def search_ticker_list_US_ETF():
    df_etfs = investpy.etfs.get_etfs(country='united states')
    df_US_ETF = df_etfs[['symbol', 'name']].copy()
    df_US_ETF['market'] = 'US_ETF'
    df_US_ETF['Sector'] = 'US_ETF'
    df_US_ETF.columns = ['Symbol', 'Name', 'market', 'Sector']
    return df_US_ETF

def get_ticker_list_all():
    df_KR = search_ticker_list_KR()
    df_US = search_ticker_list_US()
    df_US_ETF = search_ticker_list_US_ETF()
    df_combined = pd.concat([df_KR, df_US, df_US_ETF], ignore_index=True)
    df_combined.to_csv(ticker_path, encoding='utf-8-sig', index=False)
    return df_combined

def get_ticker_from_korean_name(name):
    df_KR = search_ticker_list_KR()
    result = df_KR.loc[df_KR['Name'] == name, 'Symbol']
    ticker = result.iloc[0] if not result.empty else None
    return ticker

async def search_tickers_and_respond(ctx, query):
    ticker_dict = load_tickers()
    matching_tickers = search_tickers(query, ticker_dict)
    if not matching_tickers:
        await ctx.send("No search results.")
        return
    response_message = "Search results:\n"
    response_messages = []
    for symbol, name in matching_tickers:
        line = f"{symbol} - {name}\n"
        if len(response_message) + len(line) > 2000:
            response_messages.append(response_message)
            response_message = "Search results (continued):\n"
        response_message += line
    if response_message:
        response_messages.append(response_message)
    for message in response_messages:
        await ctx.send(message)
    print(f'Sent messages for query: {query}')

def is_valid_stock(stock):  # Check if the stock is in the stock market CSV
    try:
        url = 'https://raw.githubusercontent.com/photo2story/my-flutter-app/main/my-flask-app/stock_market.csv'
        stock_market_df = pd.read_csv(url)
        return stock in stock_market_df['Symbol'].values
    except Exception as e:
        print(f"Error checking stock market CSV: {e}")
        return False

if __name__ == "__main__":
    # 사용 예시 python get_ticker.py

    info = get_stock_info('AAPL')
    print(info)
    market = get_ticker_market('086520', ticker_path)
    print(market)
    
    # python get_ticker.py