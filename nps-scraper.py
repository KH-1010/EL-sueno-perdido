#!/usr/bin/env python3
"""
NoPayStation TSV Scraper
Downloads and converts TSV files from nopaystation.com to JSON format
compatible with the PSN-Content project.
"""

import json
import os
import urllib.request
import csv
import io
from datetime import datetime

# NoPayStation TSV URLs
TSV_FILES = {
    "PS3": {
        "games": "https://nopaystation.com/tsv/PS3_GAMES.tsv",
        "dlcs": "https://nopaystation.com/tsv/PS3_DLCS.tsv",
        "themes": "https://nopaystation.com/tsv/PS3_THEMES.tsv",
        "avatars": "https://nopaystation.com/tsv/PS3_AVATARS.tsv",
        "demos": "https://nopaystation.com/tsv/PS3_DEMOS.tsv",
    },
    "PSV": {
        "games": "https://nopaystation.com/tsv/PSV_GAMES.tsv",
        "dlcs": "https://nopaystation.com/tsv/PSV_DLCS.tsv",
        "themes": "https://nopaystation.com/tsv/PSV_THEMES.tsv",
        "updates": "https://nopaystation.com/tsv/PSV_UPDATES.tsv",
        "demos": "https://nopaystation.com/tsv/PSV_DEMOS.tsv",
    },
    "PSP": {
        "games": "https://nopaystation.com/tsv/PSP_GAMES.tsv",
        "dlcs": "https://nopaystation.com/tsv/PSP_DLCS.tsv",
        "themes": "https://nopaystation.com/tsv/PSP_THEMES.tsv",
        "updates": "https://nopaystation.com/tsv/PSP_UPDATES.tsv",
        "demos": "https://nopaystation.com/tsv/PSP_DEMOS.tsv",
    },
    "PSX": {
        "games": "https://nopaystation.com/tsv/PSX_GAMES.tsv",
    },
    "PSM": {
        "games": "https://nopaystation.com/tsv/PSM_GAMES.tsv",
    },
}

# Output directory
OUTPUT_DIR = "psn-data"


def download_tsv(url):
    """Download TSV file from URL."""
    print(f"  Downloading: {url}")
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            },
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            content = response.read().decode("utf-8")
            return content
    except Exception as e:
        print(f"  Error downloading: {e}")
        return None


def parse_tsv(tsv_content):
    """Parse TSV content and return list of games."""
    games = []
    reader = csv.DictReader(io.StringIO(tsv_content), delimiter="\t")

    for row in reader:
        try:
            # Extract relevant fields
            title_id = row.get("Title ID", "").strip()
            region = row.get("Region", "").strip()
            name = row.get("Name", "").strip()
            pkg_link = row.get("PKG direct link", "").strip()
            content_id = row.get("Content ID", "").strip()
            last_modified = row.get("Last Modification Date", "").strip()
            file_size = row.get("File Size", "").strip()
            sha256 = row.get("SHA256", "").strip()

            # Skip empty entries or missing URIs
            if not name or not pkg_link or pkg_link == "MISSING":
                continue

            # Convert file size from bytes to human-readable format
            try:
                size_bytes = int(file_size)
                if size_bytes >= 1073741824:
                    size_str = f"{size_bytes / 1073741824:.1f} GB"
                elif size_bytes >= 1048576:
                    size_str = f"{size_bytes / 1048576:.1f} MB"
                elif size_bytes >= 1024:
                    size_str = f"{size_bytes / 1024:.1f} KB"
                else:
                    size_str = f"{size_bytes} B"
            except (ValueError, TypeError):
                size_str = file_size

            games.append(
                {
                    "title_id": title_id,
                    "region": region,
                    "title": name,
                    "uri": pkg_link,
                    "content_id": content_id,
                    "uploadDate": last_modified,
                    "fileSize": size_str,
                    "sha256": sha256,
                }
            )
        except Exception as e:
            continue

    return games


def save_json(data, filename):
    """Save data to JSON file."""
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  Saved: {filepath} ({len(data)} entries)")


def main():
    """Main function."""
    print("=" * 60)
    print("NoPayStation TSV Scraper")
    print("=" * 60)

    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Process each platform
    for platform, files in TSV_FILES.items():
        print(f"\n{'=' * 40}")
        print(f"Platform: {platform}")
        print("=" * 40)

        for content_type, url in files.items():
            print(f"\n  Processing {content_type}...")

            # Download TSV
            tsv_content = download_tsv(url)
            if not tsv_content:
                continue

            # Parse TSV
            games = parse_tsv(tsv_content)
            if not games:
                print(f"  No games found in {content_type}")
                continue

            # Save to JSON
            filename = f"{platform.lower()}_{content_type}.json"
            save_json(games, filename)

    print("\n" + "=" * 60)
    print("Scraping complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
