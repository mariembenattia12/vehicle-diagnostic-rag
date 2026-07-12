import json
import glob
import pandas as pd
import os

records = []
for filepath in glob.glob("data/raw/nhtsa_complaints/*.json"):
    with open(filepath, encoding="utf-8") as f:
        data = json.load(f)

    for item in data.get("results", []):
        product = item.get("products", [{}])[0]
        records.append({
            "odi_number": item.get("odiNumber"),
            "make": product.get("productMake"),
            "model": product.get("productModel"),
            "year": product.get("productYear"),
            "components": item.get("components"),
            "summary": item.get("summary"),
            "crash": item.get("crash"),
            "fire": item.get("fire"),
            "date_complaint_filed": item.get("dateComplaintFiled"),
        })

df_complaints = pd.DataFrame(records)
print("Total plaintes :", len(df_complaints))

# Ne garder que les plaintes liées moteur/motorisation, cohérent avec le scope P0xxx
ENGINE_KEYWORDS = ["ENGINE", "FUEL SYSTEM", "TRANSMISSION", "POWER TRAIN", "EMISSION"]
mask = df_complaints["components"].str.contains("|".join(ENGINE_KEYWORDS), case=False, na=False)
df_engine = df_complaints[mask].copy()

print("Plaintes liées moteur/motorisation :", len(df_engine))

os.makedirs("data/processed", exist_ok=True)
df_complaints.to_csv("data/processed/nhtsa_complaints_all.csv", index=False)
df_engine.to_csv("data/processed/nhtsa_complaints_engine.csv", index=False)