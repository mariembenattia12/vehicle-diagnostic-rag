import json
import glob
import pandas as pd
import os

records = []
for filepath in glob.glob("data/raw/nhtsa_recalls/*.json"):
    with open(filepath, encoding="utf-8") as f:
        data = json.load(f)

    for item in data.get("results", []):
        records.append({
            "campaign_number": item.get("NHTSACampaignNumber"),
            "make": item.get("Make"),
            "model": item.get("Model"),
            "year": item.get("ModelYear"),
            "component": item.get("Component"),
            "summary": item.get("Summary"),
            "consequence": item.get("Consequence"),
            "remedy": item.get("Remedy"),
            "report_date": item.get("ReportReceivedDate"),
        })

df_recalls = pd.DataFrame(records)
print("Total rappels :", len(df_recalls))

# Même filtre moteur/motorisation que pour les plaintes, cohérent avec le scope P0xxx
ENGINE_KEYWORDS = ["ENGINE", "FUEL SYSTEM", "TRANSMISSION", "POWER TRAIN", "EMISSION"]
mask = df_recalls["component"].str.contains("|".join(ENGINE_KEYWORDS), case=False, na=False)
df_recalls_engine = df_recalls[mask].copy()
print("Rappels liés moteur/motorisation :", len(df_recalls_engine))

os.makedirs("data/processed", exist_ok=True)
df_recalls.to_csv("data/processed/nhtsa_recalls_clean.csv", index=False)
df_recalls_engine.to_csv("data/processed/nhtsa_recalls_engine.csv", index=False)