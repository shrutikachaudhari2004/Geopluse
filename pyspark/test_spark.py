from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("GeoPulse")
    .master("local[*]")
    .getOrCreate()
)

print("================================")
print("GeoPulse Spark Started")
print("Spark Version:", spark.version)
print("================================")

spark.stop()