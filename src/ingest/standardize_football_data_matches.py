#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import csv
import glob

IN_DIR = os.path.expanduser("~/football_project/data/raw/football_data_matches")
OUT_DIR = os.path.expanduser("~/football_project/data/processed")
OUT_FILE = os.path.join(OUT_DIR, "football_data_matches_standardized.csv")

LEAGUE_NAMES = {
    "E0": "Premier League",
    "SP1": "La Liga",
    "I1": "Serie A",
    "D1": "Bundesliga",
    "F1": "Ligue 1",
}

SEASON_MAP = {
    "0809": "2008/2009", "0910": "2009/2010", "1011": "2010/2011",
    "1112": "2011/2012", "1213": "2012/2013", "1314": "2013/2014",
    "1415": "2014/2015", "1516": "2015/2016", "1617": "2016/2017",
    "1718": "2017/2018", "1819": "2018/2019", "1920": "2019/2020",
    "2021": "2020/2021", "2122": "2021/2022", "2223": "2022/2023",
    "2324": "2023/2024", "2425": "2024/2025",
}

REQUIRED = ["Div", "Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR",
            "HS", "AS", "HST", "AST", "HF", "AF", "HC", "AC", "HY", "AY", "HR", "AR"]

OUT_COLS = [
    "source", "season_code", "season", "era", "league", "date",
    "home_team", "away_team", "home_goals", "away_goals", "result",
    "total_goals", "home_shots", "away_shots", "total_shots",
    "home_shots_on_target", "away_shots_on_target", "total_shots_on_target",
    "home_fouls", "away_fouls", "total_fouls",
    "home_corners", "away_corners", "total_corners",
    "home_yellow", "away_yellow", "total_yellow",
    "home_red", "away_red", "total_red",
    "low_scoring_1_or_less", "low_scoring_2_or_less",
    "high_scoring_4_or_more", "draw_flag", "home_win_flag", "away_win_flag",
    "shot_conversion_rate", "shot_on_target_rate"
]

def safe_int(v):
    if v is None or v == "":
        return ""
    try:
        return int(float(v))
    except ValueError:
        return ""

def safe_rate(num, den):
    if num == "" or den == "" or den == 0:
        return ""
    return round(float(num) / float(den), 6)

def get_era(code):
    if code in ["0809", "0910", "1011", "1112", "1213", "1314", "1415", "1516"]:
        return "historical"
    return "modern_transition"

def season_code_from_path(path):
    return os.path.basename(path).split("_")[0]

def standardize_file(path):
    rows = []
    code = season_code_from_path(path)
    season = SEASON_MAP.get(code, code)
    era = get_era(code)

    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)

        missing = [c for c in REQUIRED if c not in reader.fieldnames]
        if missing:
            print("[WARN] skip {} missing {}".format(os.path.basename(path), missing))
            return rows

        for r in reader:
            hg = safe_int(r.get("FTHG"))
            ag = safe_int(r.get("FTAG"))
            hs = safe_int(r.get("HS"))
            a_s = safe_int(r.get("AS"))
            hst = safe_int(r.get("HST"))
            ast = safe_int(r.get("AST"))

            if hg == "" or ag == "" or hs == "" or a_s == "":
                continue

            tg = hg + ag
            ts = hs + a_s
            tst = "" if hst == "" or ast == "" else hst + ast

            hf = safe_int(r.get("HF"))
            af = safe_int(r.get("AF"))
            hc = safe_int(r.get("HC"))
            ac = safe_int(r.get("AC"))
            hy = safe_int(r.get("HY"))
            ay = safe_int(r.get("AY"))
            hr = safe_int(r.get("HR"))
            ar = safe_int(r.get("AR"))

            result = r.get("FTR", "")
            div = r.get("Div", "")

            rows.append({
                "source": "football-data.co.uk",
                "season_code": code,
                "season": season,
                "era": era,
                "league": LEAGUE_NAMES.get(div, div),
                "date": r.get("Date", ""),
                "home_team": r.get("HomeTeam", ""),
                "away_team": r.get("AwayTeam", ""),
                "home_goals": hg,
                "away_goals": ag,
                "result": result,
                "total_goals": tg,
                "home_shots": hs,
                "away_shots": a_s,
                "total_shots": ts,
                "home_shots_on_target": hst,
                "away_shots_on_target": ast,
                "total_shots_on_target": tst,
                "home_fouls": hf,
                "away_fouls": af,
                "total_fouls": "" if hf == "" or af == "" else hf + af,
                "home_corners": hc,
                "away_corners": ac,
                "total_corners": "" if hc == "" or ac == "" else hc + ac,
                "home_yellow": hy,
                "away_yellow": ay,
                "total_yellow": "" if hy == "" or ay == "" else hy + ay,
                "home_red": hr,
                "away_red": ar,
                "total_red": "" if hr == "" or ar == "" else hr + ar,
                "low_scoring_1_or_less": 1 if tg <= 1 else 0,
                "low_scoring_2_or_less": 1 if tg <= 2 else 0,
                "high_scoring_4_or_more": 1 if tg >= 4 else 0,
                "draw_flag": 1 if result == "D" else 0,
                "home_win_flag": 1 if result == "H" else 0,
                "away_win_flag": 1 if result == "A" else 0,
                "shot_conversion_rate": safe_rate(tg, ts),
                "shot_on_target_rate": safe_rate(tst, ts),
            })

    print("[OK] {} -> {} rows".format(os.path.basename(path), len(rows)))
    return rows

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    files = sorted(glob.glob(os.path.join(IN_DIR, "*.csv")))

    all_rows = []
    for path in files:
        all_rows.extend(standardize_file(path))

    with open(OUT_FILE, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=OUT_COLS)
        writer.writeheader()
        writer.writerows(all_rows)

    print("[DONE] standardized football-data matches")
    print("[FILES] {}".format(len(files)))
    print("[ROWS] {}".format(len(all_rows)))
    print("[OUT] {}".format(OUT_FILE))

if __name__ == "__main__":
    main()
