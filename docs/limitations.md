# Limitations observées — Pipeline RAG 

## Modele utilise
Llama 3.2 3B en local (Ollama), temperature=0

## Limitations constatees
1. **Traduction imparfaite** : le modele traduit parfois maladroitement des
   termes techniques anglais vers le francais (ex: "air/fuel mixture" rendu
   de facon approximative).
2. **Inference speculative** : sur des questions ambigues avec plusieurs
   documents proches, le modele relie parfois des faits de maniere non
   confirmee explicitement par le contexte (ex: associer une plainte a un
   rappel connu sans lien direct etabli dans les sources).
3. **Disclaimer non fiable via prompt seul** : le modele reformule parfois
   le texte legal au lieu de le reproduire mot pour mot -> mitigation
   appliquee en forcant le disclaimer par code plutot que par instruction
   au LLM.

## Pistes d'amelioration (hors scope MVP)
- Reranking des documents recuperes avant generation
- Modele plus grand (7B+) ou API cloud pour les cas ambigus
- Extraction structuree (ex: JSON des faits) avant synthese en langage naturel



## Limitations observées — Reranking (cross-encoder)

### Contexte
Un reranking par cross-encoder (ms-marco-MiniLM-L-6-v2) a ete ajoute apres la
recherche vectorielle initiale (bi-encoder), afin d'ameliorer la selection des
documents les plus pertinents avant generation de la reponse.

### Amelioration mesuree (RAGAS, avant/apres)
| Metrique           | Avant | Apres | Evolution |
|---------------------|-------|-------|-----------|
| Faithfulness         | 0.81  | 0.93  | +0.12     |
| Answer relevancy      | 0.63  | 0.78  | +0.15     |
| Context precision     | 0.86  | 0.89  | +0.03     |
| Context recall        | 1.00  | 1.00  | stable    |

### Limitation identifiee
Sur la question "Y a-t-il eu des rappels sur les airbags Honda Civic ?", le
reranking a degrade le resultat par rapport a la version sans cross-encoder :
le document pertinent (rappel Takata) a ete mal classe au profit d'un rappel
moteur sans rapport avec la question.

**Cause probable** : le modele ms-marco-MiniLM-L-6-v2 est entraine
principalement sur des requetes web en anglais (jeu de donnees MS MARCO), pas
sur du contenu technique automobile ni sur des questions en francais. Il peut
donc mal evaluer la pertinence de documents techniques anglais face a une
question francophone, malgre de meilleurs resultats en moyenne sur le reste
du jeu de test.

### Pistes d'amelioration (hors scope MVP)
- Utiliser un modele de reranking multilingue (ex: bge-reranker-v2-m3)
- Ou traduire la question en anglais avant le reranking, puis retraduire la
  reponse
- Fine-tuner un cross-encoder sur un corpus automobile bilingue