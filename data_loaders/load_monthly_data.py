import pandas as pd
import sys
import os 

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..')))
from yfinance import *
from nsepython import *

df = pd.read_csv('../data/symbols/symbol_data.csv')
df.rename(columns={'SYMBOL': 'symbol', 'NAME OF COMPANY': 'company_name', 'basicIndustry': 'basic_industry'}, inplace=True)

for index, row in df.iterrows():
    data = download(
        tickers=row['symbol'] + '.NS', 
        interval='1mo', 
        start='2020-01-01', 
        end='2025-01-31'
    )

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    data['Symbol'] = row['symbol']
    data.reset_index(inplace=True)
    data = data[['Date', 'Symbol', 'Open', 'High', 'Low', 'Close', 'Volume']]

    filename = f"../data/monthly_data/{row['company_name'].replace(' ', '_')}.csv"
    data.to_csv(filename, index=False)
    print(index, row['symbol'])

print(len(os.listdir('../data/monthly_data')))