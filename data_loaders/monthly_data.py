import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..')))
import yfinance as yf
from database import DatabaseWriter


def load(symbol_data_path, start_date, end_date, interval, db_path='data/vamana.db'):
    """
    Load monthly price data from Yahoo Finance and store directly in SQLite database.

    Args:
        symbol_data_path: Path to CSV with symbol data
        start_date: Start date for data fetch (e.g., '2010-01-01')
        end_date: End date for data fetch
        interval: Data interval (e.g., '1mo' for monthly)
        db_path: Path to SQLite database
    """
    df = pd.read_csv(symbol_data_path)
    total_symbols = len(df)
    successful = 0
    failed = 0

    with DatabaseWriter(db_path) as db:
        # Pre-load symbol cache
        db.get_all_symbols()

        for index, row in df.iterrows():
            symbol = row['symbol']
            company_name = row['name of company']

            print(f"[{index + 1}/{total_symbols}] Fetching data for {symbol}...")

            try:
                data = yf.download(
                    tickers=symbol + '.NS',
                    interval=interval,
                    start=start_date,
                    end=end_date,
                    progress=False
                )

                if data.empty:
                    print(f"  No data returned for {symbol}, skipping")
                    failed += 1
                    continue

                if isinstance(data.columns, pd.MultiIndex):
                    data.columns = data.columns.get_level_values(0)

                data['symbol'] = symbol
                data.reset_index(inplace=True)

                data = data[['Date', 'symbol', 'Open', 'High', 'Low', 'Close', 'Volume']]
                data.rename(columns={
                    'Date': 'date',
                    'Open': 'open',
                    'High': 'high',
                    'Low': 'low',
                    'Close': 'close',
                    'Volume': 'volume'
                }, inplace=True)

                # Insert into database
                records = db.insert_monthly_prices(symbol, data)

                if records > 0:
                    print(f"  Saved {records} records for {symbol}")
                    successful += 1
                else:
                    print(f"  Symbol {symbol} not found in database")
                    failed += 1

            except Exception as e:
                print(f"  Error fetching {symbol}: {e}")
                failed += 1

        # Update metadata
        from datetime import datetime
        db.update_metadata('monthly_data_last_updated', datetime.now().isoformat())

    print(f"\nSummary: {successful} successful, {failed} failed out of {total_symbols} symbols")
