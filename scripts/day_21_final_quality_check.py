
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
STORE_DIR = BASE_DIR / "data" / "stores"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# Important project files to validate
files_to_check = [
    ("Raw GPS", RAW_DIR / "gps_pings.csv"),
    ("Zones", RAW_DIR / "zones.csv"),
    ("Stores", STORE_DIR / "stores.csv"),
    ("Cleaned GPS", PROCESSED_DIR / "gps_pings_clean.csv"),
    ("Hourly GPS Summary", PROCESSED_DIR / "hourly_gps_summary.csv"),
    ("Zone Footfall", PROCESSED_DIR / "pyspark_zone_footfall.csv"),
    ("Day 17 Business Insights", PROCESSED_DIR / "day17_business_insights.csv"),
    ("Day 17 Project Health", PROCESSED_DIR / "day17_project_health.csv"),
    ("Day 18 Validation", PROCESSED_DIR / "day18_final_validation_report.csv"),
    ("Day 18 Checklist", PROCESSED_DIR / "day18_project_checklist.csv"),
    ("Day 20 Summary", PROCESSED_DIR / "day20_final_project_summary.csv"),
    ("Dashboard", BASE_DIR / "dashboard" / "app.py"),
    ("Dashboard Requirements", BASE_DIR / "dashboard" / "requirements.txt"),
    ("README", BASE_DIR / "README.md"),
]

results = []

for label, path in files_to_check:
    if not path.exists():
        results.append({
            "item": label,
            "status": "MISSING",
            "rows": 0,
            "details": str(path.relative_to(BASE_DIR))
        })
        continue

    # Python source files and documentation are checked for existence.
    if path.suffix != ".csv":
        results.append({
            "item": label,
            "status": "AVAILABLE",
            "rows": "-",
            "details": str(path.relative_to(BASE_DIR))
        })
        continue

    try:
        df = pd.read_csv(path)

        results.append({
            "item": label,
            "status": "AVAILABLE" if not df.empty else "EMPTY",
            "rows": len(df),
            "details": str(path.relative_to(BASE_DIR))
        })

    except Exception as error:
        results.append({
            "item": label,
            "status": "ERROR",
            "rows": 0,
            "details": str(error)[:150]
        })

report = pd.DataFrame(results)

output_file = PROCESSED_DIR / "day21_final_quality_report.csv"
report.to_csv(output_file, index=False)

print("\n===== GEOPULSE DAY 21 QUALITY REPORT =====")
print(report.to_string(index=False))

passed = report["status"].eq("AVAILABLE").sum()
attention = len(report) - passed

print(f"\nItems checked: {len(report)}")
print(f"Available: {passed}")
print(f"Needs attention: {attention}")
print(f"Report saved to: {output_file}")

if attention == 0:
    print("STATUS: All checked items are available and CSV files are non-empty.")
else:
    print("STATUS: Review MISSING, EMPTY, or ERROR items.")
