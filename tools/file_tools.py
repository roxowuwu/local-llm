from pathlib import Path
import shutil
import time
import os


BACKUP_DIR = "backups"


# -----------------------------
# READ FILE
# -----------------------------
def read_file(params, prefs):
    path = params.get("path")

    if not path:
        raise ValueError("No file path provided")

    file_path = Path(path)

    if not file_path.exists() or not file_path.is_file():
        raise ValueError(f"File not found: {path}")

    try:
        content = file_path.read_text(errors="ignore")
        content = content[:10000]  # limit size

        print(f"[LOG] Read file: {file_path}")

        return content

    except Exception as e:
        raise ValueError(f"Failed to read file: {e}")


# -----------------------------
# WRITE FILE (SAFE)
# -----------------------------
def write_file(params, prefs):
    path = params.get("path")
    content = params.get("content")

    if not path or content is None:
        raise ValueError("Path or content missing")

    file_path = Path(path)
    temp_path = file_path.with_suffix(".tmp")

    os.makedirs(BACKUP_DIR, exist_ok=True)

    # 1. backup if exists
    if file_path.exists():
        timestamp = int(time.time())
        backup_path = Path(BACKUP_DIR) / f"{file_path.name}.{timestamp}.bak"
        shutil.copy(file_path, backup_path)
    else:
        backup_path = None

    # 2. write temp file
    try:
        temp_path.write_text(content)
    except Exception as e:
        raise ValueError(f"Temp write failed: {e}")

    # 3. verify temp file
    if not temp_path.exists():
        raise ValueError("Temp file not created")

    # 4. replace original
    try:
        temp_path.replace(file_path)
    except Exception as e:
        raise ValueError(f"Replace failed: {e}")

    if backup_path:
        return f"Written: {path} (backup saved)"
    else:
        return f"Written: {path}"


# -----------------------------
# FIND FILE
# -----------------------------
def find_file(params, prefs):
    query = params.get("query")
    folder = params.get("folder") or str(Path.home())

    if not query:
        raise ValueError("No search query provided")

    base_path = Path(folder)

    if not base_path.exists():
        raise ValueError(f"Folder not found: {folder}")

    matches = []

    try:
        for file in base_path.rglob("*"):
            if query.lower() in file.name.lower():
                matches.append(str(file))

            if len(matches) >= 20:
                break

    except Exception as e:
        raise ValueError(f"Search failed: {e}")

    print("\nFound files:\n")
    for m in matches:
        print(m)

    return f"Found {len(matches)} files matching: {query}"
