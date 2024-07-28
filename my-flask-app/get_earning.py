# get_earning.py
import requests
from datetime import datetime

def get_cik_by_ticker(ticker):
    search_url = "https://www.sec.gov/include/ticker.txt"
    headers = {
        "User-Agent": "Your Name (your_email@example.com)"
    }
    response = requests.get(search_url, headers=headers)
    if response.status_code == 200:
        for line in response.text.splitlines():
            if line.lower().startswith(ticker.lower()):
                return line.split('\t')[1].zfill(10)
    return None

def get_financial_data(cik, tag):
    url = f"https://data.sec.gov/api/xbrl/companyconcept/CIK{cik}/us-gaap/{tag}.json"
    headers = {
        "User-Agent": "Your Name (your_email@example.com)"
    }
    print(f"Full URL: {url}")
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    print(f"Error retrieving data for {tag}.")
    return None

def get_recent_eps_and_revenue(ticker):
    cik = get_cik_by_ticker(ticker)
    if not cik:
        print(f"Error: CIK not found for ticker {ticker}.")
        return

    eps_data = get_financial_data(cik, "EarningsPerShareBasic")
    revenue_data = get_financial_data(cik, "RevenueFromContractWithCustomerExcludingAssessedTax")
    
    if not eps_data:
        print("Error retrieving EPS data. Checking alternative data points.")
        eps_data = get_financial_data(cik, "EarningsPerShareDiluted")

    if not revenue_data:
        print("Error retrieving Revenue data. Checking alternative data points.")
        revenue_data = get_financial_data(cik, "Revenues")

    if not eps_data:
        print("No EPS data available.")
        return
    
    def extract_data(data, unit_key):
        if data and unit_key in data['units']:
            return data['units'][unit_key]
        print(f"No '{unit_key}' unit data found.")
        return []

    eps_facts = extract_data(eps_data, 'USD/shares')
    revenue_facts = extract_data(revenue_data, 'USD') if revenue_data else []

    def filter_quarterly_data(data):
        quarterly_data = []
        for fact in data:
            start = datetime.strptime(fact['start'], "%Y-%m-%d")
            end = datetime.strptime(fact['end'], "%Y-%m-%d")
            if (end - start).days <= 92:
                quarterly_data.append(fact)
        return quarterly_data
    
    eps_facts = filter_quarterly_data(eps_facts)
    revenue_facts = filter_quarterly_data(revenue_facts) if revenue_facts else []
    
    eps_facts = sorted(eps_facts, key=lambda x: x['end'], reverse=True)
    revenue_facts = sorted(revenue_facts, key=lambda x: x['end'], reverse=True) if revenue_facts else []

    quarterly_results = []
    revenue_dict = {rev['end']: rev for rev in revenue_facts}
    for eps in eps_facts:
        eps_val = eps.get('val', None)
        if eps_val is not None and isinstance(eps_val, (int, float)):
            revenue_val = None
            rev = revenue_dict.get(eps['end'], None)
            if rev:
                revenue_val = rev.get('val', None)
            quarterly_results.append((eps['end'], eps['filed'], eps_val, revenue_val))
        if len(quarterly_results) == 5:
            break

    return quarterly_results

if __name__ == '__main__':
    # 주식 목록
    STOCKS = {
        # 'Technology': ['AAPL', 'MSFT', 'AMZN', 'GOOGL', 'NVDA'], 
        # 'Financials': ['BAC'],
        'Consumer Cyclical': ['TSLA', 'NFLX'],
        # 'Healthcare': ['LLY','UNH'],
        # 'Communication Services': ['META', 'VZ'],
        # 'Industrials': ['GE','UPS'],
        # 'Consumer Defensive': ['WMT', 'KO'],
        # 'Energy': ['XOM'],
        # 'Basic Materials': ['LIN','ALB'],
        # 'Real Estate': ['DHI', 'ADSK'], 
        # 'Utilities': ['EXC']
    }

    for sector, tickers in STOCKS.items():
        for ticker in tickers:
            print(f"\nAnalyzing {ticker} from sector {sector}")
            results = get_recent_eps_and_revenue(ticker)
            if results:
                print("Quarterly Results:")
                for end, filed, eps_val, revenue_val in results:
                    print(f"{end} (Filed: {filed}): EPS {eps_val}, Revenue {revenue_val / 1e9:.2f} B$" if revenue_val is not None else f"{end} (Filed: {filed}): EPS {eps_val}, Revenue: None")
            else:
                print(f"No data found for {ticker}")


# python get_earning.py    