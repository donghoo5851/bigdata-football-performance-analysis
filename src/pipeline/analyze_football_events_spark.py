#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

EVENTS_PATH = "/user/maria_dev/football_project/raw/football_events/events.csv"
GINF_PATH = "/user/maria_dev/football_project/raw/football_events/ginf.csv"

OUT_SEASON = "/user/maria_dev/football_project/result/event_season_summary"
OUT_LEAGUE = "/user/maria_dev/football_project/result/event_league_summary"

def flag(condition):
    return F.when(condition, 1).otherwise(0)

def add_rate_columns(df):
    return (
        df
        .withColumn("events_per_match", F.round(F.col("event_count") / F.col("match_count"), 3))
        .withColumn("attempts_per_match", F.round(F.col("attempts") / F.col("match_count"), 3))
        .withColumn("key_passes_per_match", F.round(F.col("key_passes") / F.col("match_count"), 3))
        .withColumn("corners_per_match", F.round(F.col("corners") / F.col("match_count"), 3))
        .withColumn("fouls_per_match", F.round(F.col("fouls") / F.col("match_count"), 3))
        .withColumn("cards_per_match", F.round(F.col("cards") / F.col("match_count"), 3))
        .withColumn("fast_breaks_per_match", F.round(F.col("fast_breaks") / F.col("match_count"), 3))
        .withColumn("goals_per_match_from_events", F.round(F.col("goals") / F.col("match_count"), 3))
        .withColumn("key_pass_rate", F.round(F.col("key_passes") / F.col("event_count"), 5))
        .withColumn("attempt_rate", F.round(F.col("attempts") / F.col("event_count"), 5))
        .withColumn("fast_break_attempt_rate", F.round(F.col("fast_break_attempts") / F.col("attempts"), 5))
        .withColumn("box_attempt_rate", F.round(F.col("box_attempts") / F.col("attempts"), 5))
        .withColumn("on_target_rate", F.round(F.col("shots_on_target") / F.col("attempts"), 5))
    )

def main():
    spark = (
        SparkSession.builder
        .appName("FootballEventsAnalysis")
        .getOrCreate()
    )

    events = (
        spark.read
        .option("header", "true")
        .option("inferSchema", "true")
        .csv(EVENTS_PATH)
    )

    ginf = (
        spark.read
        .option("header", "true")
        .option("inferSchema", "true")
        .csv(GINF_PATH)
    )

    matches = (
        ginf
        .select("id_odsp", "country", "league", "season")
        .dropDuplicates(["id_odsp"])
    )

    joined = events.join(matches, on="id_odsp", how="inner")

    # shot locations inside/near box according to dictionary:
    # 3 Centre of box, 9/10 left box/six-yard, 11/12 right box/six-yard,
    # 13 very close range, 14 penalty spot
    box_locations = [3, 9, 10, 11, 12, 13, 14]

    event_features = (
        joined
        .withColumn("is_attempt", flag(F.col("event_type") == 1))
        .withColumn("is_corner", flag(F.col("event_type") == 2))
        .withColumn("is_foul", flag(F.col("event_type") == 3))
        .withColumn("is_card", flag(F.col("event_type").isin([4, 5, 6])))
        .withColumn("is_key_pass", flag(F.col("event_type2") == 12))
        .withColumn("is_failed_through_ball", flag(F.col("event_type2") == 13))
        .withColumn("is_fast_break", flag(F.col("fast_break") == 1))
        .withColumn("is_goal_event", flag(F.col("is_goal") == 1))
        .withColumn("is_shot_on_target", flag((F.col("event_type") == 1) & (F.col("shot_outcome") == 1)))
        .withColumn("is_box_attempt", flag((F.col("event_type") == 1) & (F.col("location").isin(box_locations))))
        .withColumn("is_fast_break_attempt", flag((F.col("event_type") == 1) & (F.col("fast_break") == 1)))
    )

    match_counts_season = (
        matches
        .groupBy("season")
        .agg(F.countDistinct("id_odsp").alias("match_count"))
    )

    season_summary = (
        event_features
        .groupBy("season")
        .agg(
            F.count("*").alias("event_count"),
            F.sum("is_attempt").alias("attempts"),
            F.sum("is_corner").alias("corners"),
            F.sum("is_foul").alias("fouls"),
            F.sum("is_card").alias("cards"),
            F.sum("is_key_pass").alias("key_passes"),
            F.sum("is_failed_through_ball").alias("failed_through_balls"),
            F.sum("is_fast_break").alias("fast_breaks"),
            F.sum("is_goal_event").alias("goals"),
            F.sum("is_shot_on_target").alias("shots_on_target"),
            F.sum("is_box_attempt").alias("box_attempts"),
            F.sum("is_fast_break_attempt").alias("fast_break_attempts")
        )
        .join(match_counts_season, on="season", how="inner")
        .orderBy("season")
    )

    season_summary = add_rate_columns(season_summary)

    match_counts_league = (
        matches
        .groupBy("season", "country", "league")
        .agg(F.countDistinct("id_odsp").alias("match_count"))
    )

    league_summary = (
        event_features
        .groupBy("season", "country", "league")
        .agg(
            F.count("*").alias("event_count"),
            F.sum("is_attempt").alias("attempts"),
            F.sum("is_corner").alias("corners"),
            F.sum("is_foul").alias("fouls"),
            F.sum("is_card").alias("cards"),
            F.sum("is_key_pass").alias("key_passes"),
            F.sum("is_failed_through_ball").alias("failed_through_balls"),
            F.sum("is_fast_break").alias("fast_breaks"),
            F.sum("is_goal_event").alias("goals"),
            F.sum("is_shot_on_target").alias("shots_on_target"),
            F.sum("is_box_attempt").alias("box_attempts"),
            F.sum("is_fast_break_attempt").alias("fast_break_attempts")
        )
        .join(match_counts_league, on=["season", "country", "league"], how="inner")
        .orderBy("season", "country", "league")
    )

    league_summary = add_rate_columns(league_summary)

    season_summary.coalesce(1).write.mode("overwrite").option("header", "true").csv(OUT_SEASON)
    league_summary.coalesce(1).write.mode("overwrite").option("header", "true").csv(OUT_LEAGUE)

    print("=== Event Season Summary ===")
    season_summary.show(20, truncate=False)

    print("=== Event League Summary Sample ===")
    league_summary.show(20, truncate=False)

    spark.stop()

if __name__ == "__main__":
    main()
