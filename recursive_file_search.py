import subprocess
import argparse
from pathlib import Path
import sys
import os
import shutil


IGNORED_DIRS = {'.git', '__pycache__', 'node_modules', 'build', 'dist'}

def getFileList(rootDir, extension=None):
    files = []
    for path in Path(rootDir).rglob('*'):
        if not path.is_file():
            continue
        if any(ignored in path.parts for ignored in IGNORED_DIRS):
            continue
        if extension and not path.name.endswith(extension):
            continue
        files.append(str(path))
    return files

def getPreviewCommand():
    if shutil.which("bat"):
        return "bat --style=plain --color=always {}"
    elif os.name == 'nt':
        return "type {}"
    else:
        return "head -n 30 {}"

def selectWithFzf(fileList, allowMulti=False, enablePreview=False):
    try:
        fzfCmd = ['fzf']
        if allowMulti:
            fzfCmd.append('--multi')
        if enablePreview:
            fzfCmd += ['--preview', getPreviewCommand()]

        result = subprocess.run(
            fzfCmd,
            input='\n'.join(fileList),
            text=True,
            stdout=subprocess.PIPE
        )

        if result.returncode == 0:
            output = result.stdout.strip()
            return output.split('\n') if allowMulti else output
        return None
    except FileNotFoundError:
        print("fzf not found. Please install it and ensure it's in PATH.")
        return None

def openFiles(filePaths, editor):
    if not filePaths:
        return
    if isinstance(filePaths, str):
        filePaths = [filePaths]
    subprocess.run([editor] + filePaths)

def main():
    parser = argparse.ArgumentParser(description="Enhanced fuzzy file finder")
    parser.add_argument('directory', nargs='?', default='.', help='Directory to search')
    parser.add_argument('--multi', action='store_true', help='Enable multiple selection')
    parser.add_argument('--ext', type=str, help='Filter by extension')
    parser.add_argument('--preview', action='store_true', help='Show file preview in fzf')
    parser.add_argument('--open', action='store_true', help='Open selected files in default editor')
    parser.add_argument('--editor', type=str, default='code', help='Editor to open files with')

    args = parser.parse_args()
    fileList = getFileList(args.directory, args.ext)

    if not fileList:
        print("No matching files found.")
        sys.exit(1)

    selection = selectWithFzf(fileList, allowMulti=args.multi, enablePreview=args.preview)

    if selection:
        print("Selected file(s):")
        print(selection if isinstance(selection, str) else '\n'.join(selection))
        if args.open:
            openFiles(selection, args.editor)

if __name__ == '__main__':
    main()
