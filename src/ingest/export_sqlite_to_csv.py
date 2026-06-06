#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3
import csv

DB_PATH = os.path.expanduser("~/football_project/data/raw/database.sqlite")
OUT_DIR = os.path.expanduser("~/football_project/data/csv")

TABLES = [
    "Country",
    "League",
    "Match",
    "Team",
    "Team_Attributes",
    "Player",
    "Player_Attributes",
]

def export_table(conn, table_name):
    out_path = os.path.join(OUT_DIR, "{}.csv".format(table_name))

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM {}".format(table_name))
    rows = cursor.fetchall()

    col_names = [desc[0] for desc in cursor.description]

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(col_names)
        writer.writerows(rows)

    print("[OK] {}: {} rows -> {}".format(table_name, len(rows), out_path))

def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    if not os.path.exists(DB_PATH):
        raise FileNotFoundError("Database not found: {}".format(DB_PATH))

    conn = sqlite3.connect(DB_PATH)

    try:
        for table in TABLES:
            export_table(conn, table)
    finally:
        conn.close()

    print("[DONE] SQLite tables exported to CSV.")

if __name__ == "__main__":
    main()
