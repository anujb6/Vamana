"""
Compress JSON files for faster loading on GitHub Pages
Generates .gz versions of all JSON files in the API directory
GitHub Pages will automatically serve compressed versions when available
"""
import gzip
import shutil
import sys
from pathlib import Path

# Force UTF-8 output for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def compress_json_file(file_path):
    """Compress a single JSON file using GZIP"""
    compressed_path = Path(str(file_path) + '.gz')

    # Read the original file and compress it
    with open(file_path, 'rb') as f_in:
        with gzip.open(compressed_path, 'wb', compresslevel=9) as f_out:
            shutil.copyfileobj(f_in, f_out)

    # Calculate sizes
    original_size = file_path.stat().st_size
    compressed_size = compressed_path.stat().st_size
    reduction = ((1 - compressed_size / original_size) * 100) if original_size > 0 else 0

    # Format sizes for display
    if original_size >= 1024 * 1024:
        orig_display = f"{original_size / (1024 * 1024):.2f} MB"
        comp_display = f"{compressed_size / (1024 * 1024):.2f} MB"
    elif original_size >= 1024:
        orig_display = f"{original_size / 1024:.1f} KB"
        comp_display = f"{compressed_size / 1024:.1f} KB"
    else:
        orig_display = f"{original_size} B"
        comp_display = f"{compressed_size} B"

    # Use ASCII-only display to avoid encoding issues on Windows
    rel_path = file_path.relative_to(file_path.parent.parent).as_posix()
    print(f"  {rel_path}: {orig_display} -> {comp_display} ({reduction:.1f}% reduction)")

    return compressed_size


def compress_api(api_dir='data/api'):
    """Compress all JSON files in API directory"""
    api_path = Path(api_dir)

    if not api_path.exists():
        print(f"Error: API directory not found: {api_dir}")
        print("Run 'python scripts/build_static_api.py' first to build the API.")
        return False

    print("=" * 60)
    print("Compressing JSON API files...")
    print("=" * 60)

    total_original = 0
    total_compressed = 0
    file_count = 0

    # Find all JSON files
    json_files = list(api_path.rglob('*.json'))

    if not json_files:
        print(f"No JSON files found in {api_dir}")
        return False

    for json_file in json_files:
        original_size = json_file.stat().st_size
        compressed_size = compress_json_file(json_file)
        total_original += original_size
        total_compressed += compressed_size
        file_count += 1

    total_reduction = ((1 - total_compressed / total_original) * 100) if total_original > 0 else 0

    print("=" * 60)
    print(f"Compression complete!")
    print(f"Files compressed: {file_count}")
    print(f"Total size: {total_original / (1024 * 1024):.2f} MB -> {total_compressed / (1024 * 1024):.2f} MB")
    print(f"Total reduction: {total_reduction:.1f}%")
    print("=" * 60)
    print("\nCompressed files (.gz) have been created alongside originals.")
    print("GitHub Pages will automatically serve the .gz versions to supported browsers.")

    return True


if __name__ == '__main__':
    compress_api()
