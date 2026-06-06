#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import csv

TABLE_DIR = os.path.expanduser("~/football_project/results/tables")
OUT_DIR = TABLE_DIR

SEASON_FILE = os.path.join(TABLE_DIR, "season_summary.csv")
OUT_FILE = os.path.join(OUT_DIR, "change_point_summary.csv")
ERA_FILE = os.path.join(OUT_DIR, "tactical_era_summary.csv")

METRICS = [
    "avg_goals",
    "avg_shots",
    "avg_shots_on_target",
    "avg_shot_conversion",
    "low_score_2_rate",
    "high_score_4_rate",
    "draw_rate",
    "home_win_rate",
    "away_win_rate",
    "avg_fouls",
    "avg_yellow",
    "avg_red",
]

#      
TACTICAL_ERAS = [
    ("2008-2012", ["0809", "0910", "1011", "1112"]),
    ("2012-2016", ["1213", "1314", "1415", "1516"]),
    ("2016-2020", ["1617", "1718", "1819", "1920"]),
    ("2020-2025", ["2021", "2122", "2223", "2324", "2425"]),
]

def to_float(value):
    try:
        return float(value)
    except:
        return None

def read_rows(path):
    with open(path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    rows.sort(key=lambda r: r["season_code"])
    return rows

def avg(values):
    values = [v for v in values if v is not None]
    if not values:
        return None
    return sum(values) / len(values)

def find_best_split(rows, metric, min_side=3):
    """
     season_code split point ,
    split         .
    min_side /       .
    """
    best = None

    for i in range(min_side, len(rows) - min_side + 1):
        before = rows[:i]
        after = rows[i:]

        before_avg = avg([to_float(r[metric]) for r in before])
        after_avg = avg([to_float(r[metric]) for r in after])

        if before_avg is None or after_avg is None:
            continue

        diff = after_avg - before_avg
        abs_diff = abs(diff)
        pct_change = None

        if before_avg != 0:
            pct_change = diff / before_avg

        split_season = after[0]["season"]
        split_code = after[0]["season_code"]

        candidate = {
            "metric": metric,
            "best_split_code": split_code,
            "best_split_season": split_season,
            "before_start": before[0]["season"],
            "before_end": before[-1]["season"],
            "after_start": after[0]["season"],
            "after_end": after[-1]["season"],
            "before_avg": before_avg,
            "after_avg": after_avg,
            "diff": diff,
            "abs_diff": abs_diff,
            "pct_change": pct_change,
            "before_n": len(before),
            "after_n": len(after),
        }

        if best is None or candidate["abs_diff"] > best["abs_diff"]:
            best = candidate

    return best

def write_change_points(rows):
    output = []

    for metric in METRICS:
        best = find_best_split(rows, metric)
        if best:
            output.append(best)

    fieldnames = [
        "metric",
        "best_split_code",
        "best_split_season",
        "before_start",
        "before_end",
        "after_start",
        "after_end",
        "before_avg",
        "after_avg",
        "diff",
        "abs_diff",
        "pct_change",
        "before_n",
        "after_n",
    ]

    with open(OUT_FILE, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for r in output:
            row = dict(r)
            for k in ["before_avg", "after_avg", "diff", "abs_diff", "pct_change"]:
                if row[k] is not None:
                    row[k] = round(row[k], 6)
            writer.writerow(row)

    print("[OK] change point summary saved:", OUT_FILE)

def write_tactical_era_summary(rows):
    fieldnames = ["era", "season_count"] + METRICS

    output_rows = []

    for era_name, season_codes in TACTICAL_ERAS:
        selected = [r for r in rows if r["season_code"] in season_codes]

        out = {
            "era": era_name,
            "season_count": len(selected),
        }

        for metric in METRICS:
            out[metric] = avg([to_float(r[metric]) for r in selected])
            if out[metric] is not None:
                out[metric] = round(out[metric], 6)

        output_rows.append(out)

    with open(ERA_FILE, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    print("[OK] tactical era summary saved:", ERA_FILE)

def print_key_results():
    print("\n=== Change Point Summary ===")
    with open(OUT_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            print(
                r["metric"],
                "| split:", r["best_split_season"],
                "| before:", r["before_avg"],
                "| after:", r["after_avg"],
                "| diff:", r["diff"],
                "| pct:", r["pct_change"]
            )

    print("\n=== Tactical Era Summary ===")
    with open(ERA_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            print(r)

def main():
    rows = read_rows(SEASON_FILE)
    write_change_points(rows)
    write_tactical_era_summary(rows)
    print_key_results()

if __name__ == "__main__":
    main()
