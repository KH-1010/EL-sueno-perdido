#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  NoPayStation (NPS) High-Speed Parallel Synchronizer v2.0 (Zero Lag CI)     ║
║  مزامنة وقاعدة بيانات بلايستيشن الشاملة — تحميل متوازٍ فائق السرعة ومعالجة ذكية  ║
╚══════════════════════════════════════════════════════════════════════════════╝

Features:
- High-Speed Parallel Downloads using concurrent.futures (8x faster in CI/CD)
- Exponential Backoff & Automatic Retry for network resilience
- Atomic File Repercussions & TSV Integrity Validation
- Comprehensive Date-Sorted Latest Feeds & Category Merging
- Rich GitHub Actions Dashboard Reporting ($GITHUB_STEP_SUMMARY)
"""

import os
import csv
import time
import urllib.request
import urllib.error
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Increase CSV field size limit for massive TSV entries
csv.field_size_limit(2**20)

# ── CONFIGURATION & DIRECTORIES ─────────────────────────────────────────────
BASE_URL = "https://nopaystation.com/tsv"
NPS_DIR = "resources/database/content/official/nopaystation"
OFFICIAL_DIR = "resources/database/content/official"
LATEST_DIR = "resources/database/content/latest"
PENDING_DIR = os.path.join(OFFICIAL_DIR, "pending")

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

# ── NETWORK & RETRY ENGINE ──────────────────────────────────────────────────
def download_file_with_retry(url, filepath, max_retries=3):
    """Download a file with exponential backoff and TSV integrity verification."""
    temp_path = filepath + ".tmp"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ArabicPlayStationNPS/2.0 (+https://github.com/KH-1010/EL-sueno-perdido)",
        "Accept": "text/tab-separated-values, text/plain, */*",
    }

    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=45) as resp:
                data = resp.read()
                
                # Check for empty or HTML error pages (e.g. Cloudflare 520 / 403)
                if len(data) < 20 or b"<html" in data[:100].lower():
                    raise ValueError("Received corrupt or HTML error content instead of TSV")
                
                with open(temp_path, "wb") as f:
                    f.write(data)
            
            # Verify TSV structure
            with open(temp_path, "r", encoding="utf-8", errors="replace") as f:
                first_line = f.readline()
                if not first_line.strip().startswith("Title ID"):
                    raise ValueError("Invalid TSV header format")
                
                lines_count = sum(1 for _ in f)
            
            # Atomic replace
            os.replace(temp_path, filepath)
            return True, lines_count
        except (urllib.error.URLError, urllib.error.HTTPError, ValueError, TimeoutError) as e:
            if os.path.exists(temp_path):
                try: os.remove(temp_path)
                except: pass
            
            if attempt < max_retries - 1:
                sleep_time = (1.8 ** attempt) * 1.5
                time.sleep(sleep_time)
            else:
                return False, str(e)
        except Exception as e:
            if os.path.exists(temp_path):
                try: os.remove(temp_path)
                except: pass
            return False, str(e)

def count_items(filepath):
    """Count data rows in a TSV file."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            count = 0
            for line in f:
                if line.strip() and not line.startswith("Title ID"):
                    count += 1
            return count
    except Exception:
        return 0

# ── MERGE & COMBINE ENGINE ──────────────────────────────────────────────────
def combine_tsv_files(source_files, output_path):
    """Combine multiple platform TSV files into unified category files."""
    total = 0
    with open(output_path, "w", encoding="utf-8") as out:
        out.write(HEADER + "\n")
        for fname in source_files:
            fpath = os.path.join(NPS_DIR, fname)
            if not os.path.exists(fpath):
                continue
            with open(fpath, "r", encoding="utf-8", errors="replace") as f:
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
    """Extract modification date for sorting latest releases."""
    items = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                if line.strip() and not line.startswith("Title ID"):
                    parts = line.split("\t")
                    date_str = parts[6] if len(parts) > 6 else ""
                    try:
                        dt = datetime.strptime(date_str.strip(), "%Y-%m-%d %H:%M:%S")
                    except Exception:
                        dt = datetime.min
                    items.append((dt, line))
    except Exception:
        pass
    return items

def create_latest_files():
    """Create latest_*.tsv files sorted chronologically."""
    combos = {
        "games": ["ps3_games.tsv", "psv_games.tsv", "psp_games.tsv", "psx_games.tsv", "psm_games.tsv"],
        "dlcs": ["ps3_dlcs.tsv", "psv_dlcs.tsv", "psp_dlcs.tsv"],
        "avatars": ["ps3_avatars.tsv"],
        "demos": ["ps3_demos.tsv", "psv_demos.tsv", "psp_demos.tsv"],
    }

    for cat, files in combos.items():
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
        print(f"    ↳ Created latest_{cat}.tsv with {len(all_items):,} sorted records")

# ── GITHUB ACTIONS DASHBOARD REPORTER ───────────────────────────────────────
def write_github_summary(results_map, category_totals):
    summary_file = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_file:
        return

    try:
        with open(summary_file, "a", encoding="utf-8") as f:
            f.write("### 🎮 NoPayStation Parallel Sync Summary\n\n")
            f.write("#### 📦 Unified Category Databases\n")
            f.write("| Category File | Total Records | Status |\n")
            f.write("| :--- | :---: | :---: |\n")
            for cat, count in category_totals.items():
                f.write(f"| **`{cat}`** | `{count:,}` | ✅ Ready |\n")
            
            f.write("\n#### ⚡ Individual TSV Download Results\n")
            f.write("| Platform File | Records Downloaded | Status |\n")
            f.write("| :--- | :---: | :---: |\n")
            for name in MAIN_FILES:
                local_name = FILENAME_MAP[name]
                status_obj = results_map.get(name, {"success": False, "msg": "Skipped"})
                if status_obj["success"]:
                    f.write(f"| **`{local_name}`** | `{status_obj['count']:,}` | ✓ Downloaded |\n")
                else:
                    f.write(f"| **`{local_name}`** | `-` | ⚠️ Retained Local (`{status_obj['msg']}`) |\n")
            
            f.write(f"\n*Completed at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}*\n")
    except Exception as e:
        print(f"  [Warning] Could not write GitHub summary: {e}")

# ── MAIN EXECUTION ──────────────────────────────────────────────────────────
def main():
    os.makedirs(NPS_DIR, exist_ok=True)
    os.makedirs(OFFICIAL_DIR, exist_ok=True)
    os.makedirs(LATEST_DIR, exist_ok=True)
    os.makedirs(PENDING_DIR, exist_ok=True)

    print("╔══════════════════════════════════════════════════════════════════════════╗")
    print("║  ⚡ NoPayStation High-Speed Parallel Synchronizer v2.0                   ║")
    print("╚══════════════════════════════════════════════════════════════════════════╝\n")

    start_time = time.time()
    results_map = {}

    # Helper function for worker threads
    def fetch_task(name, is_pending=False):
        sub_dir = PENDING_DIR if is_pending else NPS_DIR
        url_prefix = f"{BASE_URL}/pending" if is_pending else BASE_URL
        url = f"{url_prefix}/{name}.tsv"
        local_name = FILENAME_MAP[name]
        filepath = os.path.join(sub_dir, local_name)
        
        success, res = download_file_with_retry(url, filepath)
        return name, is_pending, success, res, filepath

    print("🚀 [Step 1/4] Launching High-Speed Parallel Downloads (Main & Pending TSVs)...")
    
    tasks = []
    with ThreadPoolExecutor(max_workers=8) as executor:
        for name in MAIN_FILES:
            tasks.append(executor.submit(fetch_task, name, False))
        for name in PENDING_FILES:
            tasks.append(executor.submit(fetch_task, name, True))
        
        for future in as_completed(tasks):
            name, is_pending, success, res, filepath = future.result()
            label = f"[{'PENDING' if is_pending else 'MAIN'}] {FILENAME_MAP[name]}"
            if success:
                print(f"   ✓ {label:<25} ──> {res:,} items synced")
                if not is_pending:
                    results_map[name] = {"success": True, "count": res}
            else:
                existing_count = count_items(filepath) if os.path.exists(filepath) else 0
                print(f"   ⚠️ {label:<25} ──> Download failed ({res}). Retained local ({existing_count:,} items)")
                if not is_pending:
                    results_map[name] = {"success": False, "msg": str(res)[:30], "count": existing_count}

    print("\n📦 [Step 2/4] Combining Platform TSVs into Unified Official Databases...")
    category_totals = {}
    for out_name, sources in CATEGORY_COMBOS.items():
        output = os.path.join(OFFICIAL_DIR, out_name)
        total = combine_tsv_files(sources, output)
        category_totals[out_name] = total
        print(f"   ✓ Unified {out_name:<20} ──> {total:,} total records")

    # Build empty fallback stubs
    for cat in ["prototypes.tsv", "tools.tsv"]:
        output = os.path.join(OFFICIAL_DIR, cat)
        if not os.path.exists(output):
            with open(output, "w", encoding="utf-8") as f:
                f.write(HEADER + "\n")

    print("\n🕒 [Step 3/4] Generating Chronological Latest Feeds...")
    create_latest_files()

    elapsed = time.time() - start_time
    print("\n📊 [Step 4/4] Execution Summary & Dashboard Summary...")
    print("━" * 74)
    total_games = category_totals.get("games.tsv", 0)
    total_dlcs = category_totals.get("dlcs.tsv", 0)
    total_themes = category_totals.get("themes.tsv", 0)
    total_avatars = category_totals.get("avatars.tsv", 0)
    print(f"✅ Synchronization complete in {elapsed:.2f} seconds!")
    print(f"🏆 Total Library Footprint: {total_games:,} Games | {total_dlcs:,} DLCs | {total_themes:,} Themes | {total_avatars:,} Avatars")
    print("━" * 74)

    write_github_summary(results_map, category_totals)

if __name__ == "__main__":
    main()
