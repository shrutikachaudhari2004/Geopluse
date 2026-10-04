from pathlib import Path
import pandas as pd

# ==================================================
# GeoPulse - Day 17 Final Project Report
# ==================================================

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"

print("=" * 60)
print("GeoPulse - Day 17 Final Project Report")
print("=" * 60)


# --------------------------------------------------
# Helper function
# --------------------------------------------------

def load_csv(filename):
    path = PROCESSED_DIR / filename

    if path.exists():
        return pd.read_csv(path)

    print(f"WARNING: {filename} not found")
    return None


# --------------------------------------------------
# 1. Project Summary
# --------------------------------------------------

summary = load_csv("day16_project_summary.csv")

if summary is not None:

    print("\nPROJECT SUMMARY")
    print("-" * 40)

    for _, row in summary.iterrows():
        print(f"{row['metric']}: {row['value']}")


# --------------------------------------------------
# 2. Peak Hour
# --------------------------------------------------

peak = load_csv("day16_peak_hour.csv")

peak_hour = None
peak_pings = None

if peak is not None:

    print("\nPEAK HOUR")
    print("-" * 40)

    print(peak.to_string(index=False))

    if len(peak) >= 2:
        peak_hour = peak.iloc[0]["value"]
        peak_pings = peak.iloc[1]["value"]


# --------------------------------------------------
# 3. Zone Ranking
# --------------------------------------------------

zones = load_csv("day16_zone_ranking.csv")

top_zone_name = None
top_zone_value = None

if zones is not None and len(zones) > 0:

    print("\nTOP ZONES")
    print("-" * 40)

    print(zones.head(10).to_string(index=False))

    first_row = zones.iloc[0]

    if "zone_name" in zones.columns:
        top_zone_name = first_row["zone_name"]

    elif "zone_id" in zones.columns:
        top_zone_name = first_row["zone_id"]

    for col in [
        "total_gps_pings",
        "gps_pings",
        "total_pings",
        "footfall"
    ]:
        if col in zones.columns:
            top_zone_value = first_row[col]
            break


# --------------------------------------------------
# 4. Store Summary
# --------------------------------------------------

store_summary = load_csv("day16_store_summary.csv")

total_stores = None

if store_summary is not None:

    print("\nSTORE SUMMARY")
    print("-" * 40)

    print(store_summary.to_string(index=False))

    for _, row in store_summary.iterrows():

        if str(row["metric"]).lower() == "total stores":
            total_stores = row["value"]


# --------------------------------------------------
# 5. Generate Business Insights
# --------------------------------------------------

insights = []

insights.append(
    "GeoPulse analyzes simulated GPS device activity "
    "for hyper-local retail mobility analysis."
)

if summary is not None:

    total_pings = None
    unique_devices = None

    for _, row in summary.iterrows():

        metric = str(row["metric"]).lower()

        if metric == "total gps pings":
            total_pings = row["value"]

        elif metric == "unique devices":
            unique_devices = row["value"]

    if total_pings is not None:
        insights.append(
            f"The dataset contains {total_pings} recorded GPS pings."
        )

    if unique_devices is not None:
        insights.append(
            f"The dataset contains activity from "
            f"{unique_devices} unique devices."
        )


if peak_hour is not None:

    insights.append(
        f"Peak recorded GPS activity occurs around "
        f"{peak_hour}:00."
    )


if top_zone_name is not None:

    insights.append(
        f"{top_zone_name} is the highest-ranked zone "
        f"based on recorded GPS activity."
    )


if total_stores is not None:

    insights.append(
        f"The project currently contains "
        f"{total_stores} stores."
    )


insights.append(
    "GPS pings represent recorded device activity and "
    "should not be interpreted as confirmed store visits."
)

insights.append(
    "The dataset does not identify actual customer identities."
)


# --------------------------------------------------
# 6. Save Business Insights
# --------------------------------------------------

insight_df = pd.DataFrame({
    "insight_number": range(1, len(insights) + 1),
    "business_insight": insights
})

output_file = PROCESSED_DIR / "day17_business_insights.csv"

insight_df.to_csv(
    output_file,
    index=False
)


# --------------------------------------------------
# 7. Project Health Report
# --------------------------------------------------

important_files = [
    "day16_project_summary.csv",
    "day16_hourly_activity.csv",
    "day16_daily_activity.csv",
    "day16_daywise_activity.csv",
    "day16_zone_ranking.csv",
    "day16_peak_hour.csv",
    "day15_data_quality_report.csv"
]

health_rows = []

for filename in important_files:

    path = PROCESSED_DIR / filename

    health_rows.append({
        "file": filename,
        "status": "AVAILABLE" if path.exists() else "MISSING"
    })


health_df = pd.DataFrame(health_rows)

health_file = PROCESSED_DIR / "day17_project_health.csv"

health_df.to_csv(
    health_file,
    index=False
)


# --------------------------------------------------
# Final Output
# --------------------------------------------------

print("\nBUSINESS INSIGHTS")
print("-" * 40)

for number, insight in enumerate(insights, start=1):
    print(f"{number}. {insight}")


print("\nPROJECT HEALTH")
print("-" * 40)

print(health_df.to_string(index=False))


print("\n" + "=" * 60)
print("Day 17 completed successfully.")
print("=" * 60)

print(f"\nBusiness insights saved to:")
print(output_file)

print(f"\nProject health report saved to:")
print(health_file)