import pandas as pd
import os

df = pd.read_csv(
    "data/raw/obd-trouble-codes.csv",
    header=None,
    names=["dtc_code", "dtc_description"]
)

print("Colonnes :", df.columns.tolist())
print("Nombre total de lignes :", len(df))
print(df.head(10))

df_p0 = df[df["dtc_code"].str.startswith("P0", na=False)].copy()
print(f"{len(df_p0)} codes P0xxx conservés sur {len(df)} au total")

os.makedirs("data/processed", exist_ok=True)
df_p0.to_csv("data/processed/dtc_p0_codes.csv", index=False)