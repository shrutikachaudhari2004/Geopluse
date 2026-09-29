import pandas as pd

FILE = "data/processed/gps_with_zones.csv"

df = pd.read_csv(FILE)

df["timestamp"] = pd.to_datetime(df["timestamp"])

df["hour"] = df["timestamp"].dt.hour

hourly = (
    df.groupby(["zone_id", "hour"])
      .size()
      .reset_index(name="footfall")
      .sort_values(["zone_id", "hour"])
)

print("===== Hourly Footfall =====")
print(hourly.head(20))

hourly.to_csv(
    "data/processed/hourly_footfall.csv",
    index=False
)

print("\nSaved:")
print("data/processed/hourly_footfall.csv")