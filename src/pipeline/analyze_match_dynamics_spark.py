#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

INPUT = "hdfs:///user/maria_dev/football_project/processed/football_data_matches_standardized.csv"
OUT = "hdfs:///user/maria_dev/football_project/result"

spark = SparkSession.builder.appName("FootballMatchDynamics").getOrCreate()
spark.sparkContext.setLogLevel("WARN")

df = spark.read.csv(INPUT, header=True, inferSchema=True)

# season_code 0809 -> 809   
df = df.withColumn(
    "season_code",
    F.lpad(F.col("season_code").cast("string"), 4, "0")
)

num_cols = [
    "total_goals",
    "total_shots",
    "total_shots_on_target",
    "total_fouls",
    "total_corners",
    "total_yellow",
    "total_red",
    "low_scoring_1_or_less",
    "low_scoring_2_or_less",
    "high_scoring_4_or_more",
    "draw_flag",
    "home_win_flag",
    "away_win_flag",
    "shot_conversion_rate",
    "shot_on_target_rate"
]

for c in num_cols:
    df = df.withColumn(c, F.col(c).cast("double"))

df = df.withColumn(
    "period_group",
    F.when(
        F.col("season_code").isin(
            "0809", "0910", "1011", "1112", "1213", "1314", "1415", "1516"
        ),
        "2008-2016"
    ).otherwise("2016-2025")
)

season_summary = df.groupBy("season_code", "season").agg(
    F.count("*").alias("match_count"),
    F.round(F.avg("total_goals"), 3).alias("avg_goals"),
    F.round(F.avg("total_shots"), 3).alias("avg_shots"),
    F.round(F.avg("total_shots_on_target"), 3).alias("avg_shots_on_target"),
    F.round(F.avg("shot_conversion_rate"), 4).alias("avg_shot_conversion"),
    F.round(F.avg("shot_on_target_rate"), 4).alias("avg_shot_on_target_rate"),
    F.round(F.avg("low_scoring_1_or_less"), 4).alias("low_score_1_rate"),
    F.round(F.avg("low_scoring_2_or_less"), 4).alias("low_score_2_rate"),
    F.round(F.avg("high_scoring_4_or_more"), 4).alias("high_score_4_rate"),
    F.round(F.avg("draw_flag"), 4).alias("draw_rate"),
    F.round(F.avg("home_win_flag"), 4).alias("home_win_rate"),
    F.round(F.avg("away_win_flag"), 4).alias("away_win_rate"),
    F.round(F.avg("total_fouls"), 3).alias("avg_fouls"),
    F.round(F.avg("total_yellow"), 3).alias("avg_yellow"),
    F.round(F.avg("total_red"), 3).alias("avg_red")
).orderBy("season_code")

league_summary = df.groupBy("season_code", "season", "league").agg(
    F.count("*").alias("match_count"),
    F.round(F.avg("total_goals"), 3).alias("avg_goals"),
    F.round(F.avg("total_shots"), 3).alias("avg_shots"),
    F.round(F.avg("total_shots_on_target"), 3).alias("avg_sot"),
    F.round(F.avg("low_scoring_2_or_less"), 4).alias("low_score_2_rate"),
    F.round(F.avg("draw_flag"), 4).alias("draw_rate"),
    F.round(F.avg("total_fouls"), 3).alias("avg_fouls"),
    F.round(F.avg("total_yellow"), 3).alias("avg_yellow")
).orderBy("season_code", "league")

period_summary = df.groupBy("period_group").agg(
    F.count("*").alias("match_count"),
    F.round(F.avg("total_goals"), 3).alias("avg_goals"),
    F.round(F.avg("total_shots"), 3).alias("avg_shots"),
    F.round(F.avg("total_shots_on_target"), 3).alias("avg_sot"),
    F.round(F.avg("shot_conversion_rate"), 4).alias("avg_shot_conversion"),
    F.round(F.avg("low_scoring_2_or_less"), 4).alias("low_score_2_rate"),
    F.round(F.avg("draw_flag"), 4).alias("draw_rate"),
    F.round(F.avg("home_win_flag"), 4).alias("home_win_rate"),
    F.round(F.avg("away_win_flag"), 4).alias("away_win_rate"),
    F.round(F.avg("total_fouls"), 3).alias("avg_fouls"),
    F.round(F.avg("total_yellow"), 3).alias("avg_yellow"),
    F.round(F.avg("total_red"), 3).alias("avg_red")
).orderBy("period_group")

season_summary.coalesce(1).write.mode("overwrite").option("header", True).csv(OUT + "/season_summary")
league_summary.coalesce(1).write.mode("overwrite").option("header", True).csv(OUT + "/league_summary")
period_summary.coalesce(1).write.mode("overwrite").option("header", True).csv(OUT + "/period_summary")

print("=== Season Summary ===")
season_summary.show(30, truncate=False)

print("=== Period Summary ===")
period_summary.show(10, truncate=False)

spark.stop()
