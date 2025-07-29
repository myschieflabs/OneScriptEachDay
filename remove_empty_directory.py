import os
import argparse

def deleteEmptyFolders(rootDir):
    emptyFolders = []
    for dirPath, dirNames, _ in os.walk(rootDir, topdown=False):
        for dirName in dirNames:
            fullPath = os.path.join(dirPath, dirName)
            try:
                if not os.listdir(fullPath):
                    emptyFolders.append(fullPath)
            except FileNotFoundError:
                continue

    if not emptyFolders:
        print("No empty folders found.")
        return

    print("The following empty folders will be deleted:")
    for folder in emptyFolders:
        print(f"  - {folder}")

    confirm = input("Are you sure you want to delete these folders? Type 'yes' to confirm: ").strip().lower()
    if confirm == "yes":
        deletedCount = 0
        for folder in emptyFolders:
            try:
                os.rmdir(folder)
                deletedCount += 1
            except OSError:
                print(f"Failed to delete: {folder}")
        print(f"Deleted {deletedCount} empty folder(s).")
    else:
        print("Operation cancelled. No folders were deleted.")

def main():
    parser = argparse.ArgumentParser(description="Delete all empty folders in the specified directory tree, with confirmation.")
    parser.add_argument("directory", nargs="?", default=".", help="Root directory to search (default: current directory)")
    args = parser.parse_args()
    deleteEmptyFolders(args.directory)

if __name__ == "__main__":
    main()
