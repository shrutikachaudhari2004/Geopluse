
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PROCESSED = ROOT / "data" / "processed"
PROCESSED.mkdir(parents=True, exist_ok=True)


def load_csv(filename):
    path = PROCESSED / filename

    if not path.exists():
        raise FileNotFoundError(
            f"Missing file: {path}. Run Day 12 processing first."
        )

    df = pd.read_csv(path)
    df.columns = df.columns.str.strip().str.lower()
    return df


# 1. Load Day 12 outputs
gps = load_csv("gps_pings_clean.csv")
hourly = load_csv("hourly_gps_summary.csv")
zones = load_csv("pyspark_zone_footfall.csv")

# 2. Data quality report
gps["latitude"] = pd.to_numeric(gps["latitude"], errors="coerce")
gps["longitude"] = pd.to_numeric(gps["longitude"], errors="coerce")

timestamp_col = (
    "event_timestamp"
    if "event_timestamp" in gps.columns
    else "timestamp"
)
gps[timestamp_col] = pd.to_datetime(
    gps[timestamp_col], errors="coerce"
)

quality = pd.DataFrame([
    {
        "check": "total_records",
        "result": len(gps)
    },
    {
        "check": "missing_device_id",
        "result": int(gps["device_id"].isna().sum())
    },
    {
        "check": "missing_timestamp",
        "result": int(gps[timestamp_col].isna().sum())
    },
    {
        "check": "invalid_latitude",
        "result": int((~gps["latitude"].between(-90, 90)).sum())
    },
    {
        "check": "invalid_longitude",
        "result": int((~gps["longitude"].between(-180, 180)).sum())
    },
    {
        "check": "duplicate_records",
        "result": int(
            gps.duplicated(
                ["device_id", "latitude", "longitude", timestamp_col]
            ).sum()
        )
    }
])

quality.to_csv(
    PROCESSED / "day13_data_quality_report.csv",
    index=False
)

# 3. Rank zones by GPS activity
required_zone_columns = {
    "zone_name", "total_gps_pings", "unique_devices"
}

if not required_zone_columns.issubset(zones.columns):
    raise ValueError(
        f"Zone file needs these columns: {required_zone_columns}"
    )

zones["total_gps_pings"] = pd.to_numeric(
    zones["total_gps_pings"], errors="coerce"
).fillna(0)

zones["unique_devices"] = pd.to_numeric(
    zones["unique_devices"], errors="coerce"
).fillna(0)

zones = zones.sort_values(
    "total_gps_pings", ascending=False
).reset_index(drop=True)

zones["footfall_rank"] = zones.index + 1
zones["footfall_category"] = zones["total_gps_pings"].apply(
    lambda value: "High" if value > 0 else "No recorded activity"
)

zones.to_csv(
    PROCESSED / "day13_zone_ranking.csv",
    index=False
)

# 4. Rank hours by GPS activity
hourly["total_gps_pings"] = pd.to_numeric(
    hourly["total_gps_pings"], errors="coerce"
).fillna(0)

hourly["event_hour"] = pd.to_numeric(
    hourly["event_hour"], errors="coerce"
)

peak_hours = (
    hourly.groupby("event_hour", as_index=False)
    .agg(
        total_gps_pings=("total_gps_pings", "sum"),
        active_periods=("event_date", "nunique")
    )
    .sort_values("total_gps_pings", ascending=False)
)

peak_hours.to_csv(
    PROCESSED / "day13_peak_hour_analysis.csv",
    index=False
)

# 5. Print summary
print("\n--- GeoPulse Day 13 Summary ---")
print("GPS records analysed:", len(gps))

print("\nData quality report:")
print(quality.to_string(index=False))

print("\nTop 5 zones by GPS activity:")
print(
    zones[
        ["zone_name", "total_gps_pings",
         "unique_devices", "footfall_rank"]
    ].head(5).to_string(index=False)
)

print("\nTop 5 hours by GPS activity:")
print(peak_hours.head(5).to_string(index=False))

print("\nDay 13 output files saved in:", PROCESSED)