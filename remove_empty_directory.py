import os
import argparse

def delete_empty_folders(root):
    deleted = []
    for dirpath, dirnames, filenames in os.walk(root, topdown=False):
        for dirname in dirnames:
            full_path = os.path.join(dirpath, dirname)
            if not os.listdir(full_path):
                deleted.append(full_path)
    if not deleted:
        print("No empty folders found.")
        return

    print("The following empty folders will be deleted:")
    for d in deleted:
        print("  -", d)
    confirm = input("Are you sure you want to delete these folders? Type 'yes' to confirm: ")
    if confirm.lower() == "yes":
        for d in deleted:
            os.rmdir(d)
        print(f"Deleted {len(deleted)} empty folder(s).")
    else:
        print("Operation cancelled. No folders were deleted.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Remove all empty folders in the specified directory tree, with confirmation.")
    parser.add_argument("directory", nargs="?", default=".", help="Root directory (default: current directory)")
    args = parser.parse_args()
    delete_empty_folders(args.directory)
