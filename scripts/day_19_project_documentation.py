from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"

print("=" * 60)
print("GeoPulse - Day 19 Final Project Documentation")
print("=" * 60)

files_to_check = [
    "day18_final_validation_report.csv",
    "day18_project_checklist.csv",
    "day17_business_insights.csv",
    "day17_project_health.csv",
    "day16_project_summary.csv",
    "day16_hourly_activity.csv",
    "day16_zone_ranking.csv",
    "day16_peak_hour.csv",
]

results = []

for filename in files_to_check:

    file_path = PROCESSED_DIR / filename

    if file_path.exists():

        try:
            df = pd.read_csv(file_path)

            results.append({
                "file_name": filename,
                "status": "AVAILABLE",
                "rows": len(df),
                "columns": len(df.columns)
            })

            print(f"PASS: {filename}")

        except Exception as e:

            results.append({
                "file_name": filename,
                "status": "ERROR",
                "rows": 0,
                "columns": 0
            })

            print(f"ERROR: {filename} -> {e}")

    else:

        results.append({
            "file_name": filename,
            "status": "MISSING",
            "rows": 0,
            "columns": 0
        })

        print(f"MISSING: {filename}")


documentation_df = pd.DataFrame(results)

output_file = PROCESSED_DIR / "day19_documentation_status.csv"

documentation_df.to_csv(
    output_file,
    index=False
)

print()
print("=" * 60)
print("Day 19 Documentation Status")
print("=" * 60)

print(documentation_df)

print()
print(f"Output created: {output_file}")
print()
print("Day 19 documentation validation completed.")