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
    
    if not eps_data or not revenue_data:
        print("Error retrieving EPS or Revenue data.")
        return
    
    def extract_data(data, unit_key):
        if unit_key not in data['units']:
            print(f"No '{unit_key}' unit data found.")
            return []
        return data['units'][unit_key]

    eps_facts = extract_data(eps_data, 'USD/shares')
    revenue_facts = extract_data(revenue_data, 'USD')

    def filter_quarterly_data(data):
        quarterly_data = []
        for fact in data:
            start = datetime.strptime(fact['start'], "%Y-%m-%d")
            end = datetime.strptime(fact['end'], "%Y-%m-%d")
            # 날짜 차이가 3개월(90일)인 데이터만 필터링
            if (end - start).days <= 92:
                quarterly_data.append(fact)
        return quarterly_data
    
    eps_facts = filter_quarterly_data(eps_facts)
    revenue_facts = filter_quarterly_data(revenue_facts)
    
    # 최신 데이터 4개 추출 및 매칭
    eps_facts = sorted(eps_facts, key=lambda x: x['end'], reverse=True)
    revenue_facts = sorted(revenue_facts, key=lambda x: x['end'], reverse=True)

    quarterly_results = []
    for eps in eps_facts:
        for rev in revenue_facts:
            if eps['end'] == rev['end']:
                quarterly_results.append((eps['end'], eps['filed'], eps['val'], rev['val']))
                break
        if len(quarterly_results) == 4:
            break

    return quarterly_results

if __name__ == '__main__':
    # 테스트 코드
    results = get_recent_eps_and_revenue("tsla")
    if results:
        print("\nQuarterly Results:")
        for end, filed, eps_val, revenue_val in results:
            print(f"{end} (Filed: {filed}): EPS {eps_val}, Revenue {revenue_val / 1e9:.2f} B$")



# python get_earning.py    