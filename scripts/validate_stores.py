import pandas as pd

file_path = "data/stores/stores.csv"

df = pd.read_csv(file_path)

print("Number of stores:", len(df))

print("\nStore data:")
print(df)

print("\nMissing values:")
print(df.isnull().sum())

print("\nDuplicate rows:", df.duplicated().sum())

print("\nLatitude valid:",
      df["latitude"].between(-90, 90).all())

print("Longitude valid:",
      df["longitude"].between(-180, 180).all())