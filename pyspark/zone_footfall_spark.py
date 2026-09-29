from pyspark.sql import SparkSession
from pyspark.sql.functions import count, countDistinct, col

spark = (
    SparkSession.builder
    .appName("GeoPulse Zone Footfall")
    .master("local[*]")
    .getOrCreate()
)

df = spark.read.option("header", True).option("inferSchema", True).csv(
    "data/processed/spatial_join"
)

footfall = (
    df.filter(col("zone_id").isNotNull())
      .groupBy("zone_id", "zone_name")
      .agg(
          count("*").alias("total_pings"),
          countDistinct("device_id").alias("unique_devices")
      )
      .orderBy(col("total_pings").desc())
)

print("===== GeoPulse Zone Footfall =====")

footfall.show(20, truncate=False)

footfall.write.mode("overwrite").option("header", True).csv(
    "data/processed/spark_zone_footfall"
)

print("Zone footfall analysis completed.")

spark.stop()