import pandas as pd

file_path = "data/raw/zones.csv"

df = pd.read_csv(file_path)

print("Number of zones:", len(df))

print("\nZone data:")
print(df)

print("\nMissing values:")
print(df.isnull().sum())

print("\nDuplicate rows:", df.duplicated().sum())

print("\nLatitude validation:")
print(
    df["min_lat"].between(-90, 90).all()
    and df["max_lat"].between(-90, 90).all()
)

print("\nLongitude validation:")
print(
    df["min_lon"].between(-180, 180).all()
    and df["max_lon"].between(-180, 180).all()
)

print("\nLatitude range validation:")
print((df["min_lat"] < df["max_lat"]).all())

print("\nLongitude range validation:")
print((df["min_lon"] < df["max_lon"]).all())