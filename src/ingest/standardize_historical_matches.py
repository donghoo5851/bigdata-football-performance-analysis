#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import csv

CSV_DIR = os.path.expanduser("~/football_project/data/csv")
OUT_DIR = os.path.expanduser("~/football_project/data/processed")
OUT_FILE = os.path.join(OUT_DIR, "historical_matches_standardized.csv")

MATCH_FILE = os.path.join(CSV_DIR, "Match.csv")
LEAGUE_FILE = os.path.join(CSV_DIR, "League.csv")
TEAM_FILE = os.path.join(CSV_DIR, "Team.csv")
COUNTRY_FILE = os.path.join(CSV_DIR, "Country.csv")

OUTPUT_COLUMNS = [
    "source",
    "era",
    "season",
    "league",
    "country",
    "date",
    "home_team",
    "away_team",
    "home_goals",
    "away_goals",
    "result",
    "total_goals",
]

def load_mapping(path, key_col, value_col):
    mapping = {}
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            mapping[row[key_col]] = row[value_col]
    return mapping

def load_leagues(path):
    leagues = {}
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            leagues[row["id"]] = {
                "country_id": row["country_id"],
                "name": row["name"],
            }
    return leagues

def safe_int(value):
    if value is None or value == "":
        return ""
    try:
        return int(float(value))
    except ValueError:
        return ""

def get_result(home_goals, away_goals):
    if home_goals > away_goals:
        return "H"
    if home_goals < away_goals:
        return "A"
    return "D"

def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    countries = load_mapping(COUNTRY_FILE, "id", "name")
    leagues = load_leagues(LEAGUE_FILE)
    teams = load_mapping(TEAM_FILE, "team_api_id", "team_long_name")

    output_rows = []

    with open(MATCH_FILE, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            home_goals = safe_int(row.get("home_team_goal"))
            away_goals = safe_int(row.get("away_team_goal"))

            if home_goals == "" or away_goals == "":
                continue

            league_id = row.get("league_id", "")
            league_info = leagues.get(league_id, {})
            league_name = league_info.get("name", "")
            country_name = countries.get(league_info.get("country_id", ""), "")

            home_team = teams.get(row.get("home_team_api_id", ""), row.get("home_team_api_id", ""))
            away_team = teams.get(row.get("away_team_api_id", ""), row.get("away_team_api_id", ""))

            out = {
                "source": "European Soccer Database",
                "era": "historical",
                "season": row.get("season", ""),
                "league": league_name,
                "country": country_name,
                "date": row.get("date", ""),
                "home_team": home_team,
                "away_team": away_team,
                "home_goals": home_goals,
                "away_goals": away_goals,
                "result": get_result(home_goals, away_goals),
                "total_goals": home_goals + away_goals,
            }

            output_rows.append(out)

    with open(OUT_FILE, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(output_rows)

    print("[DONE] Saved standardized historical match data.")
    print("[OUT] {}".format(OUT_FILE))
    print("[ROWS] {}".format(len(output_rows)))

if __name__ == "__main__":
    main()
