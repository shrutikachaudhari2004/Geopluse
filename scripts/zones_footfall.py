import pandas as pd

FILE = "data/processed/gps_with_zones.csv"

df = pd.read_csv(FILE)

# Count GPS pings by zone
zone_footfall = (
    df.groupby("zone_id")
      .size()
      .reset_index(name="footfall")
      .sort_values("footfall", ascending=False)
)

print("===== Zone Footfall =====")
print(zone_footfall)

zone_footfall.to_csv(
    "data/processed/zone_footfall.csv",
    index=False
)

print("\nSaved:")
print("data/processed/zone_footfall.csv")