import pandas as pd

FILE = "data/processed/gps_with_zones.csv"

df = pd.read_csv(FILE)

device_analysis = (
    df.groupby("zone_id")
      .agg(
          total_pings=("device_id", "count"),
          unique_devices=("device_id", "nunique")
      )
      .reset_index()
      .sort_values("unique_devices", ascending=False)
)

print("===== Zone Device Analysis =====")
print(device_analysis)

device_analysis.to_csv(
    "data/processed/zone_device_analysis.csv",
    index=False
)

print("\nSaved:")
print("data/processed/zone_device_analysis.csv")
