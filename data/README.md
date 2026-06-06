# Data Directory

This directory contains small sample files only.

Large raw datasets are not committed to GitHub because of file size.  
The full datasets are downloaded and processed by `scripts/run_pipeline.sh`.

## Data sources

| Dataset | Source | Role |
|---|---|---|
| football-data.co.uk Match Statistics | football-data.co.uk | Main long-term match statistics analysis |
| Kaggle Understat Data | Kaggle | xG-based attacking quality analysis |
| Kaggle football-events | Kaggle | Large-scale event data analysis with HDFS and Spark |
| Kaggle European Soccer Database | Kaggle | SQLite-to-CSV conversion and HDFS loading practice |

## Sample files

| File | Description |
|---|---|
| `sample/football_data_matches_sample.csv` | Sample from standardized football-data match statistics |
| `sample/understat_game_stats_sample.csv` | Sample from Understat game-level xG data |
| `sample/football_events_sample.csv` | Sample from Kaggle football-events event data |
| `sample/football_events_games_sample.csv` | Sample from Kaggle football-events game metadata |

## Raw data policy

Raw data files are excluded from GitHub using `.gitignore`.

The full data size used in this project includes:
- Kaggle football-events `events.csv`: about 173MB
- Kaggle football-events total folder: about 196MB
- football-data.co.uk match statistics
- Kaggle Understat data
- Kaggle European Soccer Database

The large datasets are stored locally and in HDFS during execution.
