import requests
import os

url = "https://raw.githubusercontent.com/mytrile/obd-trouble-codes/master/obd-trouble-codes.csv"
os.makedirs("data/raw", exist_ok=True)

response = requests.get(url)
response.raise_for_status()

with open("data/raw/obd-trouble-codes.csv", "wb") as f:
    f.write(response.content)

print("Fichier téléchargé :", len(response.content), "octets")