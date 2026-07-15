from retriever import retrieve
from prompt import build_prompt
from llm import generate_answer

DISCLAIMER = (
    "\n\nCeci est un outil pedagogique base sur des donnees publiques. "
    "Consultez un technicien automobile certifie pour un diagnostic reel."
)


def rag_query(question, n_results=5):
    retrieved = retrieve(question, n_results=n_results)
    system_prompt, user_prompt = build_prompt(question, retrieved)
    answer = generate_answer(system_prompt, user_prompt)

    return answer.strip() + DISCLAIMER, retrieved


if __name__ == "__main__":
    questions = [
        "Qu'est-ce que le code P0171 ?",
        "Ma voiture perd de la puissance et le voyant moteur est allume, que faire ?",
        "Y a-t-il eu des rappels sur les airbags Honda Civic ?",
    ]

    for q in questions:
        print(f"\n{'='*60}\nQuestion : {q}\n{'='*60}")
        answer, sources = rag_query(q, n_results=3)
        print(answer)
        print(f"\n(Base sur {len(sources)} sources recuperees)")