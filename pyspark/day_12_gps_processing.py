
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, count, countDistinct, hour, to_timestamp,
    to_date, when
)

# Project paths
ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"

PROCESSED.mkdir(parents=True, exist_ok=True)

# Start Spark
spark = (
    SparkSession.builder
    .appName("GeoPulse-Day12")
    .master("local[*]")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("ERROR")

try:
    # 1. Load GPS data
    gps = (
        spark.read
        .option("header", True)
        .option("inferSchema", True)
        .csv(str(RAW / "gps_pings.csv"))
    )

    # Normalize column names
    gps = gps.toDF(*[c.strip().lower() for c in gps.columns])

    required = {"device_id", "latitude", "longitude", "timestamp"}
    if not required.issubset(set(gps.columns)):
        raise ValueError(
            f"Missing columns. Found: {gps.columns}"
        )

    # 2. Clean and convert columns
    gps = (
        gps.withColumn("device_id", col("device_id").cast("string"))
        .withColumn("latitude", col("latitude").cast("double"))
        .withColumn("longitude", col("longitude").cast("double"))
        .withColumn(
            "event_timestamp",
            to_timestamp(col("timestamp"))
        )
    )

    # 3. Remove missing and invalid coordinates
    gps_clean = (
        gps.filter(
            col("device_id").isNotNull()
            & col("event_timestamp").isNotNull()
            & col("latitude").between(-90, 90)
            & col("longitude").between(-180, 180)
        )
        .dropDuplicates(
            ["device_id", "latitude", "longitude", "event_timestamp"]
        )
        .withColumn("event_date", to_date("event_timestamp"))
        .withColumn("event_hour", hour("event_timestamp"))
    )

    # Save cleaned GPS records
    clean_path = PROCESSED / "gps_pings_clean.csv"
    gps_clean.select(
        "device_id", "latitude", "longitude",
        "event_timestamp", "event_date", "event_hour"
    ).toPandas().to_csv(clean_path, index=False)

    # 4. Hourly activity summary
    hourly = (
        gps_clean.groupBy("event_date", "event_hour")
        .agg(
            count("*").alias("total_gps_pings"),
            countDistinct("device_id").alias("unique_devices")
        )
        .orderBy("event_date", "event_hour")
    )

    hourly.toPandas().to_csv(
        PROCESSED / "hourly_gps_summary.csv",
        index=False
    )

    # 5. Zone-wise footfall
    zones = (
        spark.read
        .option("header", True)
        .option("inferSchema", True)
        .csv(str(RAW / "zones.csv"))
    )
    zones = zones.toDF(*[c.strip().lower() for c in zones.columns])

    zone_required = {
        "zone_id", "zone_name",
        "min_lat", "max_lat", "min_lon", "max_lon"
    }
    if not zone_required.issubset(set(zones.columns)):
        raise ValueError(f"Missing zone columns. Found: {zones.columns}")

    g = gps_clean.alias("g")
    z = zones.alias("z")

    matches = g.join(
        z,
        (col("g.latitude") >= col("z.min_lat"))
        & (col("g.latitude") <= col("z.max_lat"))
        & (col("g.longitude") >= col("z.min_lon"))
        & (col("g.longitude") <= col("z.max_lon")),
        "inner"
    )

    zone_footfall = (
        matches.groupBy(
            col("z.zone_id"), col("z.zone_name")
        )
        .agg(
            count("*").alias("total_gps_pings"),
            countDistinct("g.device_id").alias("unique_devices")
        )
        .orderBy(col("total_gps_pings").desc())
    )

    zone_footfall.toPandas().to_csv(
        PROCESSED / "pyspark_zone_footfall.csv",
        index=False
    )

    # 6. Print validation results
    print("\n--- GeoPulse Day 12 Results ---")
    print("Raw GPS records:", gps.count())
    print("Clean GPS records:", gps_clean.count())
    print("Hourly summary rows:", hourly.count())
    print("Zones loaded:", zones.count())

    print("\nTop zones by GPS activity:")
    zone_footfall.show(10, truncate=False)

    print("\nFiles saved in:", PROCESSED)

finally:
    spark.stop()