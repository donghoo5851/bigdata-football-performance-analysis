#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PROJECT_HOME = os.path.expanduser("~/football_project")
TABLE_FILE = os.path.join(PROJECT_HOME, "results/tables/event_season_summary.csv")
FIG_DIR = os.path.join(PROJECT_HOME, "results/figures")
OUT_FILE = os.path.join(FIG_DIR, "event_season_metrics_trend.png")

def to_float(x):
    try:
        return float(x)
    except:
        return None

def read_rows():
    rows = []
    with open(TABLE_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows

def main():
    os.makedirs(FIG_DIR, exist_ok=True)
    rows = read_rows()

    seasons = [r["season"] for r in rows]
    events = [to_float(r["events_per_match"]) for r in rows]
    attempts = [to_float(r["attempts_per_match"]) for r in rows]
    key_passes = [to_float(r["key_passes_per_match"]) for r in rows]
    fouls = [to_float(r["fouls_per_match"]) for r in rows]

    plt.figure(figsize=(12, 6))
    plt.plot(seasons, events, marker="o", linewidth=2, label="Events per match")
    plt.plot(seasons, attempts, marker="s", linewidth=2, label="Attempts per match")
    plt.plot(seasons, key_passes, marker="^", linewidth=2, label="Key passes per match")
    plt.plot(seasons, fouls, marker="D", linewidth=2, label="Fouls per match")

    plt.title("Football-events: event composition by season")
    plt.xlabel("Season")
    plt.ylabel("Per-match count")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUT_FILE, dpi=180)
    plt.close()

    print("[OK]", OUT_FILE)

if __name__ == "__main__":
    main()
