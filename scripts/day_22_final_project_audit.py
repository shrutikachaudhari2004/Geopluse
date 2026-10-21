
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

checks = [
    ("Raw GPS", BASE_DIR / "data/raw/gps_pings.csv"),
    ("Zones", BASE_DIR / "data/raw/zones.csv"),
    ("Stores", BASE_DIR / "data/stores/stores.csv"),
    ("Cleaned GPS", PROCESSED_DIR / "gps_pings_clean.csv"),
    ("Hourly GPS Summary", PROCESSED_DIR / "hourly_gps_summary.csv"),
    ("Zone Footfall", PROCESSED_DIR / "pyspark_zone_footfall.csv"),
    ("Day 17 Business Insights", PROCESSED_DIR / "day17_business_insights.csv"),
    ("Day 18 Validation", PROCESSED_DIR / "day18_final_validation_report.csv"),
    ("Day 19 Documentation", PROCESSED_DIR / "day19_documentation_status.csv"),
    ("Day 20 Summary", PROCESSED_DIR / "day20_final_project_summary.csv"),
    ("Day 21 Quality Report", PROCESSED_DIR / "day21_final_quality_report.csv"),
    ("Dashboard", BASE_DIR / "dashboard/app.py"),
    ("Requirements", BASE_DIR / "dashboard/requirements.txt"),
    ("README", BASE_DIR / "README.md"),
]

results = []

for name, path in checks:
    relative_path = str(path.relative_to(BASE_DIR))

    if not path.exists():
        status, rows, details = "MISSING", 0, "File not found"

    elif path.suffix.lower() == ".csv":
        try:
            df = pd.read_csv(path)
            rows = len(df)

            if df.empty:
                status, details = "EMPTY", "CSV has no data rows"
            else:
                status, details = "AVAILABLE", "CSV readable"

        except Exception as error:
            status, rows = "ERROR", 0
            details = str(error)[:120]

    else:
        status, rows, details = "AVAILABLE", "-", "File exists"

    results.append({
        "item": name,
        "status": status,
        "rows": rows,
        "path": relative_path,
        "details": details,
    })

report = pd.DataFrame(results)
output_file = PROCESSED_DIR / "day22_final_project_audit.csv"
report.to_csv(output_file, index=False)

print("\n===== GEOPULSE DAY 22 PROJECT AUDIT =====")
print(report.to_string(index=False))

passed = report["status"].eq("AVAILABLE").sum()
attention = len(report) - passed

print(f"\nItems checked: {len(report)}")
print(f"Available: {passed}")
print(f"Needs attention: {attention}")
print(f"Audit saved to: {output_file}")

if attention == 0:
    print("STATUS: All checked items are available.")
else:
    print("STATUS: Review MISSING, EMPTY, or ERROR items.")
