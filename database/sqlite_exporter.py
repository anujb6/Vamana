"""
SQLite Exporter for Vamana
Converts CSV data to SQLite database for GitHub Pages hosting with sql.js-httpvfs
"""

import sqlite3
import pandas as pd
import numpy as np
import os
from datetime import datetime


class SQLiteExporter:
    def __init__(self, db_path='data/vamana.db'):
        self.db_path = db_path
        self.conn = None

    def connect(self):
        """Create database connection"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        return self.conn

    def create_schema(self):
        """Create all tables"""
        cursor = self.conn.cursor()

        # Symbols table - company metadata
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS symbols (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL UNIQUE,
                name_of_company TEXT NOT NULL,
                macro_sector TEXT,
                sector TEXT,
                industry TEXT,
                basic_industry TEXT,
                market_cap REAL
            )
        ''')

        # Monthly prices table - individual company prices
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS monthly_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INTEGER,
                rsi REAL,
                FOREIGN KEY (symbol_id) REFERENCES symbols(id)
            )
        ''')

        # Sector prices table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sector_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sector TEXT NOT NULL,
                date TEXT NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                rsi REAL
            )
        ''')

        # Industry prices table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS industry_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                industry TEXT NOT NULL,
                date TEXT NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                rsi REAL
            )
        ''')

        # Basic industry prices table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS basic_industry_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                basic_industry TEXT NOT NULL,
                date TEXT NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                rsi REAL
            )
        ''')

        # Metadata table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metadata (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')

        self.conn.commit()
        print("Schema created successfully")

    def create_indexes(self):
        """Create indexes for optimized HTTP Range queries"""
        cursor = self.conn.cursor()

        indexes = [
            'CREATE INDEX IF NOT EXISTS idx_symbols_sector ON symbols(sector)',
            'CREATE INDEX IF NOT EXISTS idx_symbols_industry ON symbols(industry)',
            'CREATE INDEX IF NOT EXISTS idx_symbols_basic_industry ON symbols(basic_industry)',
            'CREATE INDEX IF NOT EXISTS idx_monthly_prices_symbol_date ON monthly_prices(symbol_id, date)',
            'CREATE INDEX IF NOT EXISTS idx_monthly_prices_date ON monthly_prices(date)',
            'CREATE INDEX IF NOT EXISTS idx_sector_prices_sector_date ON sector_prices(sector, date)',
            'CREATE INDEX IF NOT EXISTS idx_sector_prices_sector ON sector_prices(sector)',
            'CREATE INDEX IF NOT EXISTS idx_industry_prices_industry_date ON industry_prices(industry, date)',
            'CREATE INDEX IF NOT EXISTS idx_industry_prices_industry ON industry_prices(industry)',
            'CREATE INDEX IF NOT EXISTS idx_basic_industry_prices_bi_date ON basic_industry_prices(basic_industry, date)',
            'CREATE INDEX IF NOT EXISTS idx_basic_industry_prices_bi ON basic_industry_prices(basic_industry)',
        ]

        for idx in indexes:
            cursor.execute(idx)

        self.conn.commit()
        print("Indexes created successfully")

    def import_symbol_data(self, csv_path='data/symbols/symbol_data.csv'):
        """Import symbol data from CSV"""
        if not os.path.exists(csv_path):
            print(f"Warning: {csv_path} not found, skipping symbol import")
            return

        df = pd.read_csv(csv_path)

        cursor = self.conn.cursor()

        for _, row in df.iterrows():
            cursor.execute('''
                INSERT OR REPLACE INTO symbols
                (symbol, name_of_company, macro_sector, sector, industry, basic_industry, market_cap)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                row.get('symbol'),
                row.get('name of company'),
                row.get('macro sector'),
                row.get('sector'),
                row.get('industry'),
                row.get('basic industry'),
                row.get('market cap')
            ))

        self.conn.commit()
        print(f"Imported {len(df)} symbols")

    def import_monthly_data(self, main_folder='data/monthly_data'):
        """Import all monthly price data from CSV files"""
        if not os.path.exists(main_folder):
            print(f"Warning: {main_folder} not found, skipping monthly data import")
            return

        cursor = self.conn.cursor()
        total_records = 0

        for subfolder in os.listdir(main_folder):
            subfolder_path = os.path.join(main_folder, subfolder)
            if os.path.isdir(subfolder_path):
                csv_files = [f for f in os.listdir(subfolder_path) if f.endswith('.csv')]
                if csv_files:
                    csv_path = os.path.join(subfolder_path, csv_files[0])
                    try:
                        df = pd.read_csv(csv_path)

                        # Get symbol from data or folder name
                        symbol = df['symbol'].iloc[0] if 'symbol' in df.columns else subfolder.upper()

                        # Get symbol_id
                        cursor.execute('SELECT id FROM symbols WHERE symbol = ?', (symbol,))
                        result = cursor.fetchone()

                        if result:
                            symbol_id = result[0]
                            for _, row in df.iterrows():
                                cursor.execute('''
                                    INSERT INTO monthly_prices
                                    (symbol_id, date, open, high, low, close, volume, rsi)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                ''', (
                                    symbol_id,
                                    str(row.get('date')),
                                    row.get('open'),
                                    row.get('high'),
                                    row.get('low'),
                                    row.get('close'),
                                    row.get('volume'),
                                    row.get('rsi')
                                ))
                            total_records += len(df)
                    except Exception as e:
                        print(f"Error processing {csv_path}: {e}")

        self.conn.commit()
        print(f"Imported {total_records} monthly price records")

    def import_sector_data(self, sectors_folder='data/sectors'):
        """Import sector price data"""
        if not os.path.exists(sectors_folder):
            print(f"Warning: {sectors_folder} not found, skipping sector data import")
            return

        cursor = self.conn.cursor()
        total_records = 0

        for sector_dir in os.listdir(sectors_folder):
            sector_path = os.path.join(sectors_folder, sector_dir)
            if os.path.isdir(sector_path):
                csv_file = os.path.join(sector_path, f'{sector_dir}_price.csv')
                if os.path.exists(csv_file):
                    try:
                        df = pd.read_csv(csv_file)
                        # Convert folder name back to proper sector name
                        sector_name = sector_dir.replace('_', ' ').title()

                        for _, row in df.iterrows():
                            cursor.execute('''
                                INSERT INTO sector_prices
                                (sector, date, open, high, low, close, rsi)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            ''', (
                                sector_name,
                                str(row.get('date')),
                                row.get('open'),
                                row.get('high'),
                                row.get('low'),
                                row.get('close'),
                                row.get('rsi')
                            ))
                        total_records += len(df)
                    except Exception as e:
                        print(f"Error processing {csv_file}: {e}")

        self.conn.commit()
        print(f"Imported {total_records} sector price records")

    def import_industry_data(self, industries_folder='data/industries'):
        """Import industry price data"""
        if not os.path.exists(industries_folder):
            print(f"Warning: {industries_folder} not found, skipping industry data import")
            return

        cursor = self.conn.cursor()
        total_records = 0

        for industry_dir in os.listdir(industries_folder):
            industry_path = os.path.join(industries_folder, industry_dir)
            if os.path.isdir(industry_path):
                csv_file = os.path.join(industry_path, f'{industry_dir}_price.csv')
                if os.path.exists(csv_file):
                    try:
                        df = pd.read_csv(csv_file)
                        # Convert folder name back to proper industry name
                        industry_name = industry_dir.replace('_', ' ').replace('-', '/').title()

                        for _, row in df.iterrows():
                            cursor.execute('''
                                INSERT INTO industry_prices
                                (industry, date, open, high, low, close, rsi)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            ''', (
                                industry_name,
                                str(row.get('date')),
                                row.get('open'),
                                row.get('high'),
                                row.get('low'),
                                row.get('close'),
                                row.get('rsi')
                            ))
                        total_records += len(df)
                    except Exception as e:
                        print(f"Error processing {csv_file}: {e}")

        self.conn.commit()
        print(f"Imported {total_records} industry price records")

    def import_basic_industry_data(self, basic_industries_folder='data/basic_industries'):
        """Import basic industry price data"""
        if not os.path.exists(basic_industries_folder):
            print(f"Warning: {basic_industries_folder} not found, skipping basic industry data import")
            return

        cursor = self.conn.cursor()
        total_records = 0

        for bi_dir in os.listdir(basic_industries_folder):
            bi_path = os.path.join(basic_industries_folder, bi_dir)
            if os.path.isdir(bi_path):
                csv_file = os.path.join(bi_path, f'{bi_dir}_price.csv')
                if os.path.exists(csv_file):
                    try:
                        df = pd.read_csv(csv_file)
                        # Convert folder name back to proper basic industry name
                        bi_name = bi_dir.replace('_', ' ').replace('-', '/').title()

                        for _, row in df.iterrows():
                            cursor.execute('''
                                INSERT INTO basic_industry_prices
                                (basic_industry, date, open, high, low, close, rsi)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            ''', (
                                bi_name,
                                str(row.get('date')),
                                row.get('open'),
                                row.get('high'),
                                row.get('low'),
                                row.get('close'),
                                row.get('rsi')
                            ))
                        total_records += len(df)
                    except Exception as e:
                        print(f"Error processing {csv_file}: {e}")

        self.conn.commit()
        print(f"Imported {total_records} basic industry price records")

    def set_metadata(self, key, value):
        """Set a metadata value"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)
        ''', (key, str(value)))
        self.conn.commit()

    def optimize_database(self):
        """Run VACUUM and ANALYZE for optimization"""
        print("Optimizing database...")
        self.conn.execute('VACUUM')
        self.conn.execute('ANALYZE')
        print("Database optimized")

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print(f"Database saved to {self.db_path}")


def build_database(output_path='data/vamana.db', data_dir='data'):
    """Main function to build the complete database from CSV files"""

    # Remove existing database
    if os.path.exists(output_path):
        os.remove(output_path)
        print(f"Removed existing database: {output_path}")

    exporter = SQLiteExporter(output_path)

    try:
        exporter.connect()

        print("\n=== Building Vamana SQLite Database ===\n")

        print("Step 1: Creating schema...")
        exporter.create_schema()

        print("\nStep 2: Importing symbol data...")
        exporter.import_symbol_data(f'{data_dir}/symbols/symbol_data.csv')

        print("\nStep 3: Importing monthly price data...")
        exporter.import_monthly_data(f'{data_dir}/monthly_data')

        print("\nStep 4: Importing sector data...")
        exporter.import_sector_data(f'{data_dir}/sectors')

        print("\nStep 5: Importing industry data...")
        exporter.import_industry_data(f'{data_dir}/industries')

        print("\nStep 6: Importing basic industry data...")
        exporter.import_basic_industry_data(f'{data_dir}/basic_industries')

        print("\nStep 7: Creating indexes...")
        exporter.create_indexes()

        print("\nStep 8: Setting metadata...")
        exporter.set_metadata('last_updated', datetime.now().isoformat())
        exporter.set_metadata('version', '1.0')

        print("\nStep 9: Optimizing database...")
        exporter.optimize_database()

        # Print summary
        cursor = exporter.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM symbols')
        symbols_count = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM monthly_prices')
        monthly_count = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM sector_prices')
        sector_count = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM industry_prices')
        industry_count = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM basic_industry_prices')
        basic_industry_count = cursor.fetchone()[0]

        print(f"\n=== Database Summary ===")
        print(f"Symbols: {symbols_count}")
        print(f"Monthly prices: {monthly_count}")
        print(f"Sector prices: {sector_count}")
        print(f"Industry prices: {industry_count}")
        print(f"Basic industry prices: {basic_industry_count}")
        print(f"Total records: {symbols_count + monthly_count + sector_count + industry_count + basic_industry_count}")

        # Get file size
        db_size = os.path.getsize(output_path)
        print(f"Database size: {db_size / 1024 / 1024:.2f} MB")

        print(f"\n=== Database created successfully at {output_path} ===")

    finally:
        exporter.close()


if __name__ == '__main__':
    build_database()
