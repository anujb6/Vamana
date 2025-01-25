from nsepython import *
import pandas as pd
from tqdm import tqdm 

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import meta_data_utils

df = pd.read_csv("data/equity_symbols.csv")

df = df[['SYMBOL', 'NAME OF COMPANY']]
tqdm.pandas()
industry_data = df['SYMBOL'].apply(meta_data_utils.fetch_industry_info)
industry_df = pd.DataFrame(industry_data.tolist())
df = pd.concat([df, industry_df], axis=1)
df.to_csv(r'C:\Users\AnujBhor\Desktop\nsepython\data\symbol_data.csv')


