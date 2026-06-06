#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import csv
from collections import defaultdict

PROJECT_HOME = os.path.expanduser("~/football_project")
DATA_FILE = os.path.join(PROJECT_HOME, "data/processed/football_data_matches_standardized.csv")
TABLE_DIR = os.path.join(PROJECT_HOME, "results/tables")

OUT_STANDINGS = os.path.join(TABLE_DIR, "team_standings_by_season.csv")
OUT_SEASON = os.path.join(TABLE_DIR, "big_match_season_summary.csv")
OUT_ERA = os.path.join(TABLE_DIR, "big_match_era_summary.csv")
OUT_CHANGE = os.path.join(TABLE_DIR, "big_match_change_summary.csv")

def to_float(x):
    try:
        return float(x)
    except:
        return None

def avg(values):
    vals = [v for v in values if v is not None]
    if not vals:
        return None
    return sum(vals) / len(vals)

def era_group(season_code):
    season_code = str(season_code).zfill(4)
    if season_code in ["0809", "0910", "1011", "1112"]:
        return "2008-2012"
    if season_code in ["1213", "1314", "1415", "1516"]:
        return "2012-2016"
    if season_code in ["1617", "1718", "1819", "1920"]:
        return "2016-2020"
    return "2020-2025"

def read_matches():
    rows = []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            r["season_code"] = str(r["season_code"]).zfill(4)
            rows.append(r)
    return rows

def init_team():
    return {
        "played": 0,
        "points": 0,
        "gf": 0,
        "ga": 0,
        "wins": 0,
        "draws": 0,
        "losses": 0,
    }

def build_standings(matches):
    standings = defaultdict(lambda: defaultdict(init_team))

    for r in matches:
        key = (r["season_code"], r["season"], r["league"])
        home = r["home_team"]
        away = r["away_team"]
        hg = int(float(r["home_goals"]))
        ag = int(float(r["away_goals"]))

        h = standings[key][home]
        a = standings[key][away]

        h["played"] += 1
        a["played"] += 1

        h["gf"] += hg
        h["ga"] += ag
        a["gf"] += ag
        a["ga"] += hg

        if hg > ag:
            h["points"] += 3
            h["wins"] += 1
            a["losses"] += 1
        elif hg < ag:
            a["points"] += 3
            a["wins"] += 1
            h["losses"] += 1
        else:
            h["points"] += 1
            a["points"] += 1
            h["draws"] += 1
            a["draws"] += 1

    rank_map = {}
    output = []

    for key, teams in sorted(standings.items()):
        season_code, season, league = key

        team_rows = []
        for team, stat in teams.items():
            gd = stat["gf"] - stat["ga"]
            team_rows.append({
                "season_code": season_code,
                "season": season,
                "league": league,
                "team": team,
                "played": stat["played"],
                "points": stat["points"],
                "gf": stat["gf"],
                "ga": stat["ga"],
                "gd": gd,
                "wins": stat["wins"],
                "draws": stat["draws"],
                "losses": stat["losses"],
            })

        team_rows.sort(key=lambda x: (x["points"], x["gd"], x["gf"]), reverse=True)

        for i, tr in enumerate(team_rows, start=1):
            tr["rank"] = i
            rank_map[(season_code, league, tr["team"])] = i
            output.append(tr)

    fieldnames = [
        "season_code", "season", "league", "rank", "team",
        "played", "points", "gf", "ga", "gd", "wins", "draws", "losses"
    ]

    with open(OUT_STANDINGS, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output)

    print("[OK] saved:", OUT_STANDINGS)
    return rank_map

def classify_match(r, rank_map, top_n=6):
    h_rank = rank_map.get((r["season_code"], r["league"], r["home_team"]))
    a_rank = rank_map.get((r["season_code"], r["league"], r["away_team"]))

    if h_rank is None or a_rank is None:
        return "unknown"

    h_top = h_rank <= top_n
    a_top = a_rank <= top_n

    if h_top and a_top:
        return "top6_vs_top6"
    if h_top or a_top:
        return "top6_vs_other"
    return "other_vs_other"

def summarize(rows):
    return {
        "match_count": len(rows),
        "avg_goals": avg([to_float(r["total_goals"]) for r in rows]),
        "avg_shots": avg([to_float(r["total_shots"]) for r in rows]),
        "avg_sot": avg([to_float(r["total_shots_on_target"]) for r in rows]),
        "avg_shot_conversion": avg([to_float(r["shot_conversion_rate"]) for r in rows]),
        "low_score_2_rate": avg([to_float(r["low_scoring_2_or_less"]) for r in rows]),
        "high_score_4_rate": avg([to_float(r["high_scoring_4_or_more"]) for r in rows]),
        "draw_rate": avg([to_float(r["draw_flag"]) for r in rows]),
        "home_win_rate": avg([to_float(r["home_win_flag"]) for r in rows]),
        "away_win_rate": avg([to_float(r["away_win_flag"]) for r in rows]),
        "avg_fouls": avg([to_float(r["total_fouls"]) for r in rows]),
        "avg_yellow": avg([to_float(r["total_yellow"]) for r in rows]),
        "avg_red": avg([to_float(r["total_red"]) for r in rows]),
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

def make_season_summary(matches):
    grouped = defaultdict(list)

    for r in matches:
        key = (r["season_code"], r["season"], r["match_category"])
        grouped[key].append(r)

    output = []
    for (season_code, season, category), group in sorted(grouped.items()):
        row = {
            "season_code": season_code,
            "season": season,
            "match_category": category,
        }
        row.update(summarize(group))
        output.append(round_row(row))

    fieldnames = [
        "season_code", "season", "match_category",
        "match_count", "avg_goals", "avg_shots", "avg_sot",
        "avg_shot_conversion", "low_score_2_rate", "high_score_4_rate",
        "draw_rate", "home_win_rate", "away_win_rate",
        "avg_fouls", "avg_yellow", "avg_red"
    ]

    write_csv(OUT_SEASON, fieldnames, output)
    return output

def make_era_summary(matches):
    grouped = defaultdict(list)

    for r in matches:
        key = (era_group(r["season_code"]), r["match_category"])
        grouped[key].append(r)

    output = []
    for (era, category), group in sorted(grouped.items()):
        row = {
            "era": era,
            "match_category": category,
        }
        row.update(summarize(group))
        output.append(round_row(row))

    fieldnames = [
        "era", "match_category",
        "match_count", "avg_goals", "avg_shots", "avg_sot",
        "avg_shot_conversion", "low_score_2_rate", "high_score_4_rate",
        "draw_rate", "home_win_rate", "away_win_rate",
        "avg_fouls", "avg_yellow", "avg_red"
    ]

    write_csv(OUT_ERA, fieldnames, output)
    return output

def make_change_summary(era_rows):
    by_cat = defaultdict(dict)
    for r in era_rows:
        by_cat[r["match_category"]][r["era"]] = r

    metrics = [
        "avg_goals",
        "avg_shots",
        "avg_sot",
        "avg_shot_conversion",
        "low_score_2_rate",
        "high_score_4_rate",
        "draw_rate",
        "avg_fouls",
    ]

    output = []
    for category, data in sorted(by_cat.items()):
        old = data.get("2008-2012")
        new = data.get("2020-2025")

        if not old or not new:
            continue

        row = {
            "match_category": category,
            "old_era": "2008-2012",
            "new_era": "2020-2025",
            "old_match_count": old["match_count"],
            "new_match_count": new["match_count"],
        }

        for m in metrics:
            old_v = to_float(old[m])
            new_v = to_float(new[m])
            diff = None
            pct = None

            if old_v is not None and new_v is not None:
                diff = new_v - old_v
                if old_v != 0:
                    pct = diff / old_v

            row["diff_" + m] = round(diff, 6) if diff is not None else ""
            row["pct_" + m] = round(pct, 6) if pct is not None else ""

        output.append(row)

    fieldnames = [
        "match_category", "old_era", "new_era",
        "old_match_count", "new_match_count",
    ]

    for m in metrics:
        fieldnames.append("diff_" + m)
        fieldnames.append("pct_" + m)

    write_csv(OUT_CHANGE, fieldnames, output)
    return output

def main():
    os.makedirs(TABLE_DIR, exist_ok=True)

    matches = read_matches()
    rank_map = build_standings(matches)

    annotated = []
    for r in matches:
        row = dict(r)
        row["match_category"] = classify_match(r, rank_map, top_n=6)
        annotated.append(row)

    season_rows = make_season_summary(annotated)
    era_rows = make_era_summary(annotated)
    change_rows = make_change_summary(era_rows)

    print("\n=== Big Match Era Summary ===")
    with open(OUT_ERA, "r", encoding="utf-8") as f:
        print(f.read())

    print("\n=== Big Match Change Summary ===")
    with open(OUT_CHANGE, "r", encoding="utf-8") as f:
        print(f.read())

if __name__ == "__main__":
    main()
