from pyspark.sql import SparkSession
from pyspark.sql.functions import col

spark = (
    SparkSession.builder
    .appName("GeoPulse Zone Processing")
    .master("local[*]")
    .getOrCreate()
)

zones = spark.read.option("header", True).option("inferSchema", True).csv(
    "data/raw/zones.csv"
)

print("===== Commercial Zones =====")

zones.printSchema()

print("Total zones:", zones.count())

zones.show(10, truncate=False)

zones.write.mode("overwrite").option("header", True).csv(
    "data/processed/spark_zones"
)

print("Zone processing completed.")

spark.stop()