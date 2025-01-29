import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from nsepython import *

def fetch_industry_info(symbol):
    if '&' in symbol:
        symbol = symbol.replace('&', '%26')

    url = f"https://www.nseindia.com/api/quote-equity?symbol={symbol}"
    try:
        payload = nsefetch(url)
        industry_info = payload.get('industryInfo', {})
        trade_info = nsefetch(f'https://www.nseindia.com/api/quote-equity?symbol={symbol}&section=trade_info')
        print(symbol, trade_info['marketDeptOrderBook']['tradeInfo'].get('totalMarketCap', None))
        return {
            'macro': industry_info.get('macro', None),
            'sector': industry_info.get('sector', None),
            'industry': industry_info.get('industry', None),
            'basicIndustry': industry_info.get('basicIndustry', None),
            'market cap':trade_info['marketDeptOrderBook']['tradeInfo'].get('totalMarketCap', None)
        }
    except Exception as e:
        print(f"Error fetching data for symbol {symbol}: {e}")
        return {
            'macro': 'None',
            'sector': 'None',
            'industry': 'None',
            'basicIndustry': 'None',
            'market cap': 'None'
        }