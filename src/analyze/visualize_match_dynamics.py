#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

TABLE_DIR = os.path.expanduser("~/football_project/results/tables")
FIG_DIR = os.path.expanduser("~/football_project/results/figures")

SEASON_FILE = os.path.join(TABLE_DIR, "season_summary.csv")
PERIOD_FILE = os.path.join(TABLE_DIR, "period_summary.csv")

def read_csv(path):
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def to_float(x):
    try:
        return float(x)
    except:
        return 0.0

def save_line_chart(rows, y_col, title, ylabel, filename):
    seasons = [r["season"] for r in rows]
    values = [to_float(r[y_col]) for r in rows]

    plt.figure(figsize=(12, 6))
    plt.plot(seasons, values, marker="o")
    plt.title(title)
    plt.xlabel("Season")
    plt.ylabel(ylabel)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    out_path = os.path.join(FIG_DIR, filename)
    plt.savefig(out_path, dpi=150)
    plt.close()
    print("[OK]", out_path)

def save_period_bar(rows, y_col, title, ylabel, filename):
    groups = [r["period_group"] for r in rows]
    values = [to_float(r[y_col]) for r in rows]

    plt.figure(figsize=(7, 5))
    plt.bar(groups, values)
    plt.title(title)
    plt.xlabel("Period")
    plt.ylabel(ylabel)
    plt.tight_layout()

    out_path = os.path.join(FIG_DIR, filename)
    plt.savefig(out_path, dpi=150)
    plt.close()
    print("[OK]", out_path)

def main():
    os.makedirs(FIG_DIR, exist_ok=True)

    season_rows = read_csv(SEASON_FILE)
    period_rows = read_csv(PERIOD_FILE)

    save_line_chart(
        season_rows,
        "avg_goals",
        "Average Goals per Match by Season",
        "Average Goals",
        "season_avg_goals.png"
    )

    save_line_chart(
        season_rows,
        "avg_shots",
        "Average Shots per Match by Season",
        "Average Shots",
        "season_avg_shots.png"
    )

    save_line_chart(
        season_rows,
        "avg_shot_conversion",
        "Shot Conversion Rate by Season",
        "Goals / Shots",
        "season_shot_conversion.png"
    )

    save_line_chart(
        season_rows,
        "low_score_2_rate",
        "Low-scoring Match Rate by Season",
        "Rate of Matches with 2 or Fewer Goals",
        "season_low_score_2_rate.png"
    )

    save_line_chart(
        season_rows,
        "home_win_rate",
        "Home Win Rate by Season",
        "Home Win Rate",
        "season_home_win_rate.png"
    )

    save_period_bar(
        period_rows,
        "avg_goals",
        "Average Goals: 2008-2016 vs 2016-2025",
        "Average Goals",
        "period_avg_goals.png"
    )

    save_period_bar(
        period_rows,
        "avg_shots",
        "Average Shots: 2008-2016 vs 2016-2025",
        "Average Shots",
        "period_avg_shots.png"
    )

    save_period_bar(
        period_rows,
        "low_score_2_rate",
        "Low-scoring Match Rate: 2008-2016 vs 2016-2025",
        "Rate",
        "period_low_score_2_rate.png"
    )

    print("[DONE] figures generated.")

if __name__ == "__main__":
    main()
