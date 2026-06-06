#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PROJECT_HOME = os.path.expanduser("~/football_project")
TABLE_FILE = os.path.join(PROJECT_HOME, "results/tables/understat_xg_shot_quality_summary.csv")
FIG_DIR = os.path.join(PROJECT_HOME, "results/figures")

def to_float(x):
    try:
        return float(x)
    except:
        return 0.0

def read_rows():
    with open(TABLE_FILE, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    rows.sort(key=lambda r: r["season_code"])
    return rows

def plot_xg_quality(rows):
    seasons = [r["season"] for r in rows]
    xg_per_shot = [to_float(r["xg_per_shot_proxy"]) for r in rows]
    avg_xg = [to_float(r["avg_xg_for_per_team_match"]) for r in rows]
    avg_goals = [to_float(r["avg_goals_for_per_team_match"]) for r in rows]

    # Indexing makes different-scale metrics comparable.
    base_xg_per_shot = xg_per_shot[0]
    base_avg_xg = avg_xg[0]
    base_avg_goals = avg_goals[0]

    xg_per_shot_idx = [v / base_xg_per_shot * 100 for v in xg_per_shot]
    avg_xg_idx = [v / base_avg_xg * 100 for v in avg_xg]
    avg_goals_idx = [v / base_avg_goals * 100 for v in avg_goals]

    plt.figure(figsize=(12, 6))
    plt.plot(seasons, xg_per_shot_idx, marker="o", linewidth=2, label="xG per shot proxy")
    plt.plot(seasons, avg_xg_idx, marker="s", linewidth=2, label="xG per team-match")
    plt.plot(seasons, avg_goals_idx, marker="^", linewidth=2, label="Goals per team-match")

    plt.axhline(100, linestyle="--", linewidth=1)
    plt.title("Understat xG-based attacking quality trend")
    plt.xlabel("Season")
    plt.ylabel("Index value, 2014/15 = 100")
    plt.xticks(rotation=45, ha="right")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    out = os.path.join(FIG_DIR, "understat_xg_shot_quality_trend.png")
    plt.savefig(out, dpi=180)
    plt.close()
    print("[OK]", out)

def plot_deep_ppda(rows):
    seasons = [r["season"] for r in rows]
    deep = [to_float(r["avg_deep"]) for r in rows]
    ppda = [to_float(r["avg_ppda"]) for r in rows]

    fig, ax1 = plt.subplots(figsize=(12, 6))

    ax1.plot(seasons, deep, marker="o", linewidth=2, label="Deep completions")
    ax1.set_xlabel("Season")
    ax1.set_ylabel("Average deep")
    ax1.tick_params(axis="x", rotation=45)
    ax1.grid(True, alpha=0.3)

    ax2 = ax1.twinx()
    ax2.plot(seasons, ppda, marker="s", linestyle="--", linewidth=2, label="PPDA")
    ax2.set_ylabel("Average PPDA")

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    plt.title("Understat deep and PPDA trend")
    fig.tight_layout()

    out = os.path.join(FIG_DIR, "understat_deep_ppda_trend.png")
    plt.savefig(out, dpi=180)
    plt.close()
    print("[OK]", out)

def main():
    os.makedirs(FIG_DIR, exist_ok=True)
    rows = read_rows()
    plot_xg_quality(rows)
    plot_deep_ppda(rows)
    print("[DONE] Understat visualizations generated.")

if __name__ == "__main__":
    main()
