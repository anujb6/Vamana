"""
Database Writer for Vamana
Provides methods to write stock data directly to SQLite database
"""

import sqlite3
import pandas as pd
from datetime import datetime


class DatabaseWriter:
    def __init__(self, db_path='data/vamana.db'):
        self.db_path = db_path
        self.conn = None
        self._symbol_cache = {}  # Cache symbol -> id mapping

    def connect(self):
        """Create database connection"""
        self.conn = sqlite3.connect(self.db_path)
        return self.conn

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def get_symbol_id(self, symbol):
        """Get symbol_id from cache or database"""
        if symbol in self._symbol_cache:
            return self._symbol_cache[symbol]

        cursor = self.conn.cursor()
        cursor.execute('SELECT id FROM symbols WHERE symbol = ?', (symbol,))
        result = cursor.fetchone()

        if result:
            self._symbol_cache[symbol] = result[0]
            return result[0]
        return None

    def get_all_symbols(self):
        """Get all symbols with their IDs"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, symbol FROM symbols')
        results = cursor.fetchall()
        for symbol_id, symbol in results:
            self._symbol_cache[symbol] = symbol_id
        return results

    def clear_monthly_prices(self, symbol_id=None):
        """Clear monthly prices table, optionally for a specific symbol"""
        cursor = self.conn.cursor()
        if symbol_id:
            cursor.execute('DELETE FROM monthly_prices WHERE symbol_id = ?', (symbol_id,))
        else:
            cursor.execute('DELETE FROM monthly_prices')
        self.conn.commit()

    def clear_sector_prices(self):
        """Clear sector prices table"""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM sector_prices')
        self.conn.commit()

    def clear_industry_prices(self):
        """Clear industry prices table"""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM industry_prices')
        self.conn.commit()

    def clear_basic_industry_prices(self):
        """Clear basic industry prices table"""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM basic_industry_prices')
        self.conn.commit()

    def insert_monthly_prices(self, symbol, data):
        """
        Insert monthly price data for a symbol

        Args:
            symbol: Stock symbol (e.g., 'RELIANCE')
            data: DataFrame with columns: date, open, high, low, close, volume
        """
        symbol_id = self.get_symbol_id(symbol)
        if not symbol_id:
            print(f"Warning: Symbol {symbol} not found in database, skipping")
            return 0

        cursor = self.conn.cursor()

        # Delete existing data for this symbol
        cursor.execute('DELETE FROM monthly_prices WHERE symbol_id = ?', (symbol_id,))

        # Prepare data for batch insert
        records = []
        for _, row in data.iterrows():
            records.append((
                symbol_id,
                str(row.get('date')),
                row.get('open'),
                row.get('high'),
                row.get('low'),
                row.get('close'),
                row.get('volume'),
                None  # RSI will be calculated later
            ))

        # Batch insert
        cursor.executemany('''
            INSERT INTO monthly_prices
            (symbol_id, date, open, high, low, close, volume, rsi)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', records)

        self.conn.commit()
        return len(records)

    def update_rsi_for_symbol(self, symbol_id, rsi_data):
        """
        Update RSI values for a symbol

        Args:
            symbol_id: The symbol's database ID
            rsi_data: List of tuples (date, rsi_value)
        """
        cursor = self.conn.cursor()

        for date_str, rsi_value in rsi_data:
            cursor.execute('''
                UPDATE monthly_prices
                SET rsi = ?
                WHERE symbol_id = ? AND date = ?
            ''', (rsi_value, symbol_id, date_str))

        self.conn.commit()

    def get_monthly_prices_for_symbol(self, symbol_id):
        """Get all monthly prices for a symbol"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT date, open, high, low, close, volume, rsi
            FROM monthly_prices
            WHERE symbol_id = ?
            ORDER BY date
        ''', (symbol_id,))
        columns = ['date', 'open', 'high', 'low', 'close', 'volume', 'rsi']
        return pd.DataFrame(cursor.fetchall(), columns=columns)

    def get_monthly_prices_for_company(self, company_name):
        """
        Get monthly prices by company name (formatted as folder name)

        Args:
            company_name: Company name formatted as folder name (e.g., 'reliance_industries_limited')
        """
        cursor = self.conn.cursor()
        # Join with symbols table to find by company name
        cursor.execute('''
            SELECT mp.date, mp.open, mp.high, mp.low, mp.close, mp.volume, mp.rsi
            FROM monthly_prices mp
            JOIN symbols s ON mp.symbol_id = s.id
            WHERE LOWER(REPLACE(s.name_of_company, ' ', '_')) = ?
            ORDER BY mp.date
        ''', (company_name.lower(),))
        columns = ['date', 'open', 'high', 'low', 'close', 'volume', 'rsi']
        return pd.DataFrame(cursor.fetchall(), columns=columns)

    def insert_sector_prices(self, sector_name, data):
        """
        Insert sector price data

        Args:
            sector_name: Name of the sector
            data: DataFrame with columns: date, open, high, low, close, rsi (index should be date)
        """
        cursor = self.conn.cursor()

        # Delete existing data for this sector
        cursor.execute('DELETE FROM sector_prices WHERE sector = ?', (sector_name,))

        # Prepare data for batch insert
        records = []
        for date_idx, row in data.iterrows():
            records.append((
                sector_name,
                str(date_idx),
                row.get('open'),
                row.get('high'),
                row.get('low'),
                row.get('close'),
                row.get('rsi')
            ))

        # Batch insert
        cursor.executemany('''
            INSERT INTO sector_prices
            (sector, date, open, high, low, close, rsi)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', records)

        self.conn.commit()
        return len(records)

    def insert_industry_prices(self, industry_name, data):
        """
        Insert industry price data

        Args:
            industry_name: Name of the industry
            data: DataFrame with columns: date, open, high, low, close, rsi (index should be date)
        """
        cursor = self.conn.cursor()

        # Delete existing data for this industry
        cursor.execute('DELETE FROM industry_prices WHERE industry = ?', (industry_name,))

        # Prepare data for batch insert
        records = []
        for date_idx, row in data.iterrows():
            records.append((
                industry_name,
                str(date_idx),
                row.get('open'),
                row.get('high'),
                row.get('low'),
                row.get('close'),
                row.get('rsi')
            ))

        # Batch insert
        cursor.executemany('''
            INSERT INTO industry_prices
            (industry, date, open, high, low, close, rsi)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', records)

        self.conn.commit()
        return len(records)

    def insert_basic_industry_prices(self, basic_industry_name, data):
        """
        Insert basic industry price data

        Args:
            basic_industry_name: Name of the basic industry
            data: DataFrame with columns: date, open, high, low, close, rsi (index should be date)
        """
        cursor = self.conn.cursor()

        # Delete existing data for this basic industry
        cursor.execute('DELETE FROM basic_industry_prices WHERE basic_industry = ?', (basic_industry_name,))

        # Prepare data for batch insert
        records = []
        for date_idx, row in data.iterrows():
            records.append((
                basic_industry_name,
                str(date_idx),
                row.get('open'),
                row.get('high'),
                row.get('low'),
                row.get('close'),
                row.get('rsi')
            ))

        # Batch insert
        cursor.executemany('''
            INSERT INTO basic_industry_prices
            (basic_industry, date, open, high, low, close, rsi)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', records)

        self.conn.commit()
        return len(records)

    def update_metadata(self, key, value):
        """Update or insert metadata"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)
        ''', (key, str(value)))
        self.conn.commit()

    def get_symbols_by_sector(self, sector):
        """Get all symbols in a sector"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, symbol, name_of_company
            FROM symbols
            WHERE sector = ?
        ''', (sector,))
        return cursor.fetchall()

    def get_symbols_by_industry(self, industry):
        """Get all symbols in an industry"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, symbol, name_of_company
            FROM symbols
            WHERE industry = ?
        ''', (industry,))
        return cursor.fetchall()

    def get_symbols_by_basic_industry(self, basic_industry):
        """Get all symbols in a basic industry"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, symbol, name_of_company
            FROM symbols
            WHERE basic_industry = ?
        ''', (basic_industry,))
        return cursor.fetchall()

    def get_unique_sectors(self):
        """Get all unique sectors"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT DISTINCT sector FROM symbols WHERE sector IS NOT NULL AND sector != ''
        ''')
        return [row[0] for row in cursor.fetchall()]

    def get_unique_industries(self):
        """Get all unique industries"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT DISTINCT industry FROM symbols WHERE industry IS NOT NULL AND industry != ''
        ''')
        return [row[0] for row in cursor.fetchall()]

    def get_unique_basic_industries(self):
        """Get all unique basic industries"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT DISTINCT basic_industry FROM symbols WHERE basic_industry IS NOT NULL AND basic_industry != ''
        ''')
        return [row[0] for row in cursor.fetchall()]
