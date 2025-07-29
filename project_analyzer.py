import os
import sys
import argparse
from collections import defaultdict

LANGUAGE_MAP = {
    '.py':  ('Python', '#'),
    '.js':  ('JavaScript', '//'),
    '.jsx': ('React JSX', '//'),
    '.ts':  ('TypeScript', '//'),
    '.tsx': ('React TSX', '//'),
    '.java': ('Java', '//'),
    '.kt':  ('Kotlin', '//'),
    '.c':   ('C', '//'),
    '.cpp': ('C++', '//'),
    '.h':   ('C/C++ Header', '//'),
    '.go':  ('Go', '//'),
    '.rs':  ('Rust', '//'),
    '.dart': ('Flutter (Dart)', '//'),
    '.html': ('HTML', '<!--'),
    '.css':  ('CSS', '/*'),
    '.sh':   ('Shell', '#'),
    '.bash': ('Shell', '#'),
    '.zsh':  ('Shell', '#'),
    '.xml':  ('Android XML', '<!--'),
    '.bashrc': ('Shell Config', '#'),
    '.zshrc':  ('Shell Config', '#'),
    '.profile': ('Shell Config', '#'),
}

DEFAULT_EXCLUDE = {
    'node_modules', '.git', 'build', 'dist',
    '.dart_tool', '.idea', '.vscode', '__pycache__', 'out'
}

class Stats:
    def __init__(self):
        self.files = 0
        self.code = 0
        self.comments = 0
        self.blanks = 0

    def __iadd__(self, other):
        self.files += other.files
        self.code += other.code
        self.comments += other.comments
        self.blanks += other.blanks
        return self

def analyze_file(filepath, comment_token):
    stats = Stats()
    stats.files = 1
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if not line:
                    stats.blanks += 1
                elif line.startswith(comment_token):
                    stats.comments += 1
                else:
                    stats.code += 1
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
    return stats

def analyze_directory(path, exclude):
    total = defaultdict(Stats)
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in exclude]
        for file in files:
            ext = os.path.splitext(file)[1]
            if not ext and file in LANGUAGE_MAP:
                lang, comment_token = LANGUAGE_MAP[file]
            elif ext in LANGUAGE_MAP:
                lang, comment_token = LANGUAGE_MAP[ext]
            else:
                continue
            filepath = os.path.join(root, file)
            stats = analyze_file(filepath, comment_token)
            total[lang] += stats
    return total

def print_summary(results):
    print("\nLanguage Summary:")
    print("-" * 60)
    print(f"{'Language':<20} {'Files':>6} {'Code':>8} {'Comments':>10} {'Blanks':>8}")
    print("-" * 60)

    total_files = 0
    total_code = 0
    total_comments = 0
    total_blanks = 0
    most_used_lang = None
    max_code = 0

    for lang, stat in sorted(results.items()):
        print(f"{lang:<20} {stat.files:>6} {stat.code:>8} {stat.comments:>10} {stat.blanks:>8}")
        total_files += stat.files
        total_code += stat.code
        total_comments += stat.comments
        total_blanks += stat.blanks
        if stat.code > max_code:
            max_code = stat.code
            most_used_lang = lang

    total_lines = total_code + total_comments + total_blanks
    avg_loc_per_file = (total_code / total_files) if total_files else 0

    print("-" * 60)
    print(f"{'TOTAL':<20} {total_files:>6} {total_code:>8} {total_comments:>10} {total_blanks:>8}")
    print("-" * 60)

    print("\n > Additional Stats:")
    print(f" > Total lines (code + comments + blanks): {total_lines}")
    print(f" > Average LOC per file: {avg_loc_per_file:.2f}")
    print(f" > Most used language: {most_used_lang or 'N/A'} ({max_code} LOC)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tokei-style project analyzer in Python")
    parser.add_argument("path", nargs="?", default=".", help="Path to the project root")
    parser.add_argument("--exclude", nargs="*", help="Directories to exclude (space-separated)")
    args = parser.parse_args()
    project_path = os.path.abspath(args.path)
    user_exclude = set(args.exclude) if args.exclude else set()
    all_exclude = DEFAULT_EXCLUDE.union(user_exclude)
    print(f" > Analyzing: {project_path}")
    print(f" > Excluding: {', '.join(sorted(all_exclude))}")
    print("\n")
    results = analyze_directory(project_path, all_exclude)
    print_summary(results)
