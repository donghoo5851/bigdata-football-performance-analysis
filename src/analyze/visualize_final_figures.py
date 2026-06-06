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
LEAGUE_SPLIT_FILE = os.path.join(TABLE_DIR, "league_metric_change_by_split.csv")

def read_csv(path):
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def to_float(x):
    try:
        return float(x)
    except:
        return 0.0

def save_final_era_metrics_panel(era_rows):
    eras = [r["era"] for r in era_rows]
    avg_shots = [to_float(r["avg_shots"]) for r in era_rows]
    avg_goals = [to_float(r["avg_goals"]) for r in era_rows]
    conversion = [to_float(r["avg_shot_conversion"]) * 100 for r in era_rows]

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.8))

    axes[0].plot(eras, avg_shots, marker="o", color="#1f77b4", linewidth=2)
    axes[0].set_title("Average shots")
    axes[0].set_ylabel("Shots per match")
    axes[0].set_ylim(min(avg_shots) - 0.4, max(avg_shots) + 0.4)

    axes[1].plot(eras, avg_goals, marker="o", color="#d62728", linewidth=2)
    axes[1].set_title("Average goals")
    axes[1].set_ylabel("Goals per match")
    axes[1].set_ylim(min(avg_goals) - 0.05, max(avg_goals) + 0.05)

    axes[2].plot(eras, conversion, marker="o", color="#2ca02c", linewidth=2)
    axes[2].set_title("Shot conversion")
    axes[2].set_ylabel("Goals / shots (%)")
    axes[2].set_ylim(min(conversion) - 0.3, max(conversion) + 0.3)

    for ax in axes:
        ax.set_xlabel("Era")
        ax.tick_params(axis="x", rotation=20)
        ax.grid(True, alpha=0.3)

    fig.suptitle("Match dynamics by tactical era", fontsize=14)
    fig.tight_layout()

    out = os.path.join(FIG_DIR, "final_era_metrics_panel.png")
    plt.savefig(out, dpi=180)
    plt.close()
    print("[OK]", out)

def save_season_indexed_trends(season_rows):
    seasons = [r["season"] for r in season_rows]

    base_goals = to_float(season_rows[0]["avg_goals"])
    base_shots = to_float(season_rows[0]["avg_shots"])
    base_conversion = to_float(season_rows[0]["avg_shot_conversion"])

    goals_idx = [to_float(r["avg_goals"]) / base_goals * 100 for r in season_rows]
    shots_idx = [to_float(r["avg_shots"]) / base_shots * 100 for r in season_rows]
    conv_idx = [to_float(r["avg_shot_conversion"]) / base_conversion * 100 for r in season_rows]

    plt.figure(figsize=(13, 6))
    plt.plot(seasons, shots_idx, marker="o", color="#1f77b4", linewidth=2, label="Shots index")
    plt.plot(seasons, goals_idx, marker="s", color="#d62728", linewidth=2, label="Goals index")
    plt.plot(seasons, conv_idx, marker="^", color="#2ca02c", linewidth=2, label="Shot conversion index")

    plt.axhline(100, color="gray", linestyle="--", linewidth=1)
    plt.title("Indexed trend of shots, goals, and shot conversion")
    plt.xlabel("Season")
    plt.ylabel("Index value, 2008/09 = 100")
    plt.xticks(rotation=45, ha="right")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    out = os.path.join(FIG_DIR, "final_season_indexed_trends.png")
    plt.savefig(out, dpi=180)
    plt.close()
    print("[OK]", out)

def save_scoring_match_rates(season_rows):
    seasons = [r["season"] for r in season_rows]
    low = [to_float(r["low_score_2_rate"]) * 100 for r in season_rows]
    high = [to_float(r["high_score_4_rate"]) * 100 for r in season_rows]

    plt.figure(figsize=(13, 6))
    plt.plot(seasons, low, marker="o", color="#9467bd", linewidth=2, label="2 or fewer goals")
    plt.plot(seasons, high, marker="s", color="#ff7f0e", linewidth=2, label="4 or more goals")

    plt.title("Low-scoring and high-scoring match rates by season")
    plt.xlabel("Season")
    plt.ylabel("Match rate (%)")
    plt.xticks(rotation=45, ha="right")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    out = os.path.join(FIG_DIR, "final_scoring_match_rates.png")
    plt.savefig(out, dpi=180)
    plt.close()
    print("[OK]", out)

def save_home_away_draw_rates(season_rows):
    seasons = [r["season"] for r in season_rows]
    home = [to_float(r["home_win_rate"]) * 100 for r in season_rows]
    away = [to_float(r["away_win_rate"]) * 100 for r in season_rows]
    draw = [to_float(r["draw_rate"]) * 100 for r in season_rows]

    plt.figure(figsize=(13, 6))
    plt.plot(seasons, home, marker="o", color="#d62728", linewidth=2, label="Home win")
    plt.plot(seasons, away, marker="s", color="#1f77b4", linewidth=2, label="Away win")
    plt.plot(seasons, draw, marker="^", color="#2ca02c", linewidth=2, label="Draw")

    plt.title("Home win, away win, and draw rates by season")
    plt.xlabel("Season")
    plt.ylabel("Rate (%)")
    plt.xticks(rotation=45, ha="right")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    out = os.path.join(FIG_DIR, "final_home_away_draw_rates.png")
    plt.savefig(out, dpi=180)
    plt.close()
    print("[OK]", out)

def get_metric_rows(rows, metric):
    selected = [r for r in rows if r["metric"] == metric]
    selected.sort(key=lambda r: to_float(r["diff"]))
    return selected

def save_league_change_bar(league_rows, metric, title, ylabel, filename):
    rows = get_metric_rows(league_rows, metric)
    leagues = [r["league"] for r in rows]
    diffs = [to_float(r["diff"]) for r in rows]
    split = rows[0]["split_season"] if rows else ""

    plt.figure(figsize=(10, 5.5))
    colors = ["#d62728" if v < 0 else "#1f77b4" for v in diffs]
    plt.bar(leagues, diffs, color=colors)

    plt.axhline(0, color="black", linewidth=1)
    plt.title(title + " (split: " + split + ")")
    plt.xlabel("League")
    plt.ylabel(ylabel)
    plt.xticks(rotation=25, ha="right")
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()

    out = os.path.join(FIG_DIR, filename)
    plt.savefig(out, dpi=180)
    plt.close()
    print("[OK]", out)

def main():
    os.makedirs(FIG_DIR, exist_ok=True)

    season_rows = read_csv(SEASON_FILE)
    season_rows.sort(key=lambda r: r["season_code"])

    era_rows = read_csv(ERA_FILE)
    league_split_rows = read_csv(LEAGUE_SPLIT_FILE)

    save_final_era_metrics_panel(era_rows)
    save_season_indexed_trends(season_rows)
    save_scoring_match_rates(season_rows)
    save_home_away_draw_rates(season_rows)

    save_league_change_bar(
        league_split_rows,
        "avg_goals",
        "League-level change in average goals",
        "After - before goals per match",
        "final_league_goals_change.png"
    )

    save_league_change_bar(
        league_split_rows,
        "avg_shots",
        "League-level change in average shots",
        "After - before shots per match",
        "final_league_shots_change.png"
    )

    save_league_change_bar(
        league_split_rows,
        "avg_shot_conversion",
        "League-level change in shot conversion",
        "After - before goals per shot",
        "final_league_conversion_change.png"
    )

    print("[DONE] final figures generated.")

if __name__ == "__main__":
    main()
