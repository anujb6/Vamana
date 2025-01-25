from nsepython import *

def fetch_industry_info(symbol):
    print(symbol)
    url = f"https://www.nseindia.com/api/quote-equity?symbol={symbol}"
    try:
        payload = nsefetch(url)
        industry_info = payload.get('industryInfo', {})
        return {
            'macro': industry_info.get('macro', None),
            'sector': industry_info.get('sector', None),
            'industry': industry_info.get('industry', None),
            'basicIndustry': industry_info.get('basicIndustry', None)
        }
        print(symbol)
    except Exception as e:
        print(f"Error fetching data for symbol {symbol}: {e}")
        return {
            'macro': None,
            'sector': None,
            'industry': None,
            'basicIndustry': None
        }