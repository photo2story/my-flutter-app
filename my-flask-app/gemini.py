# gemini.py
import os
import pandas as pd
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# Configure the Gemini API
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def analyze_with_gemini(ticker):
    try:
        # Load data from CSV file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        voo_file = os.path.join(current_dir, '..', 'static', 'images', f'result_VOO_{ticker}.csv')

        if not os.path.exists(voo_file):
            return f'Error: The file for {ticker} does not exist.'

        # Read the CSV file into a dataframe
        df_voo = pd.read_csv(voo_file)

        # Convert dataframe to string
        voo_data_str = df_voo.to_csv(index=False)

        # Prepare the prompt for the Gemini API
        prompt_voo = f"""
        1) 제공된 주식의 수익율(rate)와 S&P 500(VOO)의 수익율(rate_vs)과 비교해서 이격된 정도를 알려줘(간단하게: 최근1년 수익율차이 +50%) {ticker}:\n{voo_data_str}
        2) 제공된 주식의 최근 주가 변동(간단하게: 5일,20일,60일 이동평균 수치로)
        3) RSI, PPO 인덱스 지표를 분석해줘 (간단하게: RSI 40 과매도)
        4) 최근 실적 및 전망(웹검색해서 간단하게: 2분기 매출 $, 3분기 전망 $)
        5) 애널리스트 의견(웹검색해서 간단하게: 매수,강력매수..)
        """

        # Call the Gemini API
        response_voo = model.generate_content(prompt_voo)

        return f'Gemini Analysis for {ticker} (VOO): {response_voo.text}'

    except Exception as e:
        return f'An error occurred while analyzing {ticker} with Gemini API: {e}'

if __name__ == '__main__':
    ticker = 'AAPL'  # Example ticker
    report = analyze_with_gemini(ticker)
    print(report)


"""
source .venv/bin/activate
python gemini.py    
"""