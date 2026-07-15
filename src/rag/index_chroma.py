import json
import chromadb
from chromadb.utils import embedding_functions

with open("data/processed/documents.json", encoding="utf-8") as f:
    documents = json.load(f)

print(f"Documents à indexer : {len(documents)}")

embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(
    name="vehicle_diagnostic",
    embedding_function=embedding_fn,
)

batch_size = 200
for i in range(0, len(documents), batch_size):
    batch = documents[i:i + batch_size]
    collection.add(
        ids=[doc["id"] for doc in batch],
        documents=[doc["text"] for doc in batch],
        metadatas=[doc["metadata"] for doc in batch],
    )
    print(f"Indexé {min(i + batch_size, len(documents))}/{len(documents)}")

print("Terminé. Collection :", collection.count(), "documents")