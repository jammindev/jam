# 04 — Roadmap

> Statut : périmètre du MVP fixé par l'[ADR 0008](../decisions/0008-boucle-exterieure-pipeline.md). Jalons d'E0 posés, un milestone GitHub chacun.

## Étapes

| Étape | Contenu | Statut |
|---|---|---|
| **E0 — MVP** (≤ 1 mois) | **Boucle extérieure** sur Claude Code headless. Une issue traverse le pipeline dans son worktree jusqu'au merge, avec la file « À toi », les notifications filtrées, le registre de commandes d'UI et la mesure de la livraison (métriques DORA). | À faire |
| E0.5 | Coordinateur conversationnel (cadrage → issues), agent qui pilote l'UI, champ global compatible avec la dictée | À faire |
| E1 | Harness maison minimal en CLI : boucle intérieure avec `read`, `write`, `shell`, `search`, puis `edit` | À faire |
| E2 | Harness branché comme deuxième backend d'agent, rôles imposés, comparaison avec Claude Code | À faire |
| E3 | Confort : diff, éditeur et recherche de fichiers, push mobile, navigateur façon Design Mode | À faire |

## Périmètre du MVP (E0)

Briques, dans l'ordre :

1. **Squelette** : app Electron et cœur séparé, registre de commandes et palette (Cmd+K), liste de repos.
2. **Issue → worktree** : lecture des issues via `gh`, création du worktree et de sa branche.
3. **Rôle exécuté** : lancement de Claude Code headless avec un profil de rôle et son contexte d'environnement (FR-038) dans un worktree, lecture du `stream-json`, persistance horodatée de l'état (FR-036).
4. **Pipeline** : enchaînement des étapes, boucles tests et relecture, garde-fous, trois feux verts.
5. **File « À toi » et notifications filtrées.**
6. **PR, CI et merge** via `gh`, puis nettoyage.
7. **Mesure** : écran minimal des métriques DORA et des indicateurs agents (FR-037, ADR 0011).

**Critère de fin d'E0** : sur `house`, trois issues réelles traversent le pipeline en parallèle jusqu'au merge. Le mainteneur n'intervient que sur la file « À toi ».

### Coupes possibles si le mois ne suffit pas (dans cet ordre)

1. L'écran des métriques (FR-037) : les horodatages restent enregistrés (FR-036), l'écran peut donc venir plus tard sans perte.
2. La recette automatique par agent : le feu vert 2 couvre seulement la recette manuelle.
3. Le multi-repo : un seul repo configuré.
4. L'étape 6 automatisée : le cœur exécute les commandes `gh` (push, PR, merge) sous feu vert, sans suivi intégré de la CI (aucun rôle ne pousse, NFR-012).
5. La reprise de conversation avec un lead.

## Jalons d'E0 (≈ 1 semaine chacun)

Chaque jalon est un milestone GitHub, et chaque tâche une issue rattachée : [github.com/jammindev/jam/milestones](https://github.com/jammindev/jam/milestones). Un jalon est découpé en petites issues **au début du jalon**, par un cadrage (rédacteur, relecteur, feu vert cadrage). Seul le S1 fait exception : une seule issue, dont le plan était déjà validé.

| # | Jalon | Critère de « fini » vérifiable |
|---|---|---|
| S1 | **Squelette** : app Electron, cœur séparé et protocole typé, registre de commandes et palette Cmd+K, liste des repos, configuration par repo (commande de tests et commande de recette) | L'app se lance. Cmd+K liste les commandes et les exécute. Le cœur tourne seul en CLI et répond à une requête. Les tests passent en CI. Fiches concept : processus Electron, cœur séparé. |
| S2 | **Issue → worktree → un rôle** : lecture des issues via `gh`, création du worktree, exécution du rôle planificateur en headless avec son profil (ADR 0009), état SQLite avec horodatage des étapes (FR-036), injection du contexte d'environnement au rôle (FR-038), fil résumé | Le mainteneur choisit l'issue n de `house`, le worktree est créé et le plan s'affiche. Le planificateur est lancé avec son profil de permissions (ADR 0009). Le brief qu'il reçoit contient le worktree, l'issue, l'étape et le process. L'état enregistre l'heure de début et de fin de l'étape. Le fil résumé montre les événements significatifs de l'étape. Après redémarrage de l'app, l'état est conservé. Fiches : worktree, stream-json. |
| S3 | **Pipeline jusqu'à la PR** : enchaînement des rôles, boucles tests et relecture (pour le code, au moins deux relecteurs neufs, un par axe, jusqu'à ce que tous disent OK), garde-fous, trois feux verts, file « À toi », notifications filtrées | Une vraie issue de `house` arrive jusqu'à une PR avec la CI verte, et le mainteneur n'intervient que via la file. Seuls les passages dans la file « À toi » déclenchent une notification. Fiche : boucle extérieure. |
| S4 | **Merge, nettoyage, parallélisme, métriques** : feu vert 3 → `gh pr merge`, suppression du worktree et des branches, 3 tâches en parallèle, écran minimal des métriques DORA et désignation du workflow de déploiement par repo (FR-037, ADR 0011) | Trois issues de `house` traversent le pipeline en parallèle jusqu'au merge (critère d'E0). L'écran « Métriques » affiche, pour `house`, les cinq métriques DORA et les indicateurs agents, et pour jam, les cinq métriques ; les indicateurs agents de jam peuvent rester vides tant que ses tâches passent par Orca (ADR 0011 §5). Cette seconde phrase, comme la fiche « métriques DORA », tombe si la coupe 1 s'applique, et se limite à `house` si la coupe 3 s'applique. Fiche : métriques DORA. |

## Explicitement repoussé

- Diff, éditeur, arbre et recherche de fichiers : E3. Ce sont des fonctions rarement utilisées par le mainteneur.
- Même tâche confiée à plusieurs agents (S2) : Won't.
- Équipe d'agents permanents qui dialoguent entre eux : Won't (ADR 0008).
- Espaces hors code : après le MVP.
- Exécution distante sur le VPS, client mobile : après le MVP.

## Risques principaux

- **R-01** — Rester bloqué à E0 sans jamais écrire le harness. **Mitigation** : E0 limitée à 1 mois, avec une liste de coupes prête. Orca reste l'outil de repli. Le risque est réduit par l'ADR 0008 : E0 apporte désormais une valeur propre (pipeline imposé, file « À toi ») qu'Orca n'offre pas.
- **R-02** — Les boucles automatiques consomment le quota de l'abonnement, dont les limites ont déjà été atteintes. **Mitigation** : plafond d'itérations, budget par étape et détection d'absence de progrès en relecture (FR-024), et coût affiché par tâche. La relecture jusqu'à satisfaction, à plusieurs relecteurs (RET-006, RET-007), rend le budget d'autant plus nécessaire.
- **R-03** — Permissions des agents qui tournent sans surveillance. **Mitigation** : profils de permissions par rôle et mode sans permission interdit (ADR 0009), coordinateur traité comme un rôle avec sa garde (ADR 0012). Le sandbox système viendra plus tard.
- **R-04** — Le format `stream-json` ou les options de la CLI Claude Code changent. **Mitigation** : figer la version testée, et ne lire ce format qu'en un seul endroit (le backend Claude Code).
