#!/usr/bin/env python3
"""
Create latest_games.tsv from NoPayStation data
"""

import os
import csv
import io
from datetime import datetime

# Input directories
NPS_DIR = "resources/database/content/official/nopaystation"
OUTPUT_DIR = "resources/database/content/latest"

# Files to combine
NPS_FILES = [
    "ps3_games.tsv",
    "psv_games.tsv",
    "psp_games.tsv",
    "psx_games.tsv",
    "psm_games.tsv",
]

def read_tsv(filepath):
    """Read TSV file and return list of games."""
    games = []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            games.append(row)
    return games

def main():
    """Main function."""
    print("=" * 60)
    print("Creating latest_games.tsv")
    print("=" * 60)

    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Combine all games
    all_games = []
    for filename in NPS_FILES:
        filepath = os.path.join(NPS_DIR, filename)
        if os.path.exists(filepath):
            print(f"  Reading {filename}...")
            games = read_tsv(filepath)
            all_games.extend(games)
            print(f"    Found {len(games)} games")

    print(f"\n  Total games: {len(all_games)}")

    # Sort by Last Modification Date (newest first)
    def get_date(game):
        date_str = game.get("Last Modification Date", "")
        if date_str:
            try:
                return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            except:
                pass
        return datetime.min

    all_games.sort(key=get_date, reverse=True)

    # Write output
    output_file = os.path.join(OUTPUT_DIR, "latest_games.tsv")
    with open(output_file, "w", encoding="utf-8") as f:
        # Write header
        f.write("Title ID\tRegion\tName\tPKG direct link\tRAP\tContent ID\tLast Modification Date\tDownload .RAP file\tFile Size\tSHA256\tAdded Date\n")

        for game in all_games:
            title_id = game.get("Title ID", "")
            region = game.get("Region", "")
            name = game.get("Name", "")
            pkg_url = game.get("PKG direct link", "")
            rap = game.get("RAP", "")
            content_id = game.get("Content ID", "")
            last_modified = game.get("Last Modification Date", "")
            file_size = game.get("File Size", "")
            sha256 = game.get("SHA256", "")

            # Use Last Modification Date as Added Date
            added_date = last_modified

            f.write(f"{title_id}\t{region}\t{name}\t{pkg_url}\t{rap}\t{content_id}\t{last_modified}\t\t{file_size}\t{sha256}\t{added_date}\n")

    print(f"\n  Saved: {output_file}")
    print("=" * 60)

if __name__ == "__main__":
    main()
