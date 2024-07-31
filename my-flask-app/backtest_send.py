# backtest_and_send.py
import requests
import os, sys
import pandas as pd
import matplotlib.pyplot as plt
from discord.ext import commands
import discord  # discord 모듈 추가

# 사용자 정의 모듈 임포트
from Results_plot import plot_comparison_results
from get_ticker import get_ticker_name, is_valid_stock
from get_compare_stock_data import save_simplified_csv, read_and_process_csv  # 추가된 부분
from git_operations import move_files_to_images_folder
from Get_data import get_stock_data
import My_strategy
from Data_export import export_csv
# Import configuration
import config
# 루트 디렉토리를 sys.path에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# backtest_and_send.py

async def backtest_and_send(ctx, stock, option_strategy='1', bot=None):
    if bot is None:
        raise ValueError("bot 변수는 None일 수 없습니다.")

    await ctx.send(f"backtest_and_send.command: {stock}")

    if not is_valid_stock(stock):
        message = f"Stock market information updates needed. {stock}"
        await ctx.send(message)
        print(message)
        return

    try:
        await ctx.send(f'Estimate_snp: {stock}')  # 주식 이름을 출력
        
        # 주식 데이터 가져오기
        stock_data, min_stock_data_date = get_stock_data(stock, config.START_DATE, config.END_DATE)
        # 전략 실행
        result_df = My_strategy.my_strategy(stock_data, option_strategy)
        
        # 비교 주식 데이터 가져오기, 전략 실행
        stock_data, min_stock_data_date = get_stock_data('VOO', config.START_DATE, config.END_DATE)
        result_df2 = My_strategy.my_strategy(stock_data, option_strategy)
        
        # result_df2의 'rate' 컬럼 이름을 'rate_vs'로 변경
        result_df2.rename(columns={'rate': 'rate_vs'}, inplace=True)
        
        # result_df와 result_df2를 합치기 (여기서는 인덱스를 기준으로 합침)
        combined_df = result_df.join(result_df2['rate_vs'])
        combined_df.fillna(0, inplace=True)  # 누락된 값을 0으로 채우기
  
        
        # 결과 CSV 파일로 저장하기
        safe_ticker = stock.replace('/', '-')
        file_path = 'result_VOO_{}.csv'.format(safe_ticker)  # VOO_TSLA(stock1).csv
        combined_df.to_csv(file_path, float_format='%.2f', index=False)        
        

        # min_stock_data_date = str(min_stock_data_date).split(' ')[0]
        # user_stock_file_path1 = file_path

        # file_path = estimate_snp(stock, 'VOO', option_strategy, result_df)# 검토주식, 비교주식(VOO), 전략, 결과데이터
        # user_stock_file_path2 = file_path
        
        # CSV 파일 간소화
        save_simplified_csv(file_path, stock)

        # plot_comparison_results(stock, min_stock_data_date, config.END_DATE)
        # 파일 이동 및 깃헙 커밋/푸시
        await move_files_to_images_folder()        
        await bot.change_presence(status=discord.Status.online, activity=discord.Game("Waiting"))
    except Exception as e:
        await ctx.send(f"An error occurred while processing {stock}: {e}")
        print(f"Error processing {stock}: {e}")
        
if __name__ == "__main__":
    print("Starting test for back-testing.")
    stock = "AAPL"
    start_date = "2019-01-02"
    end_date = "2024-07-28"
    print(f"Plotting results for {stock1} from {start_date} to {end_date}")

    try:
        plot_comparison_results(stock1, start_date, end_date)
        print("Plotting completed successfully.")
    except Exception as e:
        print(f"Error occurred while plotting results: {e}")


    # python Results_plot.py        


