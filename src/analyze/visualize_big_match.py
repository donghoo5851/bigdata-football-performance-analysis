#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PROJECT_HOME = os.path.expanduser("~/football_project")
TABLE_FILE = os.path.join(PROJECT_HOME, "results/tables/big_match_era_summary.csv")
FIG_DIR = os.path.join(PROJECT_HOME, "results/figures")

CATEGORY_LABELS = {
    "top6_vs_top6": "Top 6 vs Top 6",
    "top6_vs_other": "Top 6 vs Other",
    "other_vs_other": "Other vs Other",
}

CATEGORY_ORDER = ["top6_vs_top6", "top6_vs_other", "other_vs_other"]
ERA_ORDER = ["2008-2012", "2012-2016", "2016-2020", "2020-2025"]

def to_float(x):
    try:
        return float(x)
    except:
        return 0.0

def read_rows():
    with open(TABLE_FILE, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return rows

def get_value(rows, era, category, metric):
    for r in rows:
        if r["era"] == era and r["match_category"] == category:
            return to_float(r[metric])
    return 0.0

def plot_big_match_goals_shots(rows):
    # Index by 2008-2012 for each category so goals and shots can be compared together.
    plt.figure(figsize=(12, 6))

    for category in CATEGORY_ORDER:
        base_goals = get_value(rows, "2008-2012", category, "avg_goals")
        base_shots = get_value(rows, "2008-2012", category, "avg_shots")

        goals_idx = []
        shots_idx = []

        for era in ERA_ORDER:
            goals = get_value(rows, era, category, "avg_goals")
            shots = get_value(rows, era, category, "avg_shots")

            goals_idx.append(goals / base_goals * 100 if base_goals else 0)
            shots_idx.append(shots / base_shots * 100 if base_shots else 0)

        if category == "top6_vs_top6":
            plt.plot(ERA_ORDER, goals_idx, marker="o", linewidth=2.5, label="Top6 vs Top6 goals")
            plt.plot(ERA_ORDER, shots_idx, marker="s", linestyle="--", linewidth=2.5, label="Top6 vs Top6 shots")

    plt.axhline(100, linestyle="--", linewidth=1)
    plt.title("Big match goals and shots trend")
    plt.xlabel("Era")
    plt.ylabel("Index value, 2008-2012 = 100")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    out = os.path.join(FIG_DIR, "big_match_goals_shots_change.png")
    plt.savefig(out, dpi=180)
    plt.close()
    print("[OK]", out)

def plot_big_match_score_rates(rows):
    eras = ERA_ORDER
    low = [get_value(rows, era, "top6_vs_top6", "low_score_2_rate") * 100 for era in eras]
    high = [get_value(rows, era, "top6_vs_top6", "high_score_4_rate") * 100 for era in eras]
    draw = [get_value(rows, era, "top6_vs_top6", "draw_rate") * 100 for era in eras]

    plt.figure(figsize=(12, 6))
    plt.plot(eras, low, marker="o", linewidth=2, label="2 or fewer goals")
    plt.plot(eras, high, marker="s", linewidth=2, label="4 or more goals")
    plt.plot(eras, draw, marker="^", linewidth=2, label="Draw")

    plt.title("Big match scoring and draw rates")
    plt.xlabel("Era")
    plt.ylabel("Rate (%)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    out = os.path.join(FIG_DIR, "big_match_score_rate_change.png")
    plt.savefig(out, dpi=180)
    plt.close()
    print("[OK]", out)

def plot_match_category_goal_change(rows):
    old_era = "2008-2012"
    new_era = "2020-2025"

    labels = []
    goal_diffs = []
    shot_diffs = []

    for category in CATEGORY_ORDER:
        labels.append(CATEGORY_LABELS[category])
        old_goals = get_value(rows, old_era, category, "avg_goals")
        new_goals = get_value(rows, new_era, category, "avg_goals")
        old_shots = get_value(rows, old_era, category, "avg_shots")
        new_shots = get_value(rows, new_era, category, "avg_shots")

        goal_diffs.append(new_goals - old_goals)
        shot_diffs.append(new_shots - old_shots)

    x = range(len(labels))
    width = 0.35

    plt.figure(figsize=(10, 6))
    plt.bar([i - width/2 for i in x], goal_diffs, width=width, label="Goals change")
    plt.bar([i + width/2 for i in x], shot_diffs, width=width, label="Shots change")

    plt.axhline(0, linewidth=1)
    plt.title("Change from 2008-2012 to 2020-2025 by match type")
    plt.xlabel("Match type")
    plt.ylabel("After - before")
    plt.xticks(list(x), labels, rotation=15, ha="right")
    plt.legend()
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()

    out = os.path.join(FIG_DIR, "big_match_category_change.png")
    plt.savefig(out, dpi=180)
    plt.close()
    print("[OK]", out)

def main():
    os.makedirs(FIG_DIR, exist_ok=True)
    rows = read_rows()

    plot_big_match_goals_shots(rows)
    plot_big_match_score_rates(rows)
    plot_match_category_goal_change(rows)

    print("[DONE] Big match visualizations generated.")

if __name__ == "__main__":
    main()
