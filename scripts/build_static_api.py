"""
Export SQLite database to static JSON files for GitHub Pages hosting
Reduces initial load from 77MB to ~350KB by loading only metadata upfront
"""
import sqlite3
import json
import os
import re
from pathlib import Path


def slugify(name):
    """Convert a name to a URL-safe slug"""
    # Replace special characters with underscores, convert to lowercase
    slug = name.lower().replace(' ', '_').replace('/', '_').replace('&', 'and')
    slug = re.sub(r'[^\w\-]', '', slug)
    return slug


def export_metadata(db_path, output_dir):
    """Export app metadata"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get metadata from database
    cursor.execute('SELECT key, value FROM metadata')
    metadata = {row[0]: row[1] for row in cursor.fetchall()}

    # Add statistics
    cursor.execute('SELECT COUNT(*) FROM symbols')
    metadata['total_companies'] = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(DISTINCT sector) FROM symbols WHERE sector IS NOT NULL AND sector != ""')
    metadata['total_sectors'] = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(DISTINCT industry) FROM symbols WHERE industry IS NOT NULL AND industry != ""')
    metadata['total_industries'] = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(DISTINCT basic_industry) FROM symbols WHERE basic_industry IS NOT NULL AND basic_industry != ""')
    metadata['total_basic_industries'] = cursor.fetchone()[0]

    conn.close()

    output_path = Path(output_dir) / 'metadata.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print(f"Exported metadata to {output_path}")
    print(f"  - {metadata['total_companies']} companies")
    print(f"  - {metadata['total_sectors']} sectors")
    print(f"  - {metadata['total_industries']} industries")
    print(f"  - {metadata['total_basic_industries']} basic industries")

    return metadata


def export_symbols(db_path, output_dir):
    """Export all symbols to single JSON file with latest RSI"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get symbols with their latest RSI from monthly_prices
    cursor.execute("""
        SELECT s.symbol, s.name_of_company, s.macro_sector, s.sector,
               s.industry, s.basic_industry, s.market_cap,
               latest_rsi.rsi, latest_rsi.date as rsi_date
        FROM symbols s
        LEFT JOIN (
            SELECT mp.symbol_id, mp.rsi, mp.date
            FROM monthly_prices mp
            INNER JOIN (
                SELECT symbol_id, MAX(date) as max_date
                FROM monthly_prices
                WHERE rsi IS NOT NULL
                GROUP BY symbol_id
            ) latest ON mp.symbol_id = latest.symbol_id AND mp.date = latest.max_date
        ) latest_rsi ON s.id = latest_rsi.symbol_id
        ORDER BY s.name_of_company
    """)

    symbols = []
    for row in cursor.fetchall():
        symbols.append({
            'symbol': row[0],
            'name': row[1],
            'macro_sector': row[2],
            'sector': row[3],
            'industry': row[4],
            'basic_industry': row[5],
            'market_cap': row[6],
            'rsi': row[7],
            'rsi_date': row[8]
        })

    conn.close()

    output_path = Path(output_dir) / 'symbols.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(symbols, f, ensure_ascii=False, indent=2)

    # Count symbols with RSI
    symbols_with_rsi = sum(1 for s in symbols if s['rsi'] is not None)

    file_size_kb = output_path.stat().st_size / 1024
    print(f"Exported {len(symbols)} symbols to {output_path} ({file_size_kb:.1f} KB)")
    print(f"  - {symbols_with_rsi} symbols have RSI data")

    return symbols


def export_sectors(db_path, output_dir):
    """Export sectors data with index and individual historical data"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Export sector index with latest RSI
    cursor.execute("""
        SELECT sector, rsi, date, close,
               (SELECT COUNT(*) FROM symbols s WHERE s.sector = sp.sector) as company_count
        FROM sector_prices sp
        WHERE sp.date = (
            SELECT MAX(date) FROM sector_prices WHERE sector = sp.sector
        )
        ORDER BY sector
    """)

    sectors = []
    for row in cursor.fetchall():
        sector_slug = slugify(row[0])
        sectors.append({
            'name': row[0],
            'slug': sector_slug,
            'rsi': row[1],
            'date': row[2],
            'close': row[3],
            'company_count': row[4]
        })

    # Create sectors directory
    sectors_dir = Path(output_dir) / 'sectors'
    sectors_dir.mkdir(parents=True, exist_ok=True)

    # Write index
    index_path = sectors_dir / 'index.json'
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(sectors, f, ensure_ascii=False, indent=2)

    index_size_kb = index_path.stat().st_size / 1024
    print(f"Exported {len(sectors)} sectors to index ({index_size_kb:.1f} KB)")

    # Export each sector's historical data
    total_history_size = 0
    for sector in sectors:
        cursor.execute("""
            SELECT date, open, high, low, close, rsi
            FROM sector_prices
            WHERE sector = ?
            ORDER BY date
        """, (sector['name'],))

        history = []
        for row in cursor.fetchall():
            history.append({
                'date': row[0],
                'open': row[1],
                'high': row[2],
                'low': row[3],
                'close': row[4],
                'rsi': row[5]
            })

        sector_path = sectors_dir / f"{sector['slug']}.json"
        with open(sector_path, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

        file_size_kb = sector_path.stat().st_size / 1024
        total_history_size += file_size_kb

    conn.close()
    print(f"Exported sector historical data ({total_history_size:.1f} KB total)")

    return sectors


def export_industries(db_path, output_dir):
    """Export industries data with index and individual historical data"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT industry, rsi, date, close,
               (SELECT COUNT(*) FROM symbols s WHERE s.industry = ip.industry) as company_count
        FROM industry_prices ip
        WHERE ip.date = (
            SELECT MAX(date) FROM industry_prices WHERE industry = ip.industry
        )
        ORDER BY industry
    """)

    industries = []
    for row in cursor.fetchall():
        industry_slug = slugify(row[0])
        industries.append({
            'name': row[0],
            'slug': industry_slug,
            'rsi': row[1],
            'date': row[2],
            'close': row[3],
            'company_count': row[4]
        })

    # Create industries directory
    industries_dir = Path(output_dir) / 'industries'
    industries_dir.mkdir(parents=True, exist_ok=True)

    # Write index
    index_path = industries_dir / 'index.json'
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(industries, f, ensure_ascii=False, indent=2)

    index_size_kb = index_path.stat().st_size / 1024
    print(f"Exported {len(industries)} industries to index ({index_size_kb:.1f} KB)")

    # Export each industry's historical data
    total_history_size = 0
    for industry in industries:
        cursor.execute("""
            SELECT date, open, high, low, close, rsi
            FROM industry_prices
            WHERE industry = ?
            ORDER BY date
        """, (industry['name'],))

        history = []
        for row in cursor.fetchall():
            history.append({
                'date': row[0],
                'open': row[1],
                'high': row[2],
                'low': row[3],
                'close': row[4],
                'rsi': row[5]
            })

        industry_path = industries_dir / f"{industry['slug']}.json"
        with open(industry_path, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

        file_size_kb = industry_path.stat().st_size / 1024
        total_history_size += file_size_kb

    conn.close()
    print(f"Exported industry historical data ({total_history_size:.1f} KB total)")

    return industries


def export_basic_industries(db_path, output_dir):
    """Export basic industries data with index and individual historical data"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT basic_industry, rsi, date, close,
               (SELECT COUNT(*) FROM symbols s WHERE s.basic_industry = bip.basic_industry) as company_count
        FROM basic_industry_prices bip
        WHERE bip.date = (
            SELECT MAX(date) FROM basic_industry_prices WHERE basic_industry = bip.basic_industry
        )
        ORDER BY basic_industry
    """)

    basic_industries = []
    for row in cursor.fetchall():
        bi_slug = slugify(row[0])
        basic_industries.append({
            'name': row[0],
            'slug': bi_slug,
            'rsi': row[1],
            'date': row[2],
            'close': row[3],
            'company_count': row[4]
        })

    # Create basic-industries directory
    bi_dir = Path(output_dir) / 'basic-industries'
    bi_dir.mkdir(parents=True, exist_ok=True)

    # Write index
    index_path = bi_dir / 'index.json'
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(basic_industries, f, ensure_ascii=False, indent=2)

    index_size_kb = index_path.stat().st_size / 1024
    print(f"Exported {len(basic_industries)} basic industries to index ({index_size_kb:.1f} KB)")

    # Export each basic industry's historical data
    total_history_size = 0
    for bi in basic_industries:
        cursor.execute("""
            SELECT date, open, high, low, close, rsi
            FROM basic_industry_prices
            WHERE basic_industry = ?
            ORDER BY date
        """, (bi['name'],))

        history = []
        for row in cursor.fetchall():
            history.append({
                'date': row[0],
                'open': row[1],
                'high': row[2],
                'low': row[3],
                'close': row[4],
                'rsi': row[5]
            })

        bi_path = bi_dir / f"{bi['slug']}.json"
        with open(bi_path, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

        file_size_kb = bi_path.stat().st_size / 1024
        total_history_size += file_size_kb

    conn.close()
    print(f"Exported basic industry historical data ({total_history_size:.1f} KB total)")

    return basic_industries


def cleanup_stale_exports(output_dir, expected, dry_run=False):
    """Remove API files this run did not produce.

    Categories get renamed or delisted between runs. Without this their JSON
    lingers on disk: missing from index.json so the dashboard never links to
    it, but still served and still committed to the repo.

    `expected` maps a subdirectory name to the set of slugs just written.
    Returns the list of removed paths.
    """
    api_dir = Path(output_dir)
    stale = []

    for subdir, slugs in expected.items():
        target = api_dir / subdir
        if not target.is_dir():
            continue

        # A category that exported nothing means the query failed or the table
        # is empty. Deleting on that basis would wipe the whole directory, so
        # skip it and say so rather than treating "no results" as "delete all".
        if not slugs:
            print(f"  ! Skipping {subdir}/ - export produced no entries")
            continue

        keep = {f'{slug}.json' for slug in slugs} | {'index.json'}
        stale.extend(p for p in sorted(target.glob('*.json')) if p.name not in keep)

    # Leftovers from compress_api.py. Nothing reads them, and GitHub Pages
    # negotiates compression itself rather than serving .gz variants directly.
    stale.extend(sorted(api_dir.rglob('*.gz')))

    if not stale:
        print("No stale files found.")
        return []

    for path in stale:
        print(f"  {'Would remove' if dry_run else 'Removing'} {path.relative_to(api_dir)}")
        if not dry_run:
            path.unlink()

    verb = 'Would remove' if dry_run else 'Removed'
    print(f"{verb} {len(stale)} stale file(s).")
    return stale


def build_all(db_path='data/vamana.db', output_dir='data/api', dry_run_cleanup=False):
    """Build entire static API from SQLite database"""
    print("=" * 60)
    print("Building static API from SQLite database...")
    print("=" * 60)

    # Check if database exists
    if not Path(db_path).exists():
        print(f"Error: Database file not found: {db_path}")
        return False

    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Export all data
    export_metadata(db_path, output_dir)
    print()

    export_symbols(db_path, output_dir)
    print()

    sectors = export_sectors(db_path, output_dir)
    print()

    industries = export_industries(db_path, output_dir)
    print()

    basic_industries = export_basic_industries(db_path, output_dir)
    print()

    # Drop files left over from previous runs before measuring, so the
    # reported total reflects what is actually being deployed.
    print("Cleaning up stale exports...")
    cleanup_stale_exports(output_dir, {
        'sectors': {s['slug'] for s in sectors},
        'industries': {i['slug'] for i in industries},
        'basic-industries': {bi['slug'] for bi in basic_industries},
    }, dry_run=dry_run_cleanup)
    print()

    # Calculate total size
    api_path = Path(output_dir)
    total_size = sum(f.stat().st_size for f in api_path.rglob('*.json'))
    total_size_kb = total_size / 1024
    total_size_mb = total_size / (1024 * 1024)

    print("=" * 60)
    print(f"Static API build complete!")
    print(f"Total size: {total_size_kb:.1f} KB ({total_size_mb:.2f} MB)")
    print(f"Output directory: {Path(output_dir).absolute()}")
    print("=" * 60)

    return True


if __name__ == '__main__':
    import sys
    build_all(dry_run_cleanup='--dry-run-cleanup' in sys.argv)
