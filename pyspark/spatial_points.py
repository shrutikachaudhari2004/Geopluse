from pyspark.sql import SparkSession
from pyspark.sql.functions import col, concat, lit

spark = (
    SparkSession.builder
    .appName("GeoPulse Spatial Points")
    .master("local[*]")
    .getOrCreate()
)

gps = spark.read.option("header", True).option("inferSchema", True).csv(
    "data/raw/gps_pings.csv"
)

# Create WKT point
gps = gps.withColumn(
    "point_wkt",
    concat(
        lit("POINT("),
        col("longitude").cast("string"),
        lit(" "),
        col("latitude").cast("string"),
        lit(")")
    )
)

print("===== Spatial GPS Points =====")

gps.select(
    "device_id",
    "latitude",
    "longitude",
    "point_wkt",
    "timestamp"
).show(10, truncate=False)

gps.select(
    "device_id",
    "latitude",
    "longitude",
    "timestamp",
    "point_wkt"
).write.mode("overwrite").option("header", True).csv(
    "data/processed/gps_spatial"
)

print("Spatial point preparation completed.")

spark.stop()