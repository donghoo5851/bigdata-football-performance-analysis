#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import csv
import glob

IN_DIR = os.path.expanduser("~/football_project/data/raw/modern_matches")
OUT_DIR = os.path.expanduser("~/football_project/data/processed")
OUT_FILE = os.path.join(OUT_DIR, "modern_matches_standardized.csv")

LEAGUE_NAMES = {
    "E0": "Premier League",
    "SP1": "La Liga",
    "I1": "Serie A",
    "D1": "Bundesliga",
    "F1": "Ligue 1",
}

REQUIRED_COLUMNS = [
    "Div", "Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR",
    "HS", "AS", "HST", "AST", "HF", "AF", "HC", "AC", "HY", "AY", "HR", "AR"
]

OUTPUT_COLUMNS = [
    "source",
    "era",
    "season",
    "league",
    "date",
    "home_team",
    "away_team",
    "home_goals",
    "away_goals",
    "result",
    "total_goals",
    "home_shots",
    "away_shots",
    "home_shots_on_target",
    "away_shots_on_target",
    "home_fouls",
    "away_fouls",
    "home_corners",
    "away_corners",
    "home_yellow",
    "away_yellow",
    "home_red",
    "away_red",
]

def safe_int(value):
    if value is None or value == "":
        return ""
    try:
        return int(float(value))
    except ValueError:
        return ""

def standardize_file(path):
    rows = []

    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)

        missing = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
        if missing:
            print("[WARN] Skip {}, missing columns: {}".format(path, missing))
            return rows

        for row in reader:
            div = row.get("Div", "")
            league = LEAGUE_NAMES.get(div, div)

            home_goals = safe_int(row.get("FTHG"))
            away_goals = safe_int(row.get("FTAG"))

            if home_goals == "" or away_goals == "":
                continue

            out = {
                "source": "football-data.co.uk",
                "era": "modern",
                "season": "2024/2025",
                "league": league,
                "date": row.get("Date", ""),
                "home_team": row.get("HomeTeam", ""),
                "away_team": row.get("AwayTeam", ""),
                "home_goals": home_goals,
                "away_goals": away_goals,
                "result": row.get("FTR", ""),
                "total_goals": home_goals + away_goals,
                "home_shots": safe_int(row.get("HS")),
                "away_shots": safe_int(row.get("AS")),
                "home_shots_on_target": safe_int(row.get("HST")),
                "away_shots_on_target": safe_int(row.get("AST")),
                "home_fouls": safe_int(row.get("HF")),
                "away_fouls": safe_int(row.get("AF")),
                "home_corners": safe_int(row.get("HC")),
                "away_corners": safe_int(row.get("AC")),
                "home_yellow": safe_int(row.get("HY")),
                "away_yellow": safe_int(row.get("AY")),
                "home_red": safe_int(row.get("HR")),
                "away_red": safe_int(row.get("AR")),
            }

            rows.append(out)

    print("[OK] {} -> {} rows".format(os.path.basename(path), len(rows)))
    return rows

def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    all_rows = []
    csv_files = sorted(glob.glob(os.path.join(IN_DIR, "*.csv")))

    if not csv_files:
        raise FileNotFoundError("No CSV files found in {}".format(IN_DIR))

    for path in csv_files:
        all_rows.extend(standardize_file(path))

    with open(OUT_FILE, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(all_rows)

    print("[DONE] Saved standardized modern match data.")
    print("[OUT] {}".format(OUT_FILE))
    print("[ROWS] {}".format(len(all_rows)))

if __name__ == "__main__":
    main()
