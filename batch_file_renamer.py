import os
import sys
import subprocess

def runFzf(files):
    if not files:
        print("No files to select.")
        return []
    try:
        out = subprocess.run(['fzf', '-m'], input="\n".join(files), text=True, capture_output=True, check=True)
        return [f for f in out.stdout.strip().split('\n') if f]
    except FileNotFoundError:
        sys.exit(1)
    except subprocess.CalledProcessError:
        print("No files selected or aborted.")
    return []

def getFiles(path='.'):
    try:
        return [f for f in os.listdir(path) if os.path.isfile(f)]
    except Exception as e:
        print(f"Error: {e}")
        return []

def interactiveRename(files):
    renames = []
    for f in files:
        newName = input(f"Rename '{f}' to (Enter to skip): ").strip()
        if not newName:
            print(f"Skipping '{f}'")
            continue
        if os.path.exists(newName) and newName != f:
            print(f"'{newName}' exists. Skipping.")
            continue
        renames.append((f, newName))
    return renames

def patternRename(files):
    find = input("Find: ")
    replace = input("Replace with: ")
    if not find:
        print("Find string can't be empty.")
        return []

    renames = []
    for f in files:
        newName = f.replace(find, replace)
        if newName == f:
            print(f"No change for '{f}'")
            continue
        if os.path.exists(newName) and newName != f:
            print(f"'{newName}' exists. Skipping.")
            continue
        renames.append((f, newName))
    return renames

def confirmAndRename(renames):
    if not renames:
        print("Nothing to rename.")
        return
    print("\n--- Preview ---")
    for old, new in renames:
        print(f"{old} -> {new}")
    if input("\nProceed? (yes/no): ").strip().lower() == 'yes':
        for old, new in renames:
            try:
                os.rename(old, new)
                print(f"Renamed: {old} -> {new}")
            except Exception as e:
                print(f"Error renaming {old}: {e}")
    else:
        print("Cancelled.")

def main():
    files = getFiles()
    if not files:
        print("No files found.")
        return

    print("Use Tab to select files, Enter to confirm.")
    selected = runFzf(files)
    if not selected:
        return

    print(f"\nSelected {len(selected)} file(s):")
    for f in selected:
        print("-", f)

    mode = ''
    while mode not in ['interactive', 'pattern', 'cancel']:
        mode = input("\nMode? (interactive/pattern/cancel): ").strip().lower()
    if mode == 'cancel':
        print("Cancelled.")
        return

    renames = interactiveRename(selected) if mode == 'interactive' else patternRename(selected)
    confirmAndRename(renames)

if __name__ == "__main__":
    main()
