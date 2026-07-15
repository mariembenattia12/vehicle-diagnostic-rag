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