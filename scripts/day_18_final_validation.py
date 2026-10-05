from pathlib import Path
import pandas as pd

# ==================================================
# GeoPulse - Day 18 Final Project Validation
# ==================================================

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
STORES_DIR = BASE_DIR / "data" / "stores"

print("=" * 65)
print("GeoPulse - Day 18 Final Project Validation")
print("=" * 65)


# --------------------------------------------------
# 1. Important files
# --------------------------------------------------

important_files = [
    "data/raw/gps_pings.csv",
    "data/raw/zones.csv",
    "data/stores/stores.csv",
    "data/processed/gps_pings_clean.csv",
    "data/processed/hourly_gps_summary.csv",
    "data/processed/pyspark_zone_footfall.csv",
    "data/processed/day15_data_quality_report.csv",
    "data/processed/day16_project_summary.csv",
    "data/processed/day16_hourly_activity.csv",
    "data/processed/day16_zone_ranking.csv",
    "data/processed/day16_peak_hour.csv",
    "data/processed/day17_business_insights.csv",
    "data/processed/day17_project_health.csv",
    "dashboard/app.py",
    "dashboard/requirements.txt",
    "README.md",
]


validation = []

for relative_path in important_files:

    path = BASE_DIR / relative_path

    if path.exists():

        size_kb = round(path.stat().st_size / 1024, 2)

        validation.append({
            "file": relative_path,
            "status": "AVAILABLE",
            "size_kb": size_kb
        })

    else:

        validation.append({
            "file": relative_path,
            "status": "MISSING",
            "size_kb": 0
        })


validation_df = pd.DataFrame(validation)


# --------------------------------------------------
# 2. GPS data validation
# --------------------------------------------------

gps_file = RAW_DIR / "gps_pings.csv"

if gps_file.exists():

    gps = pd.read_csv(gps_file)

    print("\nGPS DATA")
    print("-" * 45)

    print("Rows:", len(gps))
    print("Columns:", list(gps.columns))

    if "device_id" in gps.columns:
        print("Unique devices:", gps["device_id"].nunique())

    missing = gps.isna().sum().sum()

    print("Missing values:", missing)

    duplicate_rows = gps.duplicated().sum()

    print("Duplicate rows:", duplicate_rows)


# --------------------------------------------------
# 3. Store validation
# --------------------------------------------------

stores_file = STORES_DIR / "stores.csv"

if stores_file.exists():

    stores = pd.read_csv(stores_file)

    print("\nSTORE DATA")
    print("-" * 45)

    print("Total stores:", len(stores))

    if "area" in stores.columns:
        print("Store areas:", stores["area"].nunique())

    if "store_type" in stores.columns:
        print("Store types:", stores["store_type"].nunique())


# --------------------------------------------------
# 4. Zone validation
# --------------------------------------------------

zones_file = RAW_DIR / "zones.csv"

if zones_file.exists():

    zones = pd.read_csv(zones_file)

    print("\nZONE DATA")
    print("-" * 45)

    print("Total zones:", len(zones))

    if "zone_type" in zones.columns:
        print("Zone types:", zones["zone_type"].nunique())


# --------------------------------------------------
# 5. Project status
# --------------------------------------------------

available_count = (
    validation_df["status"] == "AVAILABLE"
).sum()

missing_count = (
    validation_df["status"] == "MISSING"
).sum()


print("\nPROJECT FILE STATUS")
print("-" * 45)

print("Available files:", available_count)
print("Missing files:", missing_count)


# --------------------------------------------------
# 6. Save validation report
# --------------------------------------------------

output_file = (
    PROCESSED_DIR /
    "day18_final_validation_report.csv"
)

validation_df.to_csv(
    output_file,
    index=False
)


# --------------------------------------------------
# 7. Final project checklist
# --------------------------------------------------

checklist = [
    ("GPS dataset available", (RAW_DIR / "gps_pings.csv").exists()),
    ("Zones dataset available", (RAW_DIR / "zones.csv").exists()),
    ("Stores dataset available", (STORES_DIR / "stores.csv").exists()),
    ("Clean GPS dataset available",
     (PROCESSED_DIR / "gps_pings_clean.csv").exists()),
    ("PySpark output available",
     (PROCESSED_DIR / "pyspark_zone_footfall.csv").exists()),
    ("Data quality report available",
     (PROCESSED_DIR / "day15_data_quality_report.csv").exists()),
    ("Final analytics available",
     (PROCESSED_DIR / "day16_project_summary.csv").exists()),
    ("Business insights available",
     (PROCESSED_DIR / "day17_business_insights.csv").exists()),
    ("Dashboard available",
     (BASE_DIR / "dashboard" / "app.py").exists()),
    ("README available",
     (BASE_DIR / "README.md").exists()),
]


checklist_df = pd.DataFrame(
    checklist,
    columns=["check", "completed"]
)


checklist_file = (
    PROCESSED_DIR /
    "day18_project_checklist.csv"
)

checklist_df.to_csv(
    checklist_file,
    index=False
)


# --------------------------------------------------
# 8. Final result
# --------------------------------------------------

all_completed = checklist_df["completed"].all()

print("\nFINAL PROJECT CHECKLIST")
print("-" * 45)

print(checklist_df.to_string(index=False))

print("\n" + "=" * 65)

if all_completed:

    print("STATUS: PROJECT READY FOR FINAL REVIEW")

else:

    print("STATUS: SOME PROJECT ITEMS NEED ATTENTION")

print("=" * 65)

print("\nReports created:")
print(output_file)
print(checklist_file)