import pandas as pd
import os 
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import meta_data_utils

df = pd.read_csv("../data/symbols/equity_symbols.csv")
df = df[['SYMBOL', 'NAME OF COMPANY']]
industry_data = df['SYMBOL'].apply(meta_data_utils.fetch_industry_info)
industry_df = pd.DataFrame(industry_data.tolist())
df = pd.concat([df, industry_df], axis=1)
df.rename(columns={'SYMBOL': 'symbol', 'NAME OF COMPANY': 'name of company', 'macro': 'macro sector', 'basicIndustry': 'basic industry'}, inplace=True)
df = df[['symbol', 'name of company', 'macro sector', 'sector', 'industry', 'basic industry']]
df.sort_values(by=['industry'], inplace=True)
df.to_csv('../data/symbols/symbol_data.csv')


