#!/usr/bin/env python3
"""
Download ALL TSV files from nopaystation.com and rebuild website data files.
"""

import os
import csv
import urllib.request
import time
from datetime import datetime

csv.field_size_limit(2**20)

BASE_URL = "https://nopaystation.com/tsv"
NPS_DIR = "resources/database/content/official/nopaystation"
OFFICIAL_DIR = "resources/database/content/official"
LATEST_DIR = "resources/database/content/latest"
PENDING_DIR = os.path.join(OFFICIAL_DIR, "pending")

# All TSV files on nopaystation.com
MAIN_FILES = [
    "PS3_GAMES", "PS3_DLCS", "PS3_THEMES", "PS3_AVATARS", "PS3_DEMOS",
    "PSV_GAMES", "PSV_DLCS", "PSV_THEMES", "PSV_UPDATES", "PSV_DEMOS",
    "PSP_GAMES", "PSP_DLCS", "PSP_THEMES", "PSP_UPDATES", "PSP_DEMOS",
    "PSM_GAMES", "PSX_GAMES",
]

PENDING_FILES = [
    "PS3_GAMES", "PS3_DLCS", "PS3_THEMES", "PS3_AVATARS", "PS3_DEMOS",
    "PSV_GAMES", "PSV_DLCS", "PSV_THEMES", "PSV_UPDATES", "PSV_DEMOS",
    "PSP_GAMES", "PSP_DLCS", "PSP_THEMES", "PSP_UPDATES", "PSP_DEMOS",
    "PSM_GAMES", "PSX_GAMES",
]

HEADER = "Title ID\tRegion\tName\tPKG direct link\tRAP\tContent ID\tLast Modification Date\tDownload .RAP file\tFile Size\tSHA256"

# Map NPS filenames to lowercase for our directory
FILENAME_MAP = {
    "PS3_GAMES": "ps3_games.tsv",
    "PS3_DLCS": "ps3_dlcs.tsv",
    "PS3_THEMES": "ps3_themes.tsv",
    "PS3_AVATARS": "ps3_avatars.tsv",
    "PS3_DEMOS": "ps3_demos.tsv",
    "PSV_GAMES": "psv_games.tsv",
    "PSV_DLCS": "psv_dlcs.tsv",
    "PSV_THEMES": "psv_themes.tsv",
    "PSV_UPDATES": "psv_updates.tsv",
    "PSV_DEMOS": "psv_demos.tsv",
    "PSP_GAMES": "psp_games.tsv",
    "PSP_DLCS": "psp_dlcs.tsv",
    "PSP_THEMES": "psp_themes.tsv",
    "PSP_UPDATES": "psp_updates.tsv",
    "PSP_DEMOS": "psp_demos.tsv",
    "PSM_GAMES": "psm_games.tsv",
    "PSX_GAMES": "psx_games.tsv",
}

CATEGORY_COMBOS = {
    "games.tsv": ["ps3_games.tsv", "psv_games.tsv", "psp_games.tsv", "psx_games.tsv", "psm_games.tsv"],
    "dlcs.tsv": ["ps3_dlcs.tsv", "psv_dlcs.tsv", "psp_dlcs.tsv"],
    "avatars.tsv": ["ps3_avatars.tsv"],
    "demos.tsv": ["ps3_demos.tsv", "psv_demos.tsv", "psp_demos.tsv"],
    "themes.tsv": ["ps3_themes.tsv", "psv_themes.tsv", "psp_themes.tsv"],
    "game_updates.tsv": ["psv_updates.tsv", "psp_updates.tsv"],
}


def download_file(url, filepath):
    """Download a file from URL."""
    try:
        print(f"  Downloading {url}...")
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()
            with open(filepath, "wb") as f:
                f.write(data)
        lines = sum(1 for _ in open(filepath, "r", encoding="utf-8", errors="replace")) - 1
        print(f"  OK: {lines} items")
        return lines
    except Exception as e:
        print(f"  FAILED: {e}")
        return 0


def count_items(filepath):
    """Count data lines in a TSV file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            count = 0
            for line in f:
                if line.strip() and not line.startswith("Title ID"):
                    count += 1
            return count
    except:
        return 0


def combine_tsv_files(source_files, output_path):
    """Combine multiple TSV files into one."""
    with open(output_path, "w", encoding="utf-8") as out:
        out.write(HEADER + "\n")
        total = 0
        for fname in source_files:
            fpath = os.path.join(NPS_DIR, fname)
            if not os.path.exists(fpath):
                continue
            with open(fpath, "r", encoding="utf-8") as f:
                first = True
                for line in f:
                    if first:
                        first = False
                        if line.strip().startswith("Title ID"):
                            continue
                    if line.strip():
                        out.write(line.rstrip("\n") + "\n")
                        total += 1
        return total


def get_date_sort_key(filepath):
    """Extract date for sorting."""
    items = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip() and not line.startswith("Title ID"):
                    parts = line.split("\t")
                    date_str = parts[6] if len(parts) > 6 else ""
                    try:
                        dt = datetime.strptime(date_str.strip(), "%Y-%m-%d %H:%M:%S")
                    except:
                        dt = datetime.min
                    items.append((dt, line))
    except:
        pass
    return items


def create_latest_files():
    """Create latest_*.tsv files sorted by date."""
    combos = {
        "games": ["ps3_games.tsv", "psv_games.tsv", "psp_games.tsv", "psx_games.tsv", "psm_games.tsv"],
        "dlcs": ["ps3_dlcs.tsv", "psv_dlcs.tsv", "psp_dlcs.tsv"],
        "avatars": ["ps3_avatars.tsv"],
        "demos": ["ps3_demos.tsv", "psv_demos.tsv", "psp_demos.tsv"],
    }

    for cat, files in combos.items():
        print(f"\n  Building latest_{cat}.tsv...")
        all_items = []
        for fname in files:
            fpath = os.path.join(NPS_DIR, fname)
            if not os.path.exists(fpath):
                continue
            all_items.extend(get_date_sort_key(fpath))

        all_items.sort(key=lambda x: x[0], reverse=True)

        output = os.path.join(LATEST_DIR, f"latest_{cat}.tsv")
        with open(output, "w", encoding="utf-8") as f:
            f.write(HEADER + "\tAdded Date\n")
            for dt, line in all_items:
                line = line.rstrip("\n")
                date_str = dt.strftime("%Y-%m-%d %H:%M:%S") if dt != datetime.min else ""
                f.write(f"{line}\t{date_str}\n")
        print(f"    Saved {len(all_items)} items")


def main():
    os.makedirs(NPS_DIR, exist_ok=True)
    os.makedirs(OFFICIAL_DIR, exist_ok=True)
    os.makedirs(LATEST_DIR, exist_ok=True)
    os.makedirs(PENDING_DIR, exist_ok=True)

    print("=" * 60)
    print("Downloading ALL TSV files from nopaystation.com")
    print("=" * 60)

    # Download main TSV files
    print("\n--- Main TSV Files ---")
    for name in MAIN_FILES:
        url = f"{BASE_URL}/{name}.tsv"
        local_name = FILENAME_MAP[name]
        filepath = os.path.join(NPS_DIR, local_name)
        download_file(url, filepath)
        time.sleep(0.5)

    # Download pending TSV files
    print("\n--- Pending TSV Files ---")
    for name in PENDING_FILES:
        url = f"{BASE_URL}/pending/{name}.tsv"
        local_name = FILENAME_MAP[name]
        filepath = os.path.join(PENDING_DIR, local_name)
        download_file(url, filepath)
        time.sleep(0.5)

    # Build combined official files
    print("\n--- Building Official Combined Files ---")
    for out_name, sources in CATEGORY_COMBOS.items():
        output = os.path.join(OFFICIAL_DIR, out_name)
        total = combine_tsv_files(sources, output)
        print(f"  {out_name}: {total} items")

    # Build empty official files
    for cat in ["prototypes.tsv", "tools.tsv"]:
        output = os.path.join(OFFICIAL_DIR, cat)
        with open(output, "w", encoding="utf-8") as f:
            f.write(HEADER + "\n")
        print(f"  {cat}: empty")

    # Build latest files
    print("\n--- Building Latest Files ---")
    create_latest_files()

    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for name in MAIN_FILES:
        local_name = FILENAME_MAP[name]
        filepath = os.path.join(NPS_DIR, local_name)
        if os.path.exists(filepath):
            count = count_items(filepath)
            size = os.path.getsize(filepath)
            print(f"  {local_name}: {count} items ({size:,} bytes)")

    print("\nDone!")


if __name__ == "__main__":
    main()
