import os
import json
import typer
from pathlib import Path
from rapidfuzz import fuzz
from typing import Optional

app = typer.Typer()
DB_PATH = Path.home() / ".zoi.json"

def load_db():
    if DB_PATH.exists():
        with open(DB_PATH, "r") as f:
            return json.load(f)
    return {}

def save_db(data):
    with open(DB_PATH, "w") as f:
        json.dump(data, f, indent=4)

def add_path(path: str):
    data = load_db()
    if path in data:
        data[path] += 1
    else:
        data[path] = 1
    save_db(data)

def best_match(keyword: str) -> Optional[str]:
    data = load_db()
    if not data:
        return None
    scored = []
    for path, freq in data.items():
        score = fuzz.partial_ratio(keyword.lower(), path.lower()) + freq
        scored.append((score, path))
    scored.sort(reverse=True)
    return scored[0][1] if scored else None

@app.command()
def add(path: str = typer.Argument(..., help="Directory to track")):
    abs_path = os.path.abspath(path)
    if os.path.isdir(abs_path):
        add_path(abs_path)
        typer.echo(f"Added: {abs_path}")
    else:
        typer.echo("Not a valid directory.")

@app.command()
def jump(keyword: str = typer.Argument(..., help="Keyword to search")):
    match = best_match(keyword)
    if match:
        typer.echo(match)
    else:
        typer.echo("")

@app.command()
def list():
    data = load_db()
    if not data:
        typer.echo("No directories tracked yet.")
        return
    sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)
    for path, freq in sorted_data:
        typer.echo(f"{freq:3}  {path}")

if __name__ == "__main__":
    app()
