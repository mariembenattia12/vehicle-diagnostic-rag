import chromadb
from chromadb.utils import embedding_functions

embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection(
    name="vehicle_diagnostic",
    embedding_function=embedding_fn,
)

queries = [
    "voyant moteur allumé perte de puissance",
    "probleme de capteur debit air",
    "rappel airbag qui explose",
]

for query in queries:
    print(f"\n=== Requête : {query} ===")
    results = collection.query(query_texts=[query], n_results=3)
    for doc, meta, dist in zip(
        results["documents"][0], results["metadatas"][0], results["distances"][0]
    ):
        print(f"[{meta.get('source')}] (distance={dist:.3f}) {doc[:150]}...")