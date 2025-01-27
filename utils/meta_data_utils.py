import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from nsepython import *
# symbol_data = {
#     'ARE&M': 'ARE%26M',
#     'GMRP&UI': 'GMRP&UI',
#     'GVT&D': 'GVT&D',
#     'IL&FSENGG': 'IL&FSENGG',
#     'IL&FSTRANS': 'IL&FSTRANS',
#     'J&KBANK': 'J&KBANK',
#     'M&M': 'M&M',
#     'M&MFIN': 'M&MFIN',
#     'S&SPOWER': 'S&SPOWER'
# }
def fetch_industry_info(symbol):
    if '&' in symbol:
        symbol = symbol.replace('&', '%26')

    url = f"https://www.nseindia.com/api/quote-equity?symbol={symbol}"
    try:
        payload = nsefetch(url)
        industry_info = payload.get('industryInfo', {})
        print(symbol)
        return {
            'macro': industry_info.get('macro', None),
            'sector': industry_info.get('sector', None),
            'industry': industry_info.get('industry', None),
            'basicIndustry': industry_info.get('basicIndustry', None)
        }
    except Exception as e:
        print(f"Error fetching data for symbol {symbol}: {e}")
        return {
            'macro': 'None',
            'sector': 'None',
            'industry': 'None',
            'basicIndustry': 'None'
        }