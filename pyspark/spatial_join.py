from pyspark.sql import SparkSession
from pyspark.sql.functions import col

spark = (
    SparkSession.builder
    .appName("GeoPulse Spatial Join")
    .master("local[*]")
    .getOrCreate()
)

gps = spark.read.option("header", True).option("inferSchema", True).csv(
    "data/raw/gps_pings.csv"
)

zones = spark.read.option("header", True).option("inferSchema", True).csv(
    "data/raw/zones.csv"
)

print("GPS records:", gps.count())
print("Zones:", zones.count())

# Rename columns for clarity
g = gps.alias("g")
z = zones.alias("z")

# Point-in-rectangle spatial condition
condition = (
    (col("g.latitude") >= col("z.min_lat")) &
    (col("g.latitude") <= col("z.max_lat")) &
    (col("g.longitude") >= col("z.min_lon")) &
    (col("g.longitude") <= col("z.max_lon"))
)

spatial_result = (
    g.join(z, condition, "left")
     .select(
         col("g.device_id"),
         col("g.latitude"),
         col("g.longitude"),
         col("g.timestamp"),
         col("z.zone_id"),
         col("z.zone_name")
     )
)

print("\n===== Spatial Join Result =====")

spatial_result.show(20, truncate=False)

print("\nTotal matched rows:")
print(spatial_result.count())

spatial_result.write.mode("overwrite").option("header", True).csv(
    "data/processed/spatial_join"
)

print("\nSpatial join completed.")

spark.stop()