
-- Hive SQL validation analysis for football match dynamics
-- This script creates an external table over the standardized football-data CSV
-- stored in HDFS and summarizes match dynamics by era.
-- Main aggregation is performed by Spark, and this HiveQL script provides
-- an additional SQL-based validation using the same HDFS data.

DROP TABLE IF EXISTS hive_era_summary;
DROP TABLE IF EXISTS football_matches_standardized;

CREATE EXTERNAL TABLE football_matches_standardized (
    source STRING,
    season_code STRING,
    season STRING,
    era STRING,
    league STRING,
    match_date STRING,
    home_team STRING,
    away_team STRING,
    home_goals DOUBLE,
    away_goals DOUBLE,
    result STRING,
    total_goals DOUBLE,
    home_shots DOUBLE,
    away_shots DOUBLE,
    total_shots DOUBLE,
    home_shots_on_target DOUBLE,
    away_shots_on_target DOUBLE,
    total_shots_on_target DOUBLE,
    home_fouls DOUBLE,
    away_fouls DOUBLE,
    total_fouls DOUBLE,
    home_corners DOUBLE,
    away_corners DOUBLE,
    total_corners DOUBLE,
    home_yellow DOUBLE,
    away_yellow DOUBLE,
    total_yellow DOUBLE,
    home_red DOUBLE,
    away_red DOUBLE,
    total_red DOUBLE,
    low_scoring_1_or_less INT,
    low_scoring_2_or_less INT,
    high_scoring_4_or_more INT,
    draw_flag INT,
    home_win_flag INT,
    away_win_flag INT,
    shot_conversion_rate DOUBLE,
    shot_on_target_rate DOUBLE
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/user/maria_dev/football_project/processed/football_data_matches_hive'
TBLPROPERTIES ("skip.header.line.count"="1");

CREATE TABLE hive_era_summary AS
SELECT
    era,
    COUNT(*) AS match_count,
    ROUND(AVG(total_goals), 4) AS avg_goals,
    ROUND(AVG(total_shots), 4) AS avg_shots,
    ROUND(AVG(total_shots_on_target), 4) AS avg_shots_on_target,
    ROUND(AVG(shot_conversion_rate), 5) AS avg_shot_conversion,
    ROUND(AVG(low_scoring_2_or_less), 5) AS low_score_2_rate,
    ROUND(AVG(high_scoring_4_or_more), 5) AS high_score_4_rate,
    ROUND(AVG(home_win_flag), 5) AS home_win_rate,
    ROUND(AVG(away_win_flag), 5) AS away_win_rate,
    ROUND(AVG(draw_flag), 5) AS draw_rate
FROM football_matches_standardized
GROUP BY era;

SELECT * FROM hive_era_summary ORDER BY era;
