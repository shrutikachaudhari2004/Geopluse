
import pandas as pd
from pathlib import Path
from math import radians, sin, cos, asin, sqrt
from itertools import combinations

# GeoPulse project paths
GPS_FILE = "data/raw/gps_pings.csv"
STORES_FILE = "data/stores/stores.csv"
OUTPUT_DIR = Path("data/processed")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Distance threshold for a potential store visit
RADIUS_KM = 2.0


def haversine_km(lat1, lon1, lat2, lon2):
    """Calculate distance between two GPS coordinates in kilometres."""
    lat1, lon1, lat2, lon2 = map(
        radians, [lat1, lon1, lat2, lon2]
    )

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        sin(dlat / 2) ** 2
        + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    )

    return 6371 * 2 * asin(sqrt(min(1, a)))


print("===== GeoPulse Day 9 =====")
print("Loading GPS and store data...")

gps = pd.read_csv(GPS_FILE)
stores = pd.read_csv(STORES_FILE)

gps["timestamp"] = pd.to_datetime(gps["timestamp"], errors="coerce")

gps = gps.dropna(
    subset=["device_id", "latitude", "longitude", "timestamp"]
)

print("GPS records:", len(gps))
print("Stores:", len(stores))

# Check for invalid coordinates
gps = gps[
    gps["latitude"].between(-90, 90)
    & gps["longitude"].between(-180, 180)
]

stores = stores.dropna(
    subset=["store_id", "store_name", "latitude", "longitude"]
)

# Calculate distance from every GPS ping to each store
matches = []

for _, store in stores.iterrows():
    distances = gps.apply(
        lambda row: haversine_km(
            row["latitude"],
            row["longitude"],
            store["latitude"],
            store["longitude"]
        ),
        axis=1
    )

    nearby = gps.loc[distances <= RADIUS_KM].copy()
    nearby["store_id"] = store["store_id"]
    nearby["store_name"] = store["store_name"]
    nearby["distance_km"] = distances[distances <= RADIUS_KM].values

    matches.append(nearby)

# Combine GPS pings within the radius of each store
if matches:
    store_matches = pd.concat(matches, ignore_index=True)
else:
    store_matches = pd.DataFrame()

if store_matches.empty:
    print("\nNo GPS pings found within the selected radius.")
    print("Try increasing RADIUS_KM if appropriate.")

    store_visits = pd.DataFrame(columns=[
        "store_id", "store_name", "total_pings", "unique_devices"
    ])
    overlap_pairs = pd.DataFrame(columns=[
        "store_1", "store_2", "shared_devices", "overlap_rate_pct"
    ])
else:
    # Store-level activity
    store_visits = (
        store_matches.groupby(["store_id", "store_name"])
        .agg(
            total_pings=("device_id", "size"),
            unique_devices=("device_id", "nunique")
        )
        .reset_index()
        .sort_values("unique_devices", ascending=False)
    )

    # Distinct devices observed near each store
    device_sets = {
        store_id: set(group["device_id"].unique())
        for store_id, group in store_matches.groupby("store_id")
    }

    store_names = stores.set_index("store_id")["store_name"].to_dict()

    # Compare each pair of stores
    rows = []

    for store_a, store_b in combinations(device_sets.keys(), 2):
        shared = device_sets[store_a] & device_sets[store_b]

        size_a = len(device_sets[store_a])
        size_b = len(device_sets[store_b])

        # Shared devices as a percentage of the smaller store's audience
        overlap_rate = (
            len(shared) / min(size_a, size_b) * 100
            if min(size_a, size_b) > 0 else 0
        )

        rows.append({
            "store_1": store_names[store_a],
            "store_2": store_names[store_b],
            "shared_devices": len(shared),
            "overlap_rate_pct": round(overlap_rate, 2)
        })

    overlap_pairs = pd.DataFrame(rows)

    if not overlap_pairs.empty:
        overlap_pairs = overlap_pairs.sort_values(
            ["shared_devices", "overlap_rate_pct"],
            ascending=False
        )

# Save reports
store_matches.to_csv(
    OUTPUT_DIR / "store_gps_matches.csv", index=False
)
store_visits.to_csv(
    OUTPUT_DIR / "store_visits.csv", index=False
)
overlap_pairs.to_csv(
    OUTPUT_DIR / "store_overlap_pairs.csv", index=False
)

print("\n===== Store Visits =====")
print(store_visits.to_string(index=False))

print("\n===== Top Store Overlap Pairs =====")
print(overlap_pairs.head(10).to_string(index=False))

print("\nReports saved in:", OUTPUT_DIR)
print("1. store_gps_matches.csv")
print("2. store_visits.csv")
print("3. store_overlap_pairs.csv")
print("\nDay 9 analysis completed.")