# ADR 0010 : état du pipeline en SQLite

- **Statut** : acceptée
- **Date** : 2026-10-08
- **Tranche** : Q-011

## Contexte

L'état du pipeline doit survivre à un redémarrage et rester hors du contexte des agents ([ADR 0008](0008-boucle-exterieure-pipeline.md)). Cet état comprend les tâches, les étapes, les itérations, les coûts, les questions et les feux verts.

## Décision

- **SQLite** via `node:sqlite` (intégré à Node, sans dépendance native), comme Orca. Un seul fichier, stocké dans le dossier de données de l'app.
- Les transcriptions détaillées restent celles de Claude Code (JSONL). L'outil ne garde que l'**identifiant de session** de chaque étape, plus un **résumé d'événements** pour le fil d'activité.
- Le schéma est versionné par migrations numérotées.

## Conséquences

- (+) Requêtes simples pour le tableau et la file « À toi », et écritures transactionnelles.
- (+) Rien à installer en plus.
- (−) `node:sqlite` est récent. Il faut vérifier sa disponibilité dans la version de Node embarquée par Electron au moment de l'implémentation. Solution de repli : `better-sqlite3`.
