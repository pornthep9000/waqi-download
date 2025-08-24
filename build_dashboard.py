#!/usr/bin/env python3
import os, glob, pandas as pd

DATA_DIR = "data"
DOC_PATH = "docs/index.html"

def find_latest_csv():
    files = sorted(glob.glob(os.path.join(DATA_DIR, "waqi_*.csv")))
    return files[-1] if files else None

def main():
    latest = find_latest_csv()
    os.makedirs("docs", exist_ok=True)
    if latest is None:
        with open(DOC_PATH, "w", encoding="utf-8") as f:
            f.write("<html><body><h2>No data yet</h2></body></html>")
        return
    with open(DOC_PATH, "w", encoding="utf-8") as f:
        f.write(f"<html><body><h2>Latest CSV: {latest}</h2><p><a href='../{latest}'>Download</a></p></body></html>")

if __name__ == "__main__":
    main()
