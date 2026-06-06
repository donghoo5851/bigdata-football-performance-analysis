#!/usr/bin/env bash
set -e

PROJECT_HOME="$HOME/football_project"
HDFS_BASE="/user/maria_dev/football_project"

echo "=================================================="
echo "[1/8] Move to project directory"
echo "=================================================="
cd "$PROJECT_HOME"

mkdir -p data/raw
mkdir -p data/processed
mkdir -p data/csv
mkdir -p results/tables
mkdir -p results/figures

echo "=================================================="
echo "[2/8] Download football-data.co.uk match data"
echo "=================================================="
if [ -d "data/raw/football_data_matches" ] && [ "$(find data/raw/football_data_matches -name '*.csv' | wc -l)" -gt 0 ]; then
    echo "[SKIP] football-data raw CSV files already exist."
else
    bash src/ingest/download_football_data_matches.sh
fi

echo "=================================================="
echo "[3/8] Download Kaggle datasets if needed"
echo "=================================================="

mkdir -p data/raw/understat
if [ -f "data/raw/understat/game_stats.csv" ]; then
    echo "[SKIP] Understat data already exists."
else
    kaggle datasets download -d codytipton/understat-data -p data/raw/understat -o
    unzip -o data/raw/understat/*.zip -d data/raw/understat
fi

mkdir -p data/raw/football_events
if [ -f "data/raw/football_events/events.csv" ] && [ -f "data/raw/football_events/ginf.csv" ]; then
    echo "[SKIP] football-events data already exists."
else
    kaggle datasets download -d secareanualin/football-events -p data/raw/football_events -o
    unzip -o data/raw/football_events/*.zip -d data/raw/football_events
fi

echo "=================================================="
echo "[4/8] Standardize football-data match data"
echo "=================================================="
python3.6 src/ingest/standardize_football_data_matches.py

echo "=================================================="
echo "[5/8] Upload data to HDFS"
echo "=================================================="
hdfs dfs -mkdir -p "$HDFS_BASE/raw/football_data_matches"
hdfs dfs -mkdir -p "$HDFS_BASE/raw/football_events"
hdfs dfs -mkdir -p "$HDFS_BASE/processed"
hdfs dfs -mkdir -p "$HDFS_BASE/result"

hdfs dfs -put -f data/raw/football_data_matches/*.csv "$HDFS_BASE/raw/football_data_matches/" || true
hdfs dfs -put -f data/raw/football_events/events.csv "$HDFS_BASE/raw/football_events/"
hdfs dfs -put -f data/raw/football_events/ginf.csv "$HDFS_BASE/raw/football_events/"
hdfs dfs -put -f data/processed/football_data_matches_standardized.csv "$HDFS_BASE/processed/"

echo "=================================================="
echo "[6/8] Run Spark analyses"
echo "=================================================="
spark-submit src/pipeline/analyze_match_dynamics_spark.py
spark-submit src/pipeline/analyze_football_events_spark.py

echo "=================================================="
echo "[7/8] Merge Spark outputs to local result tables"
echo "=================================================="

rm -f results/tables/season_summary.csv
rm -f results/tables/period_summary.csv
rm -f results/tables/league_summary.csv
rm -f results/tables/event_season_summary.csv
rm -f results/tables/event_league_summary.csv

hdfs dfs -getmerge "$HDFS_BASE/result/season_summary" results/tables/season_summary.csv
hdfs dfs -getmerge "$HDFS_BASE/result/period_summary" results/tables/period_summary.csv
hdfs dfs -getmerge "$HDFS_BASE/result/league_summary" results/tables/league_summary.csv
hdfs dfs -getmerge "$HDFS_BASE/result/event_season_summary" results/tables/event_season_summary.csv
hdfs dfs -getmerge "$HDFS_BASE/result/event_league_summary" results/tables/event_league_summary.csv

echo "=================================================="
echo "[8/8] Run additional analyses and visualizations"
echo "=================================================="

python3.6 src/analyze/change_point_analysis.py
python3.6 src/analyze/league_metric_change_by_split.py
python3.6 src/analyze/understat_xg_analysis.py
python3.6 src/analyze/big_match_analysis.py

python3.6 src/analyze/visualize_final_figures.py
python3.6 src/analyze/visualize_understat_xg.py
python3.6 src/analyze/visualize_big_match.py

echo "=================================================="
echo "[DONE] Full pipeline completed."
echo "=================================================="

echo "[LOCAL RESULTS]"
ls -lh results/tables | head
ls -lh results/figures | head

echo "[HDFS SIZE]"
hdfs dfs -du -h -s "$HDFS_BASE" || true
