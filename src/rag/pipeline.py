import re
from retriever import retrieve
from prompt import build_prompt
from llm import generate_answer

DISCLAIMER = (
    "Ceci est un outil pedagogique base sur des donnees publiques. "
    "Consultez un technicien automobile certifie pour un diagnostic reel."
)

CODE_RE = re.compile(r"\b([PBCU][0-9]{4})\b", re.IGNORECASE)


def extract_dtc_code(retrieved):
    for doc, meta, dist in retrieved:
        if meta.get("source") == "dtc" and meta.get("dtc_code"):
            return meta["dtc_code"].upper()
    return None


def extract_causes(retrieved, max_causes=3):
    causes = []
    seen = set()
    for doc, meta, dist in retrieved:
        source = meta.get("source")
        if source == "dtc":
            label = doc.split(":", 1)[-1].strip()
        elif source == "complaint":
            label = meta.get("components", "").split(",")[0].strip().title()
        elif source == "recall":
            label = meta.get("component", "").split(",")[0].strip().title()
        else:
            label = None

        if label and label not in seen:
            seen.add(label)
            causes.append(label)
        if len(causes) >= max_causes:
            break
    return causes


def compute_confidence(retrieved):
    if not retrieved:
        return "basse"
    min_distance = min(dist for _, _, dist in retrieved)
    if min_distance < 0.5:
        return "haute"
    elif min_distance < 0.9:
        return "moyenne"
    return "basse"


def build_sources(retrieved, max_sources=3):
    sources = []
    for doc, meta, dist in retrieved[:max_sources]:
        sources.append({
            "source_type": meta.get("source", "inconnu"),
            "reference": meta.get("dtc_code") or meta.get("component") or "n/a",
            "excerpt": doc[:150],
        })
    return sources


def rag_query(question, n_results=5):
    retrieved = retrieve(question, n_results=n_results)
    doc_meta_pairs = [(doc, meta) for doc, meta, _ in retrieved]
    system_prompt, user_prompt = build_prompt(question, doc_meta_pairs)
    answer = generate_answer(system_prompt, user_prompt)

    structured = {
        "dtc_code": extract_dtc_code(retrieved),
        "causes_probables": extract_causes(retrieved),
        "confidence": compute_confidence(retrieved),
        "sources": build_sources(retrieved),
    }

    full_answer = answer.strip() + "\n\n" + DISCLAIMER
    return full_answer, retrieved, structured


if __name__ == "__main__":
    questions = [
        "Qu'est-ce que le code P0171 ?",
        "Ma voiture perd de la puissance et le voyant moteur est allume, que faire ?",
        "Y a-t-il eu des rappels sur les airbags Honda Civic ?",
    ]

    for q in questions:
        print(f"\n{'='*60}\nQuestion : {q}\n{'='*60}")
        answer, sources, structured = rag_query(q)
        print(answer)
        print("\nStructure :", structured)