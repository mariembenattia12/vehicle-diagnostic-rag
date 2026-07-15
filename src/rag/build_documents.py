import pandas as pd
import json


def chunk_text(text, max_length=800, overlap=100):
    text = str(text)
    if len(text) <= max_length:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = start + max_length
        chunks.append(text[start:end])
        start = end - overlap
    return chunks


def add_document(documents, doc_id, text, metadata):
    chunks = chunk_text(text)
    for i, chunk in enumerate(chunks):
        documents.append({
            "id": f"{doc_id}_{i}" if len(chunks) > 1 else doc_id,
            "text": chunk,
            "metadata": metadata,
        })


documents = []

# 1. Codes DTC
df_dtc = pd.read_csv("data/processed/dtc_p0_codes.csv").fillna("")
for idx, row in df_dtc.iterrows():
    text = f"Code défaut {row['dtc_code']}: {row['dtc_description']}"
    add_document(documents, f"dtc_{idx}_{row['dtc_code']}", text, {
        "source": "dtc",
        "dtc_code": str(row["dtc_code"]),
    })

# 2. Plaintes NHTSA (moteur/motorisation)
df_complaints = pd.read_csv("data/processed/nhtsa_complaints_engine.csv").fillna("")
for idx, row in df_complaints.iterrows():
    text = f"Plainte {row['make']} {row['model']} {row['year']} - Composants: {row['components']}. Description: {row['summary']}"
    add_document(documents, f"complaint_{idx}_{row['odi_number']}", text, {
        "source": "complaint",
        "make": str(row["make"]),
        "model": str(row["model"]),
        "year": str(row["year"]),
        "components": str(row["components"]),
    })

# 3. Rappels NHTSA (moteur/motorisation)
df_recalls = pd.read_csv("data/processed/nhtsa_recalls_engine.csv").fillna("")
for idx, row in df_recalls.iterrows():
    text = (
        f"Rappel {row['make']} {row['model']} {row['year']} - Composant: {row['component']}. "
        f"Problème: {row['summary']} Conséquence: {row['consequence']} Solution: {row['remedy']}"
    )
    add_document(documents, f"recall_{idx}_{row['campaign_number']}", text, {

        "source": "recall",
        "make": str(row["make"]),
        "model": str(row["model"]),
        "year": str(row["year"]),
        "component": str(row["component"]),
    })

print(f"Total chunks générés : {len(documents)}")

with open("data/processed/documents.json", "w", encoding="utf-8") as f:
    json.dump(documents, f, ensure_ascii=False, indent=2)