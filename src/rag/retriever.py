import re
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

DTC_PATTERN = re.compile(r"P0\d{3}", re.IGNORECASE)


def retrieve(query, n_results=5):
    results = collection.query(query_texts=[query], n_results=n_results)
    documents = list(results["documents"][0])
    metadatas = list(results["metadatas"][0])

    # Si un code DTC est mentionné explicitement, on le recupere en priorite
    # par correspondance exacte, en plus de la recherche semantique.
    match = DTC_PATTERN.search(query)
    if match:
        code = match.group(0).upper()
        exact = collection.get(where={"dtc_code": code})
        for doc, meta in zip(exact["documents"], exact["metadatas"]):
            if doc not in documents:
                documents.insert(0, doc)
                metadatas.insert(0, meta)

    return list(zip(documents, metadatas))