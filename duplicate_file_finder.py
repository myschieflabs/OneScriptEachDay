import os, argparse
from collections import defaultdict

def getMeta(path):
    try: return os.stat(path).st_size, os.stat(path).st_mtime
    except: return None

def findDupes(dir):
    files = defaultdict(list)
    for root, _, names in os.walk(dir):
        for name in names:
            path = os.path.join(root, name)
            meta = getMeta(path)
            if meta: files[meta].append(path)
    return {k: v for k, v in files.items() if len(v) > 1}

def giveDupes(dupes):
    if not dupes: return print("No duplicates found.")
    print("Duplicate Files Found:\n")
    for i, (meta, paths) in enumerate(dupes.items(), 1):
        print(f"[{i}] Metadata: {meta}")
        for p in paths: print(f"   - {p}")
        print()

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("directory")
    args = p.parse_args()
    giveDupes(findDupes(args.directory))
