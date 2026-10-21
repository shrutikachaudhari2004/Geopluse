
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"

files_to_check = [
    "day16_project_summary.csv",
    "day16_hourly_activity.csv",
    "day16_zone_ranking.csv",
    "day16_peak_hour.csv",
    "day17_business_insights.csv",
    "day17_project_health.csv",
    "day18_final_validation_report.csv",
    "day18_project_checklist.csv",
    "day19_documentation_status.csv",
]

results = []

for filename in files_to_check:
    path = PROCESSED_DIR / filename

    if not path.exists():
        status, rows, columns = "MISSING", 0, 0
    else:
        try:
            df = pd.read_csv(path)
            status, rows, columns = "AVAILABLE", len(df), len(df.columns)
        except Exception:
            status, rows, columns = "ERROR", 0, 0

    results.append({
        "file_name": filename,
        "status": status,
        "rows": rows,
        "columns": columns,
    })

summary = pd.DataFrame(results)
output = PROCESSED_DIR / "day20_final_project_summary.csv"
summary.to_csv(output, index=False)

print("\nGEO PULSE - DAY 20 PROJECT SUMMARY")
print(summary.to_string(index=False))

available = summary["status"].eq("AVAILABLE").sum()
print(f"\nAvailable files: {available}/{len(summary)}")
print(f"Report saved to: {output}")

if available == len(summary):
    print("STATUS: All checked files are available.")
else:
    print("STATUS: Review missing or unreadable files.")
