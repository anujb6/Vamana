import pandas as pd
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..')))
from yfinance import download



def load(symbol_data_path, start_date, end_date, interval):
    df = pd.read_csv(symbol_data_path)

    for index, row in df.iterrows():
        data = download(
            tickers=row['symbol'] + '.NS', 
            interval=interval, 
            start=start_date, 
            end= end_date
        )

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        data['Symbol'] = row['symbol']
        data.reset_index(inplace=True)

        data = data[['Date', 'Symbol', 'Open', 'High', 'Low', 'Close', 'Volume']]
        data.rename(columns={
            'Date': 'date', 
            'Symbol': 'symbol', 
            'Open': 'open', 
            'High': 'high', 
            'Low': 'low', 
            'Close': 'close', 
            'Volume': 'volume'
        }, inplace=True)

        folder_name = row['name of company'].replace(' ', '_').lower()
        folder_path = f"data/monthly_data/{folder_name}"

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print(f"Created folder: {folder_path}")

        filename = f"{folder_path}/{row['name of company'].replace(' ', '_')}.csv"

        data.to_csv(filename, index=False)
        print(f"Saved data for {row['symbol']} to {filename}")

    print(f"Total files in monthly_data folder: {len(os.listdir('data/monthly_data'))}")