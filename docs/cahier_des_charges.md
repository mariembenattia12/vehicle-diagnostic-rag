# Cahier des charges — Assistant de diagnostic véhicule (RAG)

## Objectif
Développer un assistant conversationnel qui aide à comprendre les codes 
défaut (DTC) et les symptômes d'un véhicule, à partir de données publiques 
(codes OBD-II, plaintes NHTSA, rappels constructeur).

## Périmètre (in scope)
- Codes DTC génériques SAE J1979/J2012, catégorie P0xxx uniquement (P0001–P0999)
- Réponses basées uniquement sur des sources publiques et vérifiables
- Modèles ciblés (années 2015–2019) : Toyota Corolla, Honda Civic, 
  Ford Focus, Nissan Sentra, Volkswagen Golf

## Sources de données
- Base DTC : github.com/mytrile/obd-trouble-codes (CSV)
- Plaintes conducteurs : api.nhtsa.gov/complaints/complaintsByVehicle 
  (5 modèles × 5 années = 25 requêtes)
- Rappels et remèdes : api.nhtsa.gov/recalls/recallsByVehicle 
  (mêmes paramètres)

## Hors périmètre (out of scope)
- Codes propriétaires constructeur (hors P0xxx)
- Codes P2xxx/P3xxx et catégories B/C/U (bonus possible en fin de projet, non requis pour le MVP)
- Lecture temps réel depuis un boîtier OBD-II physique
- Diagnostic de sécurité critique (freins, airbags, direction) sans supervision humaine
- Véhicules poids lourd, utilitaires, motos
- Constructeurs/modèles en dehors des 5 retenus

## Disclaimer
Cet outil est un projet académique d'aide au diagnostic, basé sur des 
données publiques (SAE J1979, NHTSA). Il ne remplace pas l'avis d'un 
technicien automobile certifié et ne doit pas être utilisé pour des 
décisions de sécurité critique.

## Métriques de succès
- Précision du retrieval (top-k pertinent)
- Score RAGAS (faithfulness, answer relevancy)
- Latence de réponse raisonnable (< 5s en local)