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
ERA_FILE = os.path.join(TABLE_DIR, "tactical_era_summary.csv")
CHANGE_FILE = os.path.join(TABLE_DIR, "change_point_summary.csv")

def read_csv(path):
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def to_float(x):
    try:
        return float(x)
    except:
        return 0.0

def save_era_metric_chart(rows, metric, title, ylabel, filename):
    eras = [r["era"] for r in rows]
    values = [to_float(r[metric]) for r in rows]

    plt.figure(figsize=(9, 5))
    plt.plot(eras, values, marker="o")
    plt.title(title)
    plt.xlabel("Tactical Era")
    plt.ylabel(ylabel)
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()

    out = os.path.join(FIG_DIR, filename)
    plt.savefig(out, dpi=150)
    plt.close()
    print("[OK]", out)

def save_season_dual_axis(rows):
    seasons = [r["season"] for r in rows]
    goals = [to_float(r["avg_goals"]) for r in rows]
    shots = [to_float(r["avg_shots"]) for r in rows]

    fig, ax1 = plt.subplots(figsize=(12, 6))

    ax1.plot(seasons, goals, marker="o", label="Average Goals")
    ax1.set_xlabel("Season")
    ax1.set_ylabel("Average Goals")

    ax2 = ax1.twinx()
    ax2.plot(seasons, shots, marker="s", label="Average Shots")
    ax2.set_ylabel("Average Shots")

    plt.title("Average Goals and Shots per Match by Season")
    ax1.tick_params(axis="x", rotation=45)
    fig.tight_layout()

    out = os.path.join(FIG_DIR, "season_goals_vs_shots.png")
    plt.savefig(out, dpi=150)
    plt.close()
    print("[OK]", out)

def save_home_away_chart(rows):
    seasons = [r["season"] for r in rows]
    home = [to_float(r["home_win_rate"]) for r in rows]
    away = [to_float(r["away_win_rate"]) for r in rows]
    draw = [to_float(r["draw_rate"]) for r in rows]

    plt.figure(figsize=(12, 6))
    plt.plot(seasons, home, marker="o", label="Home Win Rate")
    plt.plot(seasons, away, marker="s", label="Away Win Rate")
    plt.plot(seasons, draw, marker="^", label="Draw Rate")

    plt.title("Home Win, Away Win, and Draw Rate by Season")
    plt.xlabel("Season")
    plt.ylabel("Rate")
    plt.xticks(rotation=45, ha="right")
    plt.legend()
    plt.tight_layout()

    out = os.path.join(FIG_DIR, "season_home_away_draw_rate.png")
    plt.savefig(out, dpi=150)
    plt.close()
    print("[OK]", out)

def save_change_point_chart(rows):
    metrics = []
    pct_changes = []

    for r in rows:
        metrics.append(r["metric"])
        pct_changes.append(to_float(r["pct_change"]) * 100)

    plt.figure(figsize=(12, 6))
    plt.bar(metrics, pct_changes)
    plt.title("Largest Before-After Change by Metric")
    plt.xlabel("Metric")
    plt.ylabel("Percent Change (%)")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    out = os.path.join(FIG_DIR, "change_point_percent_change.png")
    plt.savefig(out, dpi=150)
    plt.close()
    print("[OK]", out)

def save_era_combined_chart(rows):
    eras = [r["era"] for r in rows]
    goals = [to_float(r["avg_goals"]) for r in rows]
    shots = [to_float(r["avg_shots"]) for r in rows]
    conversion = [to_float(r["avg_shot_conversion"]) for r in rows]

    plt.figure(figsize=(10, 6))
    plt.plot(eras, goals, marker="o", label="Avg Goals")
    plt.plot(eras, shots, marker="s", label="Avg Shots")
    plt.plot(eras, [v * 100 for v in conversion], marker="^", label="Shot Conversion (%)")

    plt.title("Goals, Shots, and Shot Conversion by Tactical Era")
    plt.xlabel("Tactical Era")
    plt.ylabel("Value")
    plt.xticks(rotation=20, ha="right")
    plt.legend()
    plt.tight_layout()

    out = os.path.join(FIG_DIR, "era_goals_shots_conversion.png")
    plt.savefig(out, dpi=150)
    plt.close()
    print("[OK]", out)

def main():
    os.makedirs(FIG_DIR, exist_ok=True)

    season_rows = read_csv(SEASON_FILE)
    era_rows = read_csv(ERA_FILE)
    change_rows = read_csv(CHANGE_FILE)

    save_era_metric_chart(
        era_rows,
        "avg_goals",
        "Average Goals by Tactical Era",
        "Average Goals",
        "era_avg_goals.png"
    )

    save_era_metric_chart(
        era_rows,
        "avg_shots",
        "Average Shots by Tactical Era",
        "Average Shots",
        "era_avg_shots.png"
    )

    save_era_metric_chart(
        era_rows,
        "avg_shot_conversion",
        "Shot Conversion Rate by Tactical Era",
        "Goals / Shots",
        "era_shot_conversion.png"
    )

    save_era_metric_chart(
        era_rows,
        "low_score_2_rate",
        "Low-scoring Match Rate by Tactical Era",
        "Rate of Matches with 2 or Fewer Goals",
        "era_low_score_2_rate.png"
    )

    save_era_combined_chart(era_rows)
    save_season_dual_axis(season_rows)
    save_home_away_chart(season_rows)
    save_change_point_chart(change_rows)

    print("[DONE] advanced figures generated.")

if __name__ == "__main__":
    main()
