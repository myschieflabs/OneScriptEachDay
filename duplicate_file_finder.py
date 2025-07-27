import os
import hashlib
from collections import defaultdict
from datetime import datetime

def getMeta(path):
    try:
        stat = os.stat(path)
        return {
            "size": stat.st_size,
            "mtime": stat.st_mtime
        }
    except Exception as e:
        print(f"Error accessing {path}: {e}")
        return None

def hashFiles(path, chunk_size=65536):
    sha = hashlib.sha256()
    try:
        with open(path, 'rb') as f:
            while chunk := f.read(chunk_size):
                sha.update(chunk)
        return sha.hexdigest()
    except Exception as e:
        print(f"Error hashing {path}: {e}")
        return None

def findDupes(directory, use_hash=False):
    files_by_metadata = defaultdict(list)

    for root, _, files in os.walk(directory):
        for file in files:
            full_path = os.path.join(root, file)
            metadata = getMeta(full_path)
            if not metadata:
                continue

            key = (metadata['size'], metadata['mtime'])

            if use_hash:
                file_hash = hashFiles(full_path)
                if not file_hash:
                    continue
                key += (file_hash,)

            files_by_metadata[key].append(full_path)

    duplicates = {k: v for k, v in files_by_metadata.items() if len(v) > 1}
    return duplicates

def giveDupes(duplicates):
    if not duplicates:
        print("No duplicates found.")
        return

    print("Duplicate Files Found:\n")
    for idx, (meta, files) in enumerate(duplicates.items(), 1):
        print(f"[{idx}] Metadata: {meta}")
        for f in files:
            print(f"   - {f}")
        print()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Find duplicate files based on metadata and optional content hash.")
    parser.add_argument("directory", help="Directory to search for duplicates")
    parser.add_argument("--use-hash", action="store_true", help="Also compare SHA256 file content")

    args = parser.parse_args()

    dupes = find_duplicates(args.directory, use_hash=args.use_hash)
    print_duplicates(dupes)