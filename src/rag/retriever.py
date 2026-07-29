import re
import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import CrossEncoder

embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection(
    name="vehicle_diagnostic",
    embedding_function=embedding_fn,
)

reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

DTC_PATTERN = re.compile(r"P0\d{3}", re.IGNORECASE)


def retrieve(query, n_results=5, candidates=15):
    results = collection.query(query_texts=[query], n_results=candidates)
    documents = list(results["documents"][0])
    metadatas = list(results["metadatas"][0])
    distances = list(results["distances"][0])

    match = DTC_PATTERN.search(query)
    if match:
        code = match.group(0).upper()
        exact = collection.get(where={"dtc_code": code})
        for doc, meta in zip(exact["documents"], exact["metadatas"]):
            if doc not in documents:
                documents.insert(0, doc)
                metadatas.insert(0, meta)
                distances.insert(0, 0.0)

    if not documents:
        return []

    pairs = [[query, doc] for doc in documents]
    scores = reranker.predict(pairs)

    reranked = sorted(
        zip(documents, metadatas, distances, scores),
        key=lambda x: x[3],
        reverse=True,
    )

    top = reranked[:n_results]
    return [(doc, meta, dist) for doc, meta, dist, score in top]