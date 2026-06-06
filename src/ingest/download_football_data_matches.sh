#!/usr/bin/env bash

set -e

BASE_URL="https://www.football-data.co.uk/mmz4281"
OUT_DIR="$HOME/football_project/data/raw/football_data_matches"

mkdir -p "$OUT_DIR"

# 2008/09 ~ 2024/25
SEASONS=(
  "0809" "0910" "1011" "1112" "1213" "1314" "1415" "1516"
  "1617" "1718" "1819" "1920" "2021" "2122" "2223" "2324" "2425"
)

# Top 5 European leagues
LEAGUE_CODES=("E0" "SP1" "I1" "D1" "F1")

get_league_name() {
    case "$1" in
        "E0") echo "Premier_League" ;;
        "SP1") echo "La_Liga" ;;
        "I1") echo "Serie_A" ;;
        "D1") echo "Bundesliga" ;;
        "F1") echo "Ligue_1" ;;
        *) echo "$1" ;;
    esac
}

echo "[INFO] Downloading football-data.co.uk match statistics"
echo "[INFO] Seasons: 2008/09 ~ 2024/25"
echo "[INFO] Leagues: E0, SP1, I1, D1, F1"

for SEASON in "${SEASONS[@]}"; do
    for CODE in "${LEAGUE_CODES[@]}"; do
        NAME=$(get_league_name "$CODE")
        URL="${BASE_URL}/${SEASON}/${CODE}.csv"
        OUT_FILE="${OUT_DIR}/${SEASON}_${CODE}_${NAME}.csv"

        echo "[DOWNLOAD] ${URL}"

        #       
        if curl -L --fail -o "$OUT_FILE" "$URL"; then
            if [ -s "$OUT_FILE" ]; then
                echo "[OK] Saved to ${OUT_FILE}"
            else
                echo "[WARN] Empty file: ${OUT_FILE}"
                rm -f "$OUT_FILE"
            fi
        else
            echo "[WARN] Failed: ${URL}"
            rm -f "$OUT_FILE"
        fi

        sleep 1
    done
done

echo "[DONE] football-data.co.uk download completed."
echo "[INFO] Saved files:"
ls -lh "$OUT_DIR"
