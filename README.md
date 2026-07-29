# vehicle-diagnostic-rag
# Assistant de diagnostic véhicule (RAG)

Assistant conversationnel d'aide au diagnostic automobile, combinant recherche augmentée par génération (RAG), reranking par cross-encoder et données publiques (codes DTC, plaintes et rappels NHTSA).

Projet réalisé dans le cadre de la préparation d'un stage de fin d'études (PFE) en systèmes embarqués et Edge AI, avec un intérêt particulier pour les activités de diagnostic et maintenance automobile.

## Aperçu

L'utilisateur pose une question en langage naturel (texte ou voix) sur un code défaut, un symptôme ou un rappel constructeur. Le système :

1. Récupère les documents les plus pertinents dans une base vectorielle (ChromaDB)
2. Reclasse ces résultats avec un cross-encoder pour affiner la pertinence
3. Génère une réponse fondée uniquement sur ce contexte, avec citation du code DTC concerné
4. Retourne une réponse structurée (code, causes probables, niveau de confiance, sources)

## Stack technique

**Données** : NHTSA Complaints/Recalls API (domaine public), base de codes DTC (SAE J1979/J2012, codes P0xxx)

**Backend** : FastAPI · ChromaDB · sentence-transformers (`all-MiniLM-L6-v2`) · cross-encoder (`ms-marco-MiniLM-L-6-v2`) · LLM interchangeable (Ollama en local / Groq en API) · faster-whisper (entrée vocale)

**Frontend** : React (Vite) · design personnalisé · mise en évidence automatique des codes DTC

**Évaluation** : RAGAS (faithfulness, answer relevancy, context precision, context recall)

**Déploiement** : Docker (build multi-stage, frontend + backend dans un seul conteneur)

## Fonctionnalités

- Chat avec historique de session
- Reconnaissance vocale des questions
- Sortie structurée (code DTC, causes probables, niveau de confiance, sources citées)
- Mise en évidence visuelle des codes défaut dans les réponses
- Bascule LLM local (Ollama, gratuit, hors-ligne) / LLM cloud (Groq, rapide)
- Reranking par cross-encoder pour améliorer la pertinence du retrieval
- Conteneurisation Docker complète

## Résultats d'évaluation (RAGAS)

Comparaison avant/après ajout du reranking par cross-encoder, sur un jeu de test de 6 questions :

| Métrique | Sans reranking | Avec reranking |
|---|---|---|
| Faithfulness | 0.81 | **0.93** |
| Answer relevancy | 0.63 | **0.78** |
| Context precision | 0.86 | **0.89** |
| Context recall | 1.00 | 1.00 |

Détail et limites de cette évaluation : voir [`docs/evaluation_ragas.md`](docs/evaluation_ragas.md) et [`docs/limitations.md`](docs/limitations.md).

## Installation

### Prérequis
- Python 3.12
- Node.js 20+
- Docker Desktop (optionnel, pour la conteneurisation)
- [Ollama](https://ollama.com) (pour le LLM en local) et/ou une clé API [Groq](https://console.groq.com) (gratuite)

### Backend

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

Crée un fichier `.env` à la racine :

GROQ_API_KEY=votre_cle_groq
LLM_PROVIDER=ollama # ou "groq"


Lance le serveur :
```bash
uvicorn src.api.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Application accessible sur `http://localhost:5173`.

### Docker (build unifié)

```bash
docker build -t vehicle-diagnostic .
docker run -p 7860:7860 --env-file .env vehicle-diagnostic
```

## Structure du projet

vehicle-diagnostic-rag/
├── data/
│ ├── raw/ # Données brutes (DTC, NHTSA)
│ └── processed/ # Données nettoyées et indexées
├── src/
│ ├── ingestion/ # Scripts de collecte des données
│ ├── rag/ # Retriever, reranking, prompt, pipeline RAG
│ ├── api/ # API FastAPI
│ └── eval/ # Évaluation RAGAS
├── frontend/ # Application React
├── docs/ # Cahier des charges, limitations, évaluation
├── chroma_db/ # Base vectorielle persistée
├── Dockerfile
└── requirements.txt


## Périmètre et limites

Le projet se concentre volontairement sur les codes DTC génériques P0xxx (moteur/transmission) et 5 modèles de véhicules (Toyota Corolla, Honda Civic, Ford Focus, Nissan Sentra, Volkswagen Golf), années 2015-2019. Cet outil est un projet académique d'aide au diagnostic et ne remplace pas l'avis d'un technicien automobile certifié. Les limites techniques observées (fidélité au contexte, comportement du reranking multilingue, etc.) sont documentées en détail dans [`docs/limitations.md`](docs/limitations.md).

## Pistes d'évolution

- Reranking multilingue (ex: bge-reranker-v2-m3)
- Streaming des réponses
- Cache sémantique
- Boucle de feedback utilisateur

---