import subprocess
import os
from pathlib import Path
from collections import defaultdict
import hashlib


# -----------------------------
# STORAGE REPORT
# -----------------------------
def storage_report(params, prefs):
    try:
        df_output = subprocess.check_output(["df", "-h"]).decode()
        du_output = subprocess.check_output(["du", "-sh", str(Path.home())]).decode()

        print("\nDisk Usage:\n")
        print(df_output)

        print("\nHome Directory Size:\n")
        print(du_output)

        # basic warning detection
        for line in df_output.splitlines()[1:]:
            parts = line.split()
            if len(parts) >= 5:
                usage = parts[4]
                if usage.endswith("%"):
                    percent = int(usage[:-1])
                    if percent > 85:
                        print("⚠️ Warning: Disk usage above 85%")

        return "Storage report displayed"

    except Exception as e:
        return f"Failed to get storage report: {e}"


# -----------------------------
# FIND LARGE FILES
# -----------------------------
def find_large_files(params, prefs):
    folder = params.get("folder") or prefs.get("home_dir") or str(Path.home())
    threshold_mb = params.get("threshold", 100)

    threshold_bytes = int(threshold_mb) * 1024 * 1024
    base_path = Path(folder)

    if not base_path.exists():
        raise ValueError(f"Folder not found: {folder}")

    results = []

    for file in base_path.rglob("*"):
        if file.is_file():
            try:
                size = file.stat().st_size
                if size >= threshold_bytes:
                    results.append((str(file), size))
            except:
                continue

    results.sort(key=lambda x: x[1], reverse=True)

    print("\nLarge Files:\n")
    for path, size in results[:20]:
        print(f"{path} - {round(size / (1024*1024), 2)} MB")

    return f"Found {len(results)} files above {threshold_mb} MB"


# -----------------------------
# FIND DUPLICATE FILES
# -----------------------------
def find_duplicate_files(params, prefs):
    folder = params.get("folder") or prefs.get("home_dir") or str(Path.home())
    base_path = Path(folder)

    if not base_path.exists():
        raise ValueError(f"Folder not found: {folder}")

    size_map = defaultdict(list)

    # Step 1: group by size
    for file in base_path.rglob("*"):
        if file.is_file():
            try:
                size = file.stat().st_size
                size_map[size].append(file)
            except:
                continue

    hash_map = defaultdict(list)

    # Step 2: hash files with same size
    for size, files in size_map.items():
        if len(files) < 2:
            continue

        for file in files:
            try:
                file_hash = _hash_file(file)
                hash_map[file_hash].append(file)
            except:
                continue

    duplicate_groups = []
    reclaimable = 0

    # Step 3: collect duplicates
    for files in hash_map.values():
        if len(files) > 1:
            duplicate_groups.append(files)

            # calculate reclaimable space (all except one)
            size = files[0].stat().st_size
            reclaimable += size * (len(files) - 1)

    # print results
    print("\nDuplicate Files:\n")
    for group in duplicate_groups:
        print("----")
        for f in group:
            print(f)

    print(f"\nReclaimable space: {round(reclaimable / (1024*1024), 2)} MB")

    return f"Found {len(duplicate_groups)} duplicate groups, {round(reclaimable / (1024*1024), 2)} MB reclaimable"


# -----------------------------
# HASH HELPER
# -----------------------------
def _hash_file(path):
    hasher = hashlib.md5()

    with open(path, "rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)

    return hasher.hexdigest()
