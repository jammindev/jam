# ADR 0009 : permissions par rôle, jamais de mode sans permission

- **Statut** : acceptée
- **Date** : 2026-10-08
- **Tranche** : Q-010

## Contexte

Les étapes du pipeline tournent sans surveillance ([ADR 0008](0008-boucle-exterieure-pipeline.md)). Aujourd'hui, le mainteneur lance ses workers sans aucune permission, et Orca le fait aussi par défaut. Or un worktree ne protège ni le réseau, ni `$HOME`, ni les secrets.

## Décision

- **Le mode sans permission (`bypassPermissions`) est interdit.**
- **Chaque rôle a son profil de permissions**, transmis à Claude Code headless par `--permission-mode` et `--allowedTools` / `--disallowedTools`. Toute demande qui sortirait du profil est **refusée automatiquement**, sans invite (`--permission-prompts none` ou `dontAsk`).

| Rôle | Fichiers | Shell | Réseau / Git distant |
|---|---|---|---|
| Planificateur | Lecture seule | `git diff/log/status`, commande de tests | Non |
| Implémenteur | Lecture et écriture dans le worktree | Liste blanche : dépendances, tests, lint, build, `git status/diff` | Non |
| Relecteur | Lecture seule | `git diff/log`, commande de tests | Non |
| Recetteur | Lecture seule | Commande ou skill de recette du repo | Selon la recette (navigateur local) |

- **Aucun rôle ne committe, ne pousse ni ne merge.** Le commit, le push, la création de PR et le merge sont faits par le cœur (aujourd'hui, par le coordinateur), après le feu vert correspondant. C'est déjà la pratique du mainteneur : ses workers ne committent jamais.
- Les profils exacts (commandes Claude Code) sont décrits dans [`docs/process/roles/`](../process/roles/).
- **Un refus de permission est un signal.** Le cœur le repère (champ `permission_denials` du résultat `stream-json`, à vérifier au moment de l'implémentation). La tâche passe alors à « bloqué » et apparaît dans la file « À toi », avec la commande demandée. Le mainteneur peut l'autoriser une fois ou l'ajouter à la liste blanche du repo.

## Conséquences

- (+) La sécurité devient structurelle : elle ne repose plus sur l'obéissance de l'agent.
- (+) Les rôles en lecture seule ne peuvent pas déborder, ce qui répond à la friction « l'agent a implémenté sans y être invité ».
- (−) Au début, les listes blanches vont trop bloquer. Il faudra les ajuster à l'usage.
- (−) Pas de sandbox système (Seatbelt, conteneur) au MVP. Ce sera traité au thème 7, plus tard.
