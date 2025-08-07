import os
import stat
import platform
import getpass

def checkPermissions(path):
    if not os.path.exists(path):
        print(f"Path does not exist: {path}")
        return

    system = platform.system()
    currentUser = getpass.getuser()

    print(f"\nChecking permissions for: {path}")
    print(f"Current user: {currentUser}")
    print(f"Operating system: {system}")

    isReadable = os.access(path, os.R_OK)
    isWritable = os.access(path, os.W_OK)
    isExecutable = os.access(path, os.X_OK)

    print(f"Readable: {'yes' if isReadable else 'no'}")
    print(f"Writable: {'yes' if isWritable else 'no'}")
    print(f"Executable: {'yes' if isExecutable else 'no'}")

    info = os.stat(path)

    if system != "Windows":
        print(f"User ID: {info.st_uid}, Group ID: {info.st_gid}")
        print(f"Permission bits: {oct(info.st_mode)}")

        print("Detailed permissions:")
        print("  Owner:  " +
              ('r' if info.st_mode & stat.S_IRUSR else '-') +
              ('w' if info.st_mode & stat.S_IWUSR else '-') +
              ('x' if info.st_mode & stat.S_IXUSR else '-'))
        print("  Group:  " +
              ('r' if info.st_mode & stat.S_IRGRP else '-') +
              ('w' if info.st_mode & stat.S_IWGRP else '-') +
              ('x' if info.st_mode & stat.S_IXGRP else '-'))
        print("  Others: " +
              ('r' if info.st_mode & stat.S_IROTH else '-') +
              ('w' if info.st_mode & stat.S_IWOTH else '-') +
              ('x' if info.st_mode & stat.S_IXOTH else '-'))
    else:
        print("Windows does not provide POSIX-style permission bits.")
        print("Use 'icacls' or 'Get-Acl' in PowerShell for detailed access control.")

if __name__ == "__main__":
    path = input("Enter the path to check: ").strip()
    checkPermissions(path)
