#!/usr/bin/env bash

set -e

BASE_URL="https://www.football-data.co.uk/mmz4281"
OUT_DIR="$HOME/football_project/data/raw/modern_matches"

mkdir -p "$OUT_DIR"

# 2024/2025 season code
SEASON="2425"

# Top 5 European leagues
declare -A LEAGUES
LEAGUES["E0"]="Premier_League"
LEAGUES["SP1"]="La_Liga"
LEAGUES["I1"]="Serie_A"
LEAGUES["D1"]="Bundesliga"
LEAGUES["F1"]="Ligue_1"

echo "[INFO] Downloading modern match data from football-data.co.uk"
echo "[INFO] Season: 2024/2025"

for CODE in "${!LEAGUES[@]}"; do
    NAME="${LEAGUES[$CODE]}"
    URL="${BASE_URL}/${SEASON}/${CODE}.csv"
    OUT_FILE="${OUT_DIR}/${SEASON}_${CODE}_${NAME}.csv"

    echo "[DOWNLOAD] $URL"
    curl -L -o "$OUT_FILE" "$URL"

    if [ ! -s "$OUT_FILE" ]; then
        echo "[ERROR] Downloaded file is empty: $OUT_FILE"
        exit 1
    fi

    echo "[OK] Saved to $OUT_FILE"
done

echo "[DONE] Modern match data download completed."
