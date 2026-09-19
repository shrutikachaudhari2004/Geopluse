import pandas as pd
import numpy as np

# ==========================================
# GeoPulse - GPS Data Generator
# ==========================================

NUM_RECORDS = 10000
NUM_DEVICES = 1000

# Pune simulated area
MIN_LAT = 18.45
MAX_LAT = 18.65

MIN_LON = 73.75
MAX_LON = 73.95

# Date and time range
START_DATE = "2026-09-18 06:00:00"
END_DATE = "2026-09-18 23:00:00"

# ==========================================
# Random seed
# ==========================================

np.random.seed(42)

# ==========================================
# Device IDs
# ==========================================

device_ids = [
    f"DEV{i:03d}"
    for i in range(1, NUM_DEVICES + 1)
]

# ==========================================
# Generate device IDs
# ==========================================

devices = np.random.choice(
    device_ids,
    size=NUM_RECORDS
)

# ==========================================
# Generate latitude
# ==========================================

latitudes = np.random.uniform(
    MIN_LAT,
    MAX_LAT,
    NUM_RECORDS
)

# ==========================================
# Generate longitude
# ==========================================

longitudes = np.random.uniform(
    MIN_LON,
    MAX_LON,
    NUM_RECORDS
)

# ==========================================
# Generate timestamps
# ==========================================

date_range = pd.date_range(
    start=START_DATE,
    end=END_DATE,
    freq="1min"
)

timestamps = np.random.choice(
    date_range,
    size=NUM_RECORDS
)

# ==========================================
# Create DataFrame
# ==========================================

df = pd.DataFrame({
    "device_id": devices,
    "latitude": latitudes.round(6),
    "longitude": longitudes.round(6),
    "timestamp": timestamps
})

# ==========================================
# Sort by timestamp
# ==========================================

df = df.sort_values(
    "timestamp"
).reset_index(drop=True)

# ==========================================
# Remove duplicates
# ==========================================

df = df.drop_duplicates()

# ==========================================
# Validation
# ==========================================

print("========================================")
print("GeoPulse GPS Dataset Validation")
print("========================================")

print("Total Records:", len(df))

print(
    "Latitude Valid:",
    df["latitude"].between(-90, 90).all()
)

print(
    "Longitude Valid:",
    df["longitude"].between(-180, 180).all()
)

print(
    "Missing Device IDs:",
    df["device_id"].isna().sum()
)

print(
    "Missing Timestamps:",
    df["timestamp"].isna().sum()
)

print(
    "Duplicate Rows:",
    df.duplicated().sum()
)

# ==========================================
# Save CSV
# ==========================================

output_path = "data/raw/gps_pings.csv"

df.to_csv(
    output_path,
    index=False
)

# ==========================================
# Final message
# ==========================================

print("========================================")
print("GPS dataset generated successfully!")
print("File:", output_path)
print("Records:", len(df))
print("========================================")