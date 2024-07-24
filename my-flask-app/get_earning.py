import requests
from bs4 import BeautifulSoup
import re

def get_cik_by_ticker(ticker):
    search_url = f"https://www.sec.gov/include/ticker.txt"
    headers = {
        "User-Agent": "Your Name (your_email@example.com)"
    }

    response = requests.get(search_url, headers=headers)
    if response.status_code == 200:
        for line in response.text.splitlines():
            if line.lower().startswith(ticker.lower()):
                return line.split('\t')[1].zfill(10)
    return None

def get_filings(cik):
    base_url = "https://data.sec.gov/submissions/"
    url = f"{base_url}CIK{cik}.json"
    headers = {
        "User-Agent": "Your Name (your_email@example.com)"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

def filter_earnings_reports(filings, num_reports=4):
    earnings_reports = []
    recent_filings = filings.get('filings', {}).get('recent', {})
    forms = recent_filings.get('form', [])
    report_dates = recent_filings.get('reportDate', [])
    accession_numbers = recent_filings.get('accessionNumber', [])
    
    for i, form in enumerate(forms):
        if form == '8-K' and i < len(report_dates) and i < len(accession_numbers):
            earnings_reports.append({
                'date': report_dates[i],
                'accession_number': accession_numbers[i].replace('-', '')
            })
        if len(earnings_reports) >= num_reports:
            break
    
    return earnings_reports

def extract_earnings_data(accession_number, cik):
    base_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_number}/"
    headers = {
        "User-Agent": "Your Name (your_email@example.com)"
    }
    
    # 먼저 8-K 파일 찾기
    index_response = requests.get(f"{base_url}index.json", headers=headers)
    if index_response.status_code == 200:
        index_data = index_response.json()
        for file in index_data.get('directory', {}).get('item', []):
            if file['name'].endswith('.htm'):
                file_url = f"{base_url}{file['name']}"
                response = requests.get(file_url, headers=headers)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    text = soup.get_text()
                    
                    # 실적 데이터 추출 (다양한 형식 고려)
                    revenue_match = re.search(r'(?i)total net sales.*?(\$?\d+(?:\.\d+)?\s*(?:billion|million|B|M)?)', text)
                    eps_match = re.search(r'(?i)earnings per share.*?(\$?\d+\.\d+)', text)
                    
                    if revenue_match and eps_match:
                        revenue = revenue_match.group(1).replace(' billion', 'B').replace(' million', 'M').replace('$', '')
                        eps = eps_match.group(1).replace('$', '')
                        return {
                            'revenue': revenue.strip(),
                            'eps': eps.strip()
                        }
    return None

def get_recent_earnings(ticker, num_reports=4):
    cik = get_cik_by_ticker(ticker)
    if cik:
        filings = get_filings(cik)
        if filings:
            earnings_reports = filter_earnings_reports(filings, num_reports)
            for report in earnings_reports:
                earnings_data = extract_earnings_data(report['accession_number'], cik)
                if earnings_data:
                    report.update(earnings_data)
            return earnings_reports
    return []

# 테스트 코드
ticker = "AAPL"
print(f"--- {ticker} 어닝 발표 ---")
earnings_reports = get_recent_earnings(ticker)
for report in earnings_reports:
    print(f"Date: {report['date']}")
    if 'revenue' in report and 'eps' in report:
        print(f"Revenue: ${report['revenue']}")
        print(f"EPS: ${report['eps']}")
    else:
        print("실적 데이터를 찾을 수 없습니다.")
    print()


# python get_earning.py    