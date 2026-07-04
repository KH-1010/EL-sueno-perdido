#!/usr/bin/env python3
"""
Create latest TSV files from NoPayStation data
"""

import os
import csv
import sys
from datetime import datetime

csv.field_size_limit(2**20)

# Input directory
NPS_DIR = "resources/database/content/official/nopaystation"
OUTPUT_DIR = "resources/database/content/latest"

# Files to combine for each category
CATEGORY_FILES = {
    "games": [
        "ps3_games.tsv",
        "psv_games.tsv",
        "psp_games.tsv",
        "psx_games.tsv",
        "psm_games.tsv",
    ],
    "dlcs": [
        "ps3_dlcs.tsv",
        "psv_dlcs.tsv",
        "psp_dlcs.tsv",
    ],
    "avatars": [
        "ps3_avatars.tsv",
    ],
    "demos": [
        "ps3_demos.tsv",
        "psv_demos.tsv",
        "psp_demos.tsv",
    ],
}

def read_tsv(filepath):
    """Read TSV file and return list of items."""
    items = []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            items.append(row)
    return items

def get_date(item):
    """Get date from item."""
    date_str = item.get("Last Modification Date", "")
    if date_str:
        try:
            return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        except:
            pass
    return datetime.min

def create_latest_file(category, filenames):
    """Create a latest file for a category."""
    print(f"\n  Processing {category}...")

    all_items = []
    for filename in filenames:
        filepath = os.path.join(NPS_DIR, filename)
        if os.path.exists(filepath):
            items = read_tsv(filepath)
            all_items.extend(items)
            print(f"    {filename}: {len(items)} items")

    print(f"    Total: {len(all_items)} items")

    # Sort by date (newest first)
    all_items.sort(key=get_date, reverse=True)

    # Write output
    output_file = os.path.join(OUTPUT_DIR, f"latest_{category}.tsv")
    with open(output_file, "w", encoding="utf-8") as f:
        # Write header
        f.write("Title ID\tRegion\tName\tPKG direct link\tRAP\tContent ID\tLast Modification Date\tDownload .RAP file\tFile Size\tSHA256\tAdded Date\n")

        for item in all_items:
            title_id = item.get("Title ID", "")
            region = item.get("Region", "")
            name = item.get("Name", "")
            pkg_url = item.get("PKG direct link", "")
            rap = item.get("RAP", "")
            content_id = item.get("Content ID", "")
            last_modified = item.get("Last Modification Date", "")
            file_size = item.get("File Size", "")
            sha256 = item.get("SHA256", "")

            # Use Last Modification Date as Added Date
            added_date = last_modified

            f.write(f"{title_id}\t{region}\t{name}\t{pkg_url}\t{rap}\t{content_id}\t{last_modified}\t\t{file_size}\t{sha256}\t{added_date}\n")

    print(f"    Saved: {output_file}")

def main():
    """Main function."""
    print("=" * 60)
    print("Creating latest TSV files from NoPayStation data")
    print("=" * 60)

    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Create files for each category
    for category, filenames in CATEGORY_FILES.items():
        create_latest_file(category, filenames)

    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)

if __name__ == "__main__":
    main()
