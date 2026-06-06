#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import csv
from collections import defaultdict

PROJECT_HOME = os.path.expanduser("~/football_project")

UNDERSTAT_FILE = os.path.join(PROJECT_HOME, "data/raw/understat/game_stats.csv")
SEASON_SUMMARY_FILE = os.path.join(PROJECT_HOME, "results/tables/season_summary.csv")

TABLE_DIR = os.path.join(PROJECT_HOME, "results/tables")
OUT_LEAGUE_SEASON = os.path.join(TABLE_DIR, "understat_league_season_summary.csv")
OUT_OVERALL_SEASON = os.path.join(TABLE_DIR, "understat_overall_season_summary.csv")
OUT_JOINED = os.path.join(TABLE_DIR, "understat_xg_shot_quality_summary.csv")

# Understat league names -> project league names
LEAGUE_MAP = {
    "EPL": "Premier League",
    "La_liga": "La Liga",
    "La Liga": "La Liga",
    "Bundesliga": "Bundesliga",
    "Serie_A": "Serie A",
    "Serie A": "Serie A",
    "Ligue_1": "Ligue 1",
    "Ligue 1": "Ligue 1",
}

TOP5 = set(["Premier League", "La Liga", "Bundesliga", "Serie A", "Ligue 1"])

# 2024 season is likely incomplete in the downloaded file, so use stable completed seasons.
MIN_SEASON = 2014
MAX_SEASON = 2023

def to_float(x):
    try:
        if x is None or x == "":
            return None
        return float(x)
    except:
        return None

def avg(values):
    vals = [v for v in values if v is not None]
    if not vals:
        return None
    return sum(vals) / len(vals)

def season_to_label(season):
    season = int(season)
    return "{}/{}".format(season, season + 1)

def season_to_code(season):
    season = int(season)
    return "{:02d}{:02d}".format(season % 100, (season + 1) % 100)

def read_understat_rows():
    rows = []

    with open(UNDERSTAT_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for r in reader:
            raw_league = r.get("league", "")
            league = LEAGUE_MAP.get(raw_league)

            if league not in TOP5:
                continue

            season = int(r["season"])

            # Exclude incomplete or out-of-range seasons
            if season < MIN_SEASON or season > MAX_SEASON:
                continue

            rows.append({
                "league": league,
                "season": season,
                "season_label": season_to_label(season),
                "season_code": season_to_code(season),
                "club_name": r.get("club_name", ""),
                "home_away": r.get("home_away", ""),
                "xG": to_float(r.get("xG")),
                "xGA": to_float(r.get("xGA")),
                "npxG": to_float(r.get("npxG")),
                "npxGA": to_float(r.get("npxGA")),
                "ppda": to_float(r.get("ppda")),
                "ppda_allowed": to_float(r.get("ppda_allowed")),
                "deep": to_float(r.get("deep")),
                "deep_allowed": to_float(r.get("deep_allowed")),
                "scored": to_float(r.get("scored")),
                "missed": to_float(r.get("missed")),
                "xpts": to_float(r.get("xpts")),
            })

    return rows

def summarize_group(rows):
    return {
        "team_match_count": len(rows),
        "avg_xg_for": avg([r["xG"] for r in rows]),
        "avg_xga": avg([r["xGA"] for r in rows]),
        "avg_npxg_for": avg([r["npxG"] for r in rows]),
        "avg_npxga": avg([r["npxGA"] for r in rows]),
        "avg_goals_for": avg([r["scored"] for r in rows]),
        "avg_goals_against": avg([r["missed"] for r in rows]),
        "avg_xpts": avg([r["xpts"] for r in rows]),
        "avg_ppda": avg([r["ppda"] for r in rows]),
        "avg_ppda_allowed": avg([r["ppda_allowed"] for r in rows]),
        "avg_deep": avg([r["deep"] for r in rows]),
        "avg_deep_allowed": avg([r["deep_allowed"] for r in rows]),
    }

def round_row(row):
    out = {}
    for k, v in row.items():
        if isinstance(v, float):
            out[k] = round(v, 6)
        else:
            out[k] = v
    return out

def write_csv(path, fieldnames, rows):
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print("[OK] saved:", path)

def make_league_season_summary(rows):
    grouped = defaultdict(list)

    for r in rows:
        key = (r["season_code"], r["season_label"], r["league"])
        grouped[key].append(r)

    output = []

    for (season_code, season_label, league), group in sorted(grouped.items()):
        row = {
            "season_code": season_code,
            "season": season_label,
            "league": league,
        }
        row.update(summarize_group(group))
        output.append(round_row(row))

    fieldnames = [
        "season_code",
        "season",
        "league",
        "team_match_count",
        "avg_xg_for",
        "avg_xga",
        "avg_npxg_for",
        "avg_npxga",
        "avg_goals_for",
        "avg_goals_against",
        "avg_xpts",
        "avg_ppda",
        "avg_ppda_allowed",
        "avg_deep",
        "avg_deep_allowed",
    ]

    write_csv(OUT_LEAGUE_SEASON, fieldnames, output)
    return output

def make_overall_season_summary(rows):
    grouped = defaultdict(list)

    for r in rows:
        key = (r["season_code"], r["season_label"])
        grouped[key].append(r)

    output = []

    for (season_code, season_label), group in sorted(grouped.items()):
        row = {
            "season_code": season_code,
            "season": season_label,
        }
        row.update(summarize_group(group))
        output.append(round_row(row))

    fieldnames = [
        "season_code",
        "season",
        "team_match_count",
        "avg_xg_for",
        "avg_xga",
        "avg_npxg_for",
        "avg_npxga",
        "avg_goals_for",
        "avg_goals_against",
        "avg_xpts",
        "avg_ppda",
        "avg_ppda_allowed",
        "avg_deep",
        "avg_deep_allowed",
    ]

    write_csv(OUT_OVERALL_SEASON, fieldnames, output)
    return output

def read_existing_season_summary():
    data = {}

    with open(SEASON_SUMMARY_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for r in reader:
            code = str(r["season_code"]).zfill(4)
            data[code] = r

    return data

def make_joined_xg_shot_quality(understat_overall):
    existing = read_existing_season_summary()
    output = []

    for r in understat_overall:
        code = str(r["season_code"]).zfill(4)
        base = existing.get(code)

        if not base:
            continue

        avg_total_shots_match = to_float(base.get("avg_shots"))
        avg_team_shots_match = None
        xg_per_shot_proxy = None

        if avg_total_shots_match is not None:
            avg_team_shots_match = avg_total_shots_match / 2.0

        if avg_team_shots_match and avg_team_shots_match != 0:
            xg_per_shot_proxy = to_float(r["avg_xg_for"]) / avg_team_shots_match

        out = {
            "season_code": code,
            "season": r["season"],
            "avg_total_shots_per_match": avg_total_shots_match,
            "avg_team_shots_per_match": avg_team_shots_match,
            "avg_xg_for_per_team_match": to_float(r["avg_xg_for"]),
            "avg_goals_for_per_team_match": to_float(r["avg_goals_for"]),
            "xg_per_shot_proxy": xg_per_shot_proxy,
            "goals_per_xg": None,
            "avg_ppda": to_float(r["avg_ppda"]),
            "avg_deep": to_float(r["avg_deep"]),
        }

        if out["avg_xg_for_per_team_match"] and out["avg_xg_for_per_team_match"] != 0:
            out["goals_per_xg"] = out["avg_goals_for_per_team_match"] / out["avg_xg_for_per_team_match"]

        output.append(round_row(out))

    fieldnames = [
        "season_code",
        "season",
        "avg_total_shots_per_match",
        "avg_team_shots_per_match",
        "avg_xg_for_per_team_match",
        "avg_goals_for_per_team_match",
        "xg_per_shot_proxy",
        "goals_per_xg",
        "avg_ppda",
        "avg_deep",
    ]

    write_csv(OUT_JOINED, fieldnames, output)
    return output

def main():
    os.makedirs(TABLE_DIR, exist_ok=True)

    rows = read_understat_rows()

    print("[INFO] Understat top-5 team-match rows:", len(rows))
    print("[INFO] Seasons:", MIN_SEASON, "to", MAX_SEASON)

    league_season = make_league_season_summary(rows)
    overall = make_overall_season_summary(rows)
    joined = make_joined_xg_shot_quality(overall)

    print("\n=== Understat xG shot quality summary ===")
    for r in joined:
        print(r)

if __name__ == "__main__":
    main()
