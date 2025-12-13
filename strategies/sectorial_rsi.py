import pandas as pd
import numpy as np
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..')))
from database import DatabaseWriter


def compute(db_path='data/vamana.db'):
    """
    Compute sector-level price indices and RSI from individual stock data.

    Reads stock data from SQLite database, aggregates by sector using equal weighting,
    calculates RSI, and stores the results back in the database.

    Args:
        db_path: Path to SQLite database
    """

    def calculate_rsi(prices, period=14):
        """Calculate RSI for a price series"""
        if len(prices) <= period:
            return pd.Series(np.nan, index=prices.index)

        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).fillna(0)
        loss = (-delta.where(delta < 0, 0)).fillna(0)
        avg_gain = gain.ewm(span=period, adjust=False).mean()
        avg_loss = loss.ewm(span=period, adjust=False).mean()
        rs = avg_gain / avg_loss.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))
        rsi = rsi.fillna(50)  # Use 50 (neutral) instead of 100 for edge cases
        return rsi

    def normalize_prices(df):
        """Normalize OHLC prices to base 100 using first close price"""
        first_close = df['close'].iloc[0]
        if first_close == 0 or pd.isna(first_close):
            return None

        df = df.copy()
        df['open'] = (df['open'] / first_close) * 100
        df['high'] = (df['high'] / first_close) * 100
        df['low'] = (df['low'] / first_close) * 100
        df['close'] = (df['close'] / first_close) * 100
        return df

    with DatabaseWriter(db_path) as db:
        # Get all unique sectors
        sectors = db.get_unique_sectors()
        total_sectors = len(sectors)

        print(f"Computing sector indices for {total_sectors} sectors...")

        # Clear existing sector prices
        db.clear_sector_prices()

        for idx, sector in enumerate(sectors):
            try:
                # Get all symbols in this sector
                symbols = db.get_symbols_by_sector(sector)

                if not symbols:
                    print(f"  [{idx + 1}/{total_sectors}] {sector}: no symbols found, skipping")
                    continue

                all_dates = set()
                valid_companies = []
                company_data = []

                # Load and normalize price data for each company in the sector
                for symbol_id, symbol, company_name in symbols:
                    df = db.get_monthly_prices_for_symbol(symbol_id)

                    if not df.empty and len(df) > 0:
                        df['date'] = pd.to_datetime(df['date'])

                        # Normalize prices to base 100
                        normalized_df = normalize_prices(df)
                        if normalized_df is not None:
                            all_dates.update(normalized_df['date'].tolist())
                            valid_companies.append({'symbol_id': symbol_id, 'symbol': symbol})
                            company_data.append(normalized_df)

                if not valid_companies:
                    print(f"  [{idx + 1}/{total_sectors}] {sector}: no valid data, skipping")
                    continue

                # Create date range dataframe
                date_range = pd.DataFrame({'date': sorted(list(all_dates))})
                date_range['date'] = pd.to_datetime(date_range['date'])

                # Initialize price dataframe
                price_df = date_range.copy()
                price_df['open'] = 0.0
                price_df['high'] = 0.0
                price_df['low'] = 0.0
                price_df['close'] = 0.0

                total_companies = len(valid_companies)
                weight = 1 / total_companies

                # Aggregate normalized prices with equal weighting
                contributing_companies = 0
                for i, company_info in enumerate(valid_companies):
                    df = company_data[i]
                    df = df[['date', 'open', 'high', 'low', 'close']]

                    company_prices = pd.merge(date_range, df, on='date', how='left')
                    company_prices[['open', 'high', 'low', 'close']] = company_prices[['open', 'high', 'low', 'close']].ffill().bfill()

                    if company_prices['close'].iloc[0] == 0:
                        continue

                    contributing_companies += 1
                    price_df['open'] += company_prices['open'] * weight
                    price_df['high'] += company_prices['high'] * weight
                    price_df['low'] += company_prices['low'] * weight
                    price_df['close'] += company_prices['close'] * weight

                # Calculate RSI
                price_df['rsi'] = calculate_rsi(price_df['close'])

                # Resample to monthly
                price_df.set_index('date', inplace=True)
                monthly_price_df = price_df.resample('ME').agg({
                    'open': 'first',
                    'high': 'max',
                    'low': 'min',
                    'close': 'last',
                    'rsi': 'last'
                })

                # Store in database
                records = db.insert_sector_prices(sector, monthly_price_df)

                print(f"  [{idx + 1}/{total_sectors}] {sector}: {records} records saved ({total_companies} companies)")

            except Exception as e:
                print(f"  [{idx + 1}/{total_sectors}] {sector}: Error - {e}")

        # Update metadata
        from datetime import datetime
        db.update_metadata('sector_rsi_last_updated', datetime.now().isoformat())

    print(f"\nSector RSI computation complete.")
