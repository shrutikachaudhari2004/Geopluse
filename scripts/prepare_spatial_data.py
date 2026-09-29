import pandas as pd

GPS_FILE = "data/raw/gps_pings.csv"
ZONES_FILE = "data/raw/zones.csv"
OUTPUT_FILE = "data/processed/gps_with_zones.csv"

print("Loading GPS data...")
gps = pd.read_csv(GPS_FILE)

print("Loading zone data...")
zones = pd.read_csv(ZONES_FILE)

print("GPS records:", len(gps))
print("Zones:", len(zones))

# Create zone_id column
gps["zone_id"] = "UNKNOWN"

# Assign each GPS point to a zone
for _, zone in zones.iterrows():

    condition = (
        (gps["latitude"] >= zone["min_lat"]) &
        (gps["latitude"] <= zone["max_lat"]) &
        (gps["longitude"] >= zone["min_lon"]) &
        (gps["longitude"] <= zone["max_lon"])
    )

    gps.loc[condition, "zone_id"] = zone["zone_id"]

print("\nZone assignment completed.")

print("\nZone distribution:")
print(gps["zone_id"].value_counts())

gps.to_csv(OUTPUT_FILE, index=False)

print("\nSaved file:")
print(OUTPUT_FILE)

print("\nTotal records:", len(gps))