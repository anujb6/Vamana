import os
import sys
import pandas as pd
import talib as ta

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..')))
from database import DatabaseWriter


def compute(db_path='data/vamana.db'):
    """
    Compute RSI for all symbols in the database.

    Reads monthly price data from SQLite, calculates 14-period RSI,
    and updates the RSI column in the database.

    Args:
        db_path: Path to SQLite database
    """
    with DatabaseWriter(db_path) as db:
        # Get all symbols
        symbols = db.get_all_symbols()
        total = len(symbols)
        processed = 0

        print(f"Computing RSI for {total} symbols...")

        for symbol_id, symbol in symbols:
            try:
                # Get price data for this symbol
                df = db.get_monthly_prices_for_symbol(symbol_id)

                if df.empty or len(df) < 15:
                    print(f"  [{processed + 1}/{total}] {symbol}: insufficient data, skipping")
                    processed += 1
                    continue

                # Calculate RSI
                df['close'] = pd.to_numeric(df['close'], errors='coerce')
                df['rsi'] = ta.RSI(df['close'], timeperiod=14)

                # Prepare RSI data for update
                rsi_data = [(row['date'], row['rsi']) for _, row in df.iterrows() if pd.notna(row['rsi'])]

                # Update database
                db.update_rsi_for_symbol(symbol_id, rsi_data)

                print(f"  [{processed + 1}/{total}] {symbol}: RSI computed ({len(rsi_data)} values)")
                processed += 1

            except Exception as e:
                print(f"  [{processed + 1}/{total}] {symbol}: Error - {e}")
                processed += 1

        # Update metadata
        from datetime import datetime
        db.update_metadata('rsi_last_updated', datetime.now().isoformat())

    print(f"\nRSI computation complete. Processed {processed}/{total} symbols.")
