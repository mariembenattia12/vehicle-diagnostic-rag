import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "rag"))

from dotenv import load_dotenv
load_dotenv()

from pipeline import rag_query, DISCLAIMER
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import Faithfulness, AnswerRelevancy, ContextPrecision, ContextRecall
from ragas.run_config import RunConfig
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings

TEST_SET = [
    {
        "question": "Qu'est-ce que le code P0100 ?",
        "ground_truth": "Le code P0100 indique un dysfonctionnement du circuit du debitmetre d'air (Mass or Volume Air Flow Circuit Malfunction).",
    },
    {
        "question": "Que signifie le code P0101 ?",
        "ground_truth": "Le code P0101 indique un probleme de plage ou de performance du circuit du debitmetre d'air.",
    },
    {
        "question": "Qu'est-ce que le code P0171 ?",
        "ground_truth": "Le code P0171 indique un melange air/carburant trop pauvre sur la banque 1 (Fuel Trim Malfunction, Bank 1).",
    },
    {
        "question": "Y a-t-il eu des rappels sur les airbags Honda Civic ?",
        "ground_truth": "Oui, il y a eu des rappels concernant les airbags Takata sur certains modeles Honda Civic, notamment 2016 et 2017.",
    },
    {
        "question": "Que signifie le code P0102 ?",
        "ground_truth": "Le code P0102 indique une entree basse du circuit du debitmetre d'air.",
    },
    {
        "question": "Qu'est-ce que le code P0110 ?",
        "ground_truth": "Le code P0110 indique un dysfonctionnement du circuit de temperature d'air d'admission.",
    },
]

print("Execution du pipeline RAG sur le jeu de test...")
rows = []
for item in TEST_SET:
    full_answer, retrieved, _ = rag_query(item["question"])
    answer_only = full_answer.split(DISCLAIMER)[0].strip()
    contexts = [doc for doc, meta, dist in retrieved]
    rows.append({
        "user_input": item["question"],
        "response": answer_only,
        "retrieved_contexts": contexts,
        "reference": item["ground_truth"],
    })
    print(f"  - {item['question']}")

dataset = Dataset.from_list(rows)

print("\nConfiguration du juge (Groq) et des embeddings...")
judge_llm = LangchainLLMWrapper(ChatGroq(model="llama-3.1-8b-instant", temperature=0))
judge_embeddings = LangchainEmbeddingsWrapper(
    HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
)

metrics = [
    Faithfulness(llm=judge_llm),
    AnswerRelevancy(llm=judge_llm, embeddings=judge_embeddings, strictness=1),
    ContextPrecision(llm=judge_llm),
    ContextRecall(llm=judge_llm),
]

run_config = RunConfig(timeout=120, max_workers=2)

print("Calcul des metriques RAGAS (peut prendre 3-5 minutes, execution ralentie volontairement)...")
result = evaluate(
    dataset,
    metrics=metrics,
    run_config=run_config,
)

df = result.to_pandas()
cols = ["user_input", "faithfulness", "answer_relevancy", "context_precision", "context_recall"]
print("\n", df[cols])

os.makedirs("docs", exist_ok=True)
df.to_csv("data/processed/ragas_results.csv", index=False)

summary = df[["faithfulness", "answer_relevancy", "context_precision", "context_recall"]].mean()
with open("docs/evaluation_ragas.md", "w", encoding="utf-8") as f:
    f.write("# Evaluation RAGAS\n\n")
    f.write(f"Jeu de test : {len(TEST_SET)} questions\n\n")
    f.write("## Scores moyens\n\n")
    f.write("| Metrique | Score |\n|---|---|\n")
    for name, val in summary.items():
        f.write(f"| {name} | {val:.2f} |\n")

print("\nResultats sauvegardes dans docs/evaluation_ragas.md et data/processed/ragas_results.csv")