from pathlib import Path
import pandas as pd

# --------------------------------------------------
# GeoPulse - Day 16 Final Analytics
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_GPS = BASE_DIR / "data" / "raw" / "gps_pings.csv"
STORES = BASE_DIR / "data" / "stores" / "stores.csv"
ZONES = BASE_DIR / "data" / "raw" / "zones.csv"

CLEAN_GPS = BASE_DIR / "data" / "processed" / "gps_pings_clean.csv"
ZONE_FOOTFALL = BASE_DIR / "data" / "processed" / "pyspark_zone_footfall.csv"

OUTPUT_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def find_existing_file(primary, fallback=None):
    if primary.exists():
        return primary

    if fallback and fallback.exists():
        return fallback

    return None


# --------------------------------------------------
# 1. Load GPS data
# --------------------------------------------------

gps_file = find_existing_file(CLEAN_GPS, RAW_GPS)

if gps_file is None:
    raise FileNotFoundError("GPS data file not found.")

gps = pd.read_csv(gps_file)

print("GPS file:", gps_file)
print("GPS rows:", len(gps))


# --------------------------------------------------
# 2. Standardize column names
# --------------------------------------------------

gps.columns = [
    str(col).strip().lower().replace(" ", "_")
    for col in gps.columns
]

if "timestamp" in gps.columns:
    gps["timestamp"] = pd.to_datetime(
        gps["timestamp"],
        errors="coerce"
    )

elif "event_timestamp" in gps.columns:
    gps["event_timestamp"] = pd.to_datetime(
        gps["event_timestamp"],
        errors="coerce"
    )
    gps["timestamp"] = gps["event_timestamp"]

else:
    raise ValueError("Timestamp column not found.")


# --------------------------------------------------
# 3. Create time features
# --------------------------------------------------

gps["date"] = gps["timestamp"].dt.date
gps["hour"] = gps["timestamp"].dt.hour
gps["day_name"] = gps["timestamp"].dt.day_name()


# --------------------------------------------------
# 4. Overall project summary
# --------------------------------------------------

total_pings = len(gps)

unique_devices = (
    gps["device_id"].nunique()
    if "device_id" in gps.columns
    else 0
)

min_timestamp = gps["timestamp"].min()
max_timestamp = gps["timestamp"].max()

summary = pd.DataFrame({
    "metric": [
        "Total GPS Pings",
        "Unique Devices",
        "Start Timestamp",
        "End Timestamp",
    ],
    "value": [
        total_pings,
        unique_devices,
        min_timestamp,
        max_timestamp,
    ]
})

summary.to_csv(
    OUTPUT_DIR / "day16_project_summary.csv",
    index=False
)


# --------------------------------------------------
# 5. Hourly activity
# --------------------------------------------------

hourly = (
    gps.groupby("hour")
    .agg(
        gps_pings=("device_id", "size"),
        unique_devices=("device_id", "nunique")
    )
    .reset_index()
    .sort_values("hour")
)

hourly.to_csv(
    OUTPUT_DIR / "day16_hourly_activity.csv",
    index=False
)


# --------------------------------------------------
# 6. Daily activity
# --------------------------------------------------

daily = (
    gps.groupby("date")
    .agg(
        gps_pings=("device_id", "size"),
        unique_devices=("device_id", "nunique")
    )
    .reset_index()
)

daily.to_csv(
    OUTPUT_DIR / "day16_daily_activity.csv",
    index=False
)


# --------------------------------------------------
# 7. Day-wise activity
# --------------------------------------------------

daywise = (
    gps.groupby("day_name")
    .agg(
        gps_pings=("device_id", "size"),
        unique_devices=("device_id", "nunique")
    )
    .reset_index()
)

day_order = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
]

daywise["day_order"] = daywise["day_name"].apply(
    lambda x: day_order.index(x)
    if x in day_order else 99
)

daywise = (
    daywise
    .sort_values("day_order")
    .drop(columns="day_order")
)

daywise.to_csv(
    OUTPUT_DIR / "day16_daywise_activity.csv",
    index=False
)


# --------------------------------------------------
# 8. Load stores
# --------------------------------------------------

if STORES.exists():

    stores = pd.read_csv(STORES)

    stores.columns = [
        str(col).strip().lower().replace(" ", "_")
        for col in stores.columns
    ]

    store_summary = pd.DataFrame({
        "metric": [
            "Total Stores",
            "Unique Store Areas",
            "Store Types"
        ],
        "value": [
            len(stores),
            stores["area"].nunique()
            if "area" in stores.columns else 0,
            stores["store_type"].nunique()
            if "store_type" in stores.columns else 0
        ]
    })

    store_summary.to_csv(
        OUTPUT_DIR / "day16_store_summary.csv",
        index=False
    )

    if "area" in stores.columns:

        area_analysis = (
            stores.groupby("area")
            .size()
            .reset_index(name="store_count")
            .sort_values(
                "store_count",
                ascending=False
            )
        )

        area_analysis.to_csv(
            OUTPUT_DIR / "day16_store_area_analysis.csv",
            index=False
        )

else:
    print("Store file not found. Skipping store analysis.")


# --------------------------------------------------
# 9. Zone footfall analysis
# --------------------------------------------------

if ZONE_FOOTFALL.exists():

    zone = pd.read_csv(ZONE_FOOTFALL)

    zone.columns = [
        str(col).strip().lower().replace(" ", "_")
        for col in zone.columns
    ]

    print("\nZone columns:")
    print(zone.columns.tolist())

    possible_ping_columns = [
        "total_gps_pings",
        "gps_pings",
        "total_pings",
        "footfall"
    ]

    ping_column = None

    for col in possible_ping_columns:
        if col in zone.columns:
            ping_column = col
            break

    if ping_column:

        zone = zone.sort_values(
            ping_column,
            ascending=False
        )

        zone["rank"] = range(1, len(zone) + 1)

        zone.to_csv(
            OUTPUT_DIR / "day16_zone_ranking.csv",
            index=False
        )

        top_zone = zone.iloc[0]

        top_zone_report = pd.DataFrame({
            "metric": [
                "Top Zone",
                "Top Zone Footfall"
            ],
            "value": [
                top_zone.get("zone_name", top_zone.get("zone_id")),
                top_zone[ping_column]
            ]
        })

        top_zone_report.to_csv(
            OUTPUT_DIR / "day16_top_zone.csv",
            index=False
        )

    else:
        print("Footfall column not found in zone file.")

else:
    print("Zone footfall file not found.")


# --------------------------------------------------
# 10. Peak hour
# --------------------------------------------------

peak_hour_row = hourly.loc[
    hourly["gps_pings"].idxmax()
]

peak_hour_report = pd.DataFrame({
    "metric": [
        "Peak Hour",
        "Peak Hour GPS Pings"
    ],
    "value": [
        int(peak_hour_row["hour"]),
        int(peak_hour_row["gps_pings"])
    ]
})

peak_hour_report.to_csv(
    OUTPUT_DIR / "day16_peak_hour.csv",
    index=False
)


# --------------------------------------------------
# Final message
# --------------------------------------------------

print("\n" + "=" * 55)
print("GeoPulse Day 16 Final Analytics Completed")
print("=" * 55)

print(f"Total GPS Pings     : {total_pings}")
print(f"Unique Devices      : {unique_devices}")
print(f"Peak Hour           : {int(peak_hour_row['hour'])}:00")
print(f"Peak Hour GPS Pings : {int(peak_hour_row['gps_pings'])}")

print("\nOutput files created in:")
print(OUTPUT_DIR)