from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_timestamp, hour

spark = (
    SparkSession.builder
    .appName("GeoPulse GPS Processing")
    .master("local[*]")
    .getOrCreate()
)

print("Starting GeoPulse GPS Processing...")

# Load GPS data
gps = spark.read.option("header", True).option("inferSchema", True).csv(
    "data/raw/gps_pings.csv"
)

print("\nGPS Schema:")
gps.printSchema()

print("\nTotal GPS records:")
print(gps.count())

# Convert timestamp
gps = gps.withColumn(
    "timestamp",
    to_timestamp(col("timestamp"))
)

# Extract hour
gps = gps.withColumn(
    "hour",
    hour(col("timestamp"))
)

print("\nSample GPS records:")
gps.show(10, truncate=False)

# Save processed Spark output
gps.write.mode("overwrite").option("header", True).csv(
    "data/processed/spark_gps"
)

print("\nSpark GPS processing completed.")

spark.stop()