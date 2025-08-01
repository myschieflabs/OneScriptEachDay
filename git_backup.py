#!/usr/bin/env python3

import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
import argparse
import getpass
import platform

def getDefaultRepo():
    user = getpass.getuser()
    return Path(f"C:/Users/{user}/.backup") if isWindows() else Path.home() / ".backup"

def isWindows():
    return platform.system().lower() == "windows"

def pickFiles(dirPath):
    if isWindows():
        cmd = f'powershell -Command "Get-ChildItem -Path \'{dirPath}\' -Recurse -File | ForEach-Object {{$_.FullName}}" | fzf --multi"'
    else:
        cmd = f"find '{dirPath}' -type f | fzf --multi"

    res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, text=True)
    return [Path(f.strip()) for f in res.stdout.strip().split('\n') if f.strip()]

def moveStuff(files, fromDir, toDir, overwrite=False):
    for f in files:
        try:
            rel = f.relative_to(fromDir)
        except ValueError:
            print(f"skip (outside source): {f}")
            continue

        dest = toDir / rel
        if dest.exists() and not overwrite:
            print(f"skip: {dest}")
            continue

        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(f), str(dest))
        print(f"{f} -> {dest}")

def initGitRepo(repoDir):
    if not (repoDir / ".git").exists():
        subprocess.run("git init", cwd=repoDir, shell=True)
        subprocess.run("git branch -M main", cwd=repoDir, shell=True)
        print("git repo created")
    else:
        print("git repo already exists")

def hasRemote(repoDir):
    try:
        res = subprocess.run("git remote", cwd=repoDir, shell=True, stdout=subprocess.PIPE, text=True)
        return "origin" in res.stdout.strip().splitlines()
    except:
        return False

def commitAndPush(repoDir, msg=None):
    subprocess.run("git add .", cwd=repoDir, shell=True)
    finalMsg = msg or f"backup: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    subprocess.run(f"git commit -m \"{finalMsg}\"", cwd=repoDir, shell=True)

    if hasRemote(repoDir):
        subprocess.run("git push origin main", cwd=repoDir, shell=True)
        print("pushed to origin")
    else:
        print("no remote set, skipped push")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("src", type=Path, help="folder to pick files from")
    p.add_argument("-r", "--repo", type=Path, default=getDefaultRepo(), help="backup git repo (default: ~/.backup)")
    p.add_argument("-m", "--msg", type=str, help="commit message")
    p.add_argument("--overwrite", action="store_true", help="overwrite existing files in repo")
    args = p.parse_args()

    if not args.src.is_dir():
        print(f"invalid source: {args.src}")
        return

    if not args.repo.exists():
        args.repo.mkdir(parents=True)
        print(f"created repo directory: {args.repo}")

    initGitRepo(args.repo)

    files = pickFiles(args.src)
    if not files:
        print("no files selected")
        return

    moveStuff(files, args.src, args.repo, args.overwrite)
    commitAndPush(args.repo, args.msg)
    print("done")

if __name__ == "__main__":
    main()
