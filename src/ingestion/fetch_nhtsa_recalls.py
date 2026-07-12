import requests
import json
import time
import os

MAKES_MODELS = [
    ("toyota", "corolla"),
    ("honda", "civic"),
    ("ford", "focus"),
    ("nissan", "sentra"),
    ("volkswagen", "golf"),
]
YEARS = [2015, 2016, 2017, 2018, 2019]

os.makedirs("data/raw/nhtsa_recalls", exist_ok=True)

for make, model in MAKES_MODELS:
    for year in YEARS:
        url = "https://api.nhtsa.gov/recalls/recallsByVehicle"
        params = {"make": make, "model": model, "modelYear": year}
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.HTTPError:
            print(f"{make} {model} {year} -> ignoré (combinaison invalide)")
            continue

        filename = f"data/raw/nhtsa_recalls/{make}_{model}_{year}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"{make} {model} {year} -> {data.get('Count', 0)} rappels")
        time.sleep(0.5)