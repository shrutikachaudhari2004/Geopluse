
from pathlib import Path
import pandas as pd

# GeoPulse project root
BASE_DIR = Path(__file__).resolve().parent.parent

FILES = [
    "data/raw/gps_pings.csv",
    "data/raw/zones.csv",
    "data/stores/stores.csv",
    "data/processed/gps_pings_clean.csv",
    "data/processed/hourly_gps_summary.csv",
    "data/processed/pyspark_zone_footfall.csv",
]

reports = []

def validate_file(relative_path):
    file_path = BASE_DIR / relative_path

    if not file_path.exists():
        reports.append({
            "file": relative_path,
            "status": "FILE NOT FOUND",
            "rows": 0,
            "columns": 0,
            "missing_values": 0,
            "duplicate_rows": 0,
            "invalid_coordinates": 0,
        })
        print(f"⚠️ File not found: {relative_path}")
        return

    try:
        df = pd.read_csv(file_path)

        missing_values = int(df.isna().sum().sum())
        duplicate_rows = int(df.duplicated().sum())
        invalid_coordinates = 0

        # Check latitude and longitude where available
        if {"latitude", "longitude"}.issubset(df.columns):
            lat = pd.to_numeric(df["latitude"], errors="coerce")
            lon = pd.to_numeric(df["longitude"], errors="coerce")

            invalid = (
                lat.isna()
                | lon.isna()
                | ~lat.between(-90, 90)
                | ~lon.between(-180, 180)
            )
            invalid_coordinates = int(invalid.sum())

        reports.append({
            "file": relative_path,
            "status": "CHECKED",
            "rows": len(df),
            "columns": len(df.columns),
            "missing_values": missing_values,
            "duplicate_rows": duplicate_rows,
            "invalid_coordinates": invalid_coordinates,
        })

        print(f"\nFile: {relative_path}")
        print(f"Rows: {len(df)}")
        print(f"Columns: {len(df.columns)}")
        print(f"Missing values: {missing_values}")
        print(f"Duplicate rows: {duplicate_rows}")
        print(f"Invalid coordinates: {invalid_coordinates}")

    except Exception as error:
        reports.append({
            "file": relative_path,
            "status": f"ERROR: {error}",
            "rows": 0,
            "columns": 0,
            "missing_values": 0,
            "duplicate_rows": 0,
            "invalid_coordinates": 0,
        })
        print(f"❌ Error reading {relative_path}: {error}")


def main():
    for file in FILES:
        validate_file(file)

    output_dir = BASE_DIR / "data" / "processed"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "day15_data_quality_report.csv"
    pd.DataFrame(reports).to_csv(output_file, index=False)

    print("\n" + "=" * 45)
    print("Day 15 data validation completed.")
    print(f"Report saved to: {output_file}")


if __name__ == "__main__":
    main()