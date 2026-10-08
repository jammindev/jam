# 04 — Roadmap

> Statut : périmètre du MVP fixé par l'[ADR 0008](../decisions/0008-boucle-exterieure-pipeline.md). Le découpage en jalons hebdomadaires sera fait en fin d'entretien.

## Étapes

| Étape | Contenu | Statut |
|---|---|---|
| **E0 — MVP** (≤ 1 mois) | **Boucle extérieure** sur Claude Code headless. Une issue traverse le pipeline dans son worktree jusqu'au merge, avec la file « À toi », les notifications filtrées et le registre de commandes d'UI. | À faire |
| E0.5 | Coordinateur conversationnel (cadrage → issues), agent qui pilote l'UI, champ global compatible avec la dictée | À faire |
| E1 | Harness maison minimal en CLI : boucle intérieure avec `read`, `write`, `shell`, `search`, puis `edit` | À faire |
| E2 | Harness branché comme deuxième backend d'agent, rôles imposés, comparaison avec Claude Code | À faire |
| E3 | Confort : diff, éditeur et recherche de fichiers, push mobile, navigateur façon Design Mode | À faire |

## Périmètre du MVP (E0)

Briques, dans l'ordre :

1. **Squelette** : app Electron et cœur séparé, registre de commandes et palette (Cmd+K), liste de repos.
2. **Issue → worktree** : lecture des issues via `gh`, création du worktree et de sa branche.
3. **Rôle exécuté** : lancement de Claude Code headless avec un profil de rôle dans un worktree, lecture du `stream-json`, persistance de l'état.
4. **Pipeline** : enchaînement des étapes, boucles tests et relecture, garde-fous, trois feux verts.
5. **File « À toi » et notifications filtrées.**
6. **PR, CI et merge** via `gh`, puis nettoyage.

**Critère de fin d'E0** : sur `house`, trois issues réelles traversent le pipeline en parallèle jusqu'au merge. Le mainteneur n'intervient que sur la file « À toi ».

### Coupes possibles si le mois ne suffit pas (dans cet ordre)

1. La recette automatique par agent : le feu vert 2 couvre seulement la recette manuelle.
2. Le multi-repo : un seul repo configuré.
3. L'étape 6 automatisée : un rôle « livreur » exécute les commandes `gh` sous feu vert, sans intégration native.
4. La reprise de conversation avec un lead.

## Jalons d'E0 (≈ 1 semaine chacun)

| # | Jalon | Critère de « fini » vérifiable |
|---|---|---|
| S1 | **Squelette** : app Electron, cœur séparé et protocole typé, registre de commandes et palette Cmd+K, liste des repos, configuration par repo (commande de tests et commande de recette) | L'app se lance. Cmd+K liste les commandes et les exécute. Le cœur tourne seul en CLI et répond à une requête. Les tests passent en CI. Fiches concept : processus Electron, cœur séparé. |
| S2 | **Issue → worktree → un rôle** : lecture des issues via `gh`, création du worktree, exécution du rôle planificateur en headless avec son profil (ADR 0009), état SQLite, fil résumé | Je choisis l'issue n de `house`, le worktree est créé et le plan s'affiche. Après redémarrage de l'app, l'état est conservé. Fiches : worktree, stream-json. |
| S3 | **Pipeline jusqu'à la PR** : enchaînement des rôles, boucles tests et relecture, garde-fous, trois feux verts, file « À toi », notifications filtrées | Une vraie issue de `house` arrive jusqu'à une PR avec la CI verte, et je n'interviens que via la file. Fiche : boucle extérieure. |
| S4 | **Merge, nettoyage, parallélisme** : feu vert 3 → `gh pr merge`, suppression du worktree et des branches, 3 tâches en parallèle | Trois issues de `house` traversent le pipeline en parallèle jusqu'au merge (critère d'E0). |

## Explicitement repoussé

- Diff, éditeur, arbre et recherche de fichiers : E3. Ce sont des fonctions rarement utilisées par le mainteneur.
- Même tâche confiée à plusieurs agents (S2) : Won't.
- Équipe d'agents permanents qui dialoguent entre eux : Won't (ADR 0008).
- Espaces hors code : après le MVP.
- Exécution distante sur le VPS, client mobile : après le MVP.

## Risques principaux

- **R-01** — Rester bloqué à E0 sans jamais écrire le harness. **Mitigation** : E0 limitée à 1 mois, avec une liste de coupes prête. Orca reste l'outil de repli. Le risque est réduit par l'ADR 0008 : E0 apporte désormais une valeur propre (pipeline imposé, file « À toi ») qu'Orca n'offre pas.
- **R-02** — Les boucles automatiques consomment le quota de l'abonnement, dont les limites ont déjà été atteintes. **Mitigation** : plafonds d'itérations et de budget par étape (FR-024), et coût affiché par tâche.
- **R-03** — Permissions des agents qui tournent sans surveillance. **Mitigation** : profils de permissions par rôle et mode sans permission interdit (ADR 0009). Le sandbox système viendra plus tard.
- **R-04** — Le format `stream-json` ou les options de la CLI Claude Code changent. **Mitigation** : figer la version testée, et ne lire ce format qu'en un seul endroit (le backend Claude Code).
