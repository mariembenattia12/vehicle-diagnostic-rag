import json

with open("data/raw/nhtsa_complaints/toyota_corolla_2017.json", encoding="utf-8") as f:
    data = json.load(f)

print(data["results"][0].keys())
print(data["results"][0])