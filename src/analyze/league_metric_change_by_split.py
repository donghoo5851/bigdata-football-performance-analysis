#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import csv
from collections import defaultdict

TABLE_DIR = os.path.expanduser("~/football_project/results/tables")
DATA_FILE = os.path.expanduser("~/football_project/data/processed/football_data_matches_standardized.csv")
CHANGE_POINT_FILE = os.path.join(TABLE_DIR, "change_point_summary.csv")
OUT_FILE = os.path.join(TABLE_DIR, "league_metric_change_by_split.csv")

# change_point_summary metric       
METRIC_TO_RAW_COL = {
    "avg_goals": "total_goals",
    "avg_shots": "total_shots",
    "avg_shots_on_target": "total_shots_on_target",
    "avg_shot_conversion": "shot_conversion_rate",
    "low_score_2_rate": "low_scoring_2_or_less",
    "high_score_4_rate": "high_scoring_4_or_more",
    "draw_rate": "draw_flag",
    "home_win_rate": "home_win_flag",
    "away_win_rate": "away_win_flag",
    "avg_fouls": "total_fouls",
    "avg_yellow": "total_yellow",
    "avg_red": "total_red",
}

TARGET_METRICS = [
    "avg_goals",
    "avg_shots",
    "avg_shots_on_target",
    "avg_shot_conversion",
    "low_score_2_rate",
    "high_score_4_rate",
    "home_win_rate",
    "away_win_rate",
    "avg_fouls",
    "avg_red",
]

def to_float(x):
    try:
        return float(x)
    except:
        return None

def avg(values):
    values = [v for v in values if v is not None]
    if not values:
        return None
    return sum(values) / len(values)

def read_change_points():
    split_by_metric = {}

    with open(CHANGE_POINT_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            metric = r["metric"]
            if metric in TARGET_METRICS:
                split_by_metric[metric] = {
                    "split_code": str(r["best_split_code"]).zfill(4),
                    "split_season": r["best_split_season"],
                }

    return split_by_metric

def read_match_rows():
    rows = []

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for r in reader:
            r["season_code"] = str(r["season_code"]).zfill(4)
            rows.append(r)

    return rows

def main():
    split_by_metric = read_change_points()
    rows = read_match_rows()

    leagues = sorted(set(r["league"] for r in rows))

    output_rows = []

    for metric in TARGET_METRICS:
        raw_col = METRIC_TO_RAW_COL[metric]
        split_info = split_by_metric.get(metric)

        if not split_info:
            continue

        split_code = split_info["split_code"]
        split_season = split_info["split_season"]

        for league in leagues:
            before_values = []
            after_values = []
            before_count = 0
            after_count = 0

            for r in rows:
                if r["league"] != league:
                    continue

                value = to_float(r.get(raw_col))
                if value is None:
                    continue

                if r["season_code"] < split_code:
                    before_values.append(value)
                    before_count += 1
                else:
                    after_values.append(value)
                    after_count += 1

            before_avg = avg(before_values)
            after_avg = avg(after_values)

            if before_avg is None or after_avg is None:
                continue

            diff = after_avg - before_avg
            pct_change = "" if before_avg == 0 else diff / before_avg

            output_rows.append({
                "metric": metric,
                "raw_column": raw_col,
                "split_code": split_code,
                "split_season": split_season,
                "league": league,
                "before_match_count": before_count,
                "after_match_count": after_count,
                "before_avg": round(before_avg, 6),
                "after_avg": round(after_avg, 6),
                "diff": round(diff, 6),
                "pct_change": round(pct_change, 6) if pct_change != "" else "",
            })

    fieldnames = [
        "metric",
        "raw_column",
        "split_code",
        "split_season",
        "league",
        "before_match_count",
        "after_match_count",
        "before_avg",
        "after_avg",
        "diff",
        "pct_change",
    ]

    with open(OUT_FILE, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    print("[OK] saved:", OUT_FILE)

    print("\n=== League Metric Change by Split ===")
    with open(OUT_FILE, "r", encoding="utf-8") as f:
        print(f.read())

if __name__ == "__main__":
    main()
