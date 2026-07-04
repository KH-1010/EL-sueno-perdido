#!/usr/bin/env python3
"""
Create official TSV files from NoPayStation data.
These files are required by the DB_PATHS in modern.html for the Browse section.
"""

import os
import csv

csv.field_size_limit(2**20)

NPS_DIR = "resources/database/content/official/nopaystation"
OUT_DIR = "resources/database/content/official"

HEADER = "Title ID\tRegion\tName\tPKG direct link\tRAP\tContent ID\tLast Modification Date\tDownload .RAP file\tFile Size\tSHA256"

CATEGORY_MAP = {
    "games.tsv": ["ps3_games.tsv", "psv_games.tsv", "psp_games.tsv", "psx_games.tsv", "psm_games.tsv"],
    "dlcs.tsv": ["ps3_dlcs.tsv", "psv_dlcs.tsv", "psp_dlcs.tsv"],
    "avatars.tsv": ["ps3_avatars.tsv"],
    "demos.tsv": ["ps3_demos.tsv", "psv_demos.tsv", "psp_demos.tsv"],
    "themes.tsv": ["ps3_themes.tsv", "psv_themes.tsv", "psp_themes.tsv"],
    "game_updates.tsv": ["psv_updates.tsv", "psp_updates.tsv"],
}

EMPTY_CATEGORIES = ["prototypes.tsv", "tools.tsv"]

def combine_tsv(source_files, output_path):
    with open(output_path, "w", encoding="utf-8") as out:
        out.write(HEADER + "\n")
        total = 0
        for fname in source_files:
            fpath = os.path.join(NPS_DIR, fname)
            if not os.path.exists(fpath):
                print(f"  SKIP {fname} (not found)")
                continue
            with open(fpath, "r", encoding="utf-8") as f:
                first = True
                for line in f:
                    if first:
                        first = False
                        if line.strip().startswith("Title ID"):
                            continue
                    if line.strip():
                        out.write(line)
                        total += 1
            print(f"  {fname}: added")
        print(f"  Total: {total} items -> {output_path}")

def create_empty_tsv(output_path, category_name):
    with open(output_path, "w", encoding="utf-8") as out:
        out.write(HEADER + "\n")
    print(f"  Created empty {category_name}")

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    pending_dir = os.path.join(OUT_DIR, "pending")
    os.makedirs(pending_dir, exist_ok=True)

    print("Creating official TSV files from NPS data...")
    for out_name, source_files in CATEGORY_MAP.items():
        print(f"\n{out_name}:")
        combine_tsv(source_files, os.path.join(OUT_DIR, out_name))

    for cat_name in EMPTY_CATEGORIES:
        print(f"\n{cat_name}:")
        create_empty_tsv(os.path.join(OUT_DIR, cat_name), cat_name)

    # Create pending directory files (empty)
    for pending_name in ["games.tsv", "dlcs.tsv", "avatars.tsv", "demos.tsv", "themes.tsv"]:
        p = os.path.join(pending_dir, pending_name)
        if not os.path.exists(p):
            create_empty_tsv(p, f"pending/{pending_name}")

    print("\nDone!")

if __name__ == "__main__":
    main()
