"""
Vamana - Stock Market Analysis Pipeline

This script orchestrates the data pipeline:
1. Load symbol data from CSV (API broken, use existing CSV)
2. Fetch monthly price data from Yahoo Finance → SQLite
3. Calculate RSI for individual stocks → SQLite
4. Compute sector/industry/basic industry indices → SQLite

All data is stored directly in SQLite database (data/vamana.db)
"""

from data_loaders import monthly_data, rsi, symbol_data
from strategies import industrial_rsi, sectorial_rsi, basic_indsutrial_rsi
from database import SQLiteExporter
from datetime import datetime

# Configuration
DB_PATH = 'data/vamana.db'
SYMBOL_DATA_PATH = 'data/symbols/symbol_data.csv'
START_DATE = '2010-01-01'
END_DATE = datetime.today().strftime('%Y-%m-%d')
INTERVAL = '1mo'


def init_database():
    """Initialize database schema if it doesn't exist"""
    exporter = SQLiteExporter(DB_PATH)
    exporter.connect()
    exporter.create_schema()
    exporter.create_indexes()

    # Import symbol data from CSV (since API is broken)
    exporter.import_symbol_data(SYMBOL_DATA_PATH)

    exporter.close()
    print(f"Database initialized at {DB_PATH}")


def run_full_pipeline():
    """Run the complete data pipeline"""
    print("=" * 60)
    print("Vamana Data Pipeline")
    print("=" * 60)

    # Step 1: Initialize database
    print("\n[Step 1] Initializing database...")
    init_database()

    # Step 2: Fetch monthly data (uncomment to fetch fresh data)
    # print("\n[Step 2] Fetching monthly price data...")
    monthly_data.load(
        symbol_data_path=SYMBOL_DATA_PATH,
        start_date=START_DATE,
        end_date=END_DATE,
        interval=INTERVAL,
        db_path=DB_PATH
    )

    # Step 3: Calculate RSI for individual stocks
    # print("\n[Step 3] Computing RSI for individual stocks...")
    rsi.compute(db_path=DB_PATH)

    # Step 4: Compute sector indices
    print("\n[Step 4] Computing sector indices...")
    sectorial_rsi.compute(db_path=DB_PATH)

    # Step 5: Compute industry indices
    print("\n[Step 5] Computing industry indices...")
    industrial_rsi.compute(db_path=DB_PATH)

    # Step 6: Compute basic industry indices
    print("\n[Step 6] Computing basic industry indices...")
    basic_indsutrial_rsi.compute(db_path=DB_PATH)

    # Update final metadata
    from database import DatabaseWriter
    with DatabaseWriter(DB_PATH) as db:
        db.update_metadata('last_updated', datetime.now().isoformat())
        db.update_metadata('version', '2.0')

    print("\n" + "=" * 60)
    print("Pipeline complete!")
    print(f"Database saved to: {DB_PATH}")
    print("=" * 60)


def run_aggregation_only():
    """Run only the aggregation steps (sector/industry/basic industry RSI)"""
    print("=" * 60)
    print("Vamana - Aggregation Pipeline")
    print("=" * 60)

    print("\n[Step 1] Computing sector indices...")
    sectorial_rsi.compute(db_path=DB_PATH)

    print("\n[Step 2] Computing industry indices...")
    industrial_rsi.compute(db_path=DB_PATH)

    print("\n[Step 3] Computing basic industry indices...")
    basic_indsutrial_rsi.compute(db_path=DB_PATH)

    # Update metadata
    from database import DatabaseWriter
    with DatabaseWriter(DB_PATH) as db:
        db.update_metadata('last_updated', datetime.now().isoformat())

    print("\n" + "=" * 60)
    print("Aggregation complete!")
    print("=" * 60)


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--aggregate-only':
        run_aggregation_only()
    else:
        run_full_pipeline()
