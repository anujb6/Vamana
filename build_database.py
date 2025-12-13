#!/usr/bin/env python3
"""
Build Vamana SQLite Database

This script converts all CSV data into a single SQLite database file
that can be hosted on GitHub Pages and queried using sql.js-httpvfs.

Usage:
    python build_database.py
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.sqlite_exporter import build_database


if __name__ == '__main__':
    print("=" * 50)
    print("Vamana Database Builder")
    print("=" * 50)

    # Build the database
    build_database(
        output_path='data/vamana.db',
        data_dir='data'
    )

    print("\nDone! You can now commit data/vamana.db to your repository.")
    print("The database will be served via GitHub Pages with HTTP Range request support.")
