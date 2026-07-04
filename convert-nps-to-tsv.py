#!/usr/bin/env python3
"""
Convert NoPayStation JSON files to TSV format compatible with PSN-Content
"""

import json
import os
import glob

# Input directory
INPUT_DIR = "psn-data"
# Output directory
OUTPUT_DIR = "psn-data/tsv"


def convert_json_to_tsv(input_file, output_file):
    """Convert JSON file to TSV format."""
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    with open(output_file, "w", encoding="utf-8") as f:
        # Write header
        f.write("Title ID\tRegion\tName\tPKG direct link\tRAP\tContent ID\tLast Modification Date\tDownload .RAP file\tFile Size\tSHA256\n")

        for game in data:
            title_id = game.get("title_id", "")
            region = game.get("region", "")
            title = game.get("title", "")
            uri = game.get("uri", "")
            content_id = game.get("content_id", "")
            upload_date = game.get("uploadDate", "")
            file_size = game.get("fileSize", "")
            sha256 = game.get("sha256", "")

            # Convert file size back to bytes for TSV format
            size_bytes = 0
            if file_size:
                try:
                    if "GB" in file_size:
                        size_bytes = int(float(file_size.replace(" GB", "")) * 1073741824)
                    elif "MB" in file_size:
                        size_bytes = int(float(file_size.replace(" MB", "")) * 1048576)
                    elif "KB" in file_size:
                        size_bytes = int(float(file_size.replace(" KB", "")) * 1024)
                    elif "B" in file_size:
                        size_bytes = int(file_size.replace(" B", ""))
                except (ValueError, TypeError):
                    size_bytes = 0

            # Write TSV line
            f.write(f"{title_id}\t{region}\t{title}\t{uri}\t\t{content_id}\t{upload_date}\t\t{size_bytes}\t{sha256}\n")

    print(f"  Converted: {input_file} -> {output_file} ({len(data)} entries)")


def main():
    """Main function."""
    print("=" * 60)
    print("NoPayStation JSON to TSV Converter")
    print("=" * 60)

    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Find all JSON files
    json_files = glob.glob(os.path.join(INPUT_DIR, "*.json"))

    for json_file in json_files:
        filename = os.path.basename(json_file)
        tsv_file = os.path.join(OUTPUT_DIR, filename.replace(".json", ".tsv"))

        print(f"\nProcessing {filename}...")
        convert_json_to_tsv(json_file, tsv_file)

    print("\n" + "=" * 60)
    print("Conversion complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
