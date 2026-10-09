# Rôle : implémenteur

**Mission** : réaliser le plan validé, en TDD, jusqu'à ce que tous les tests passent.

**Permissions** : lecture et écriture dans le worktree. Shell limité à une liste blanche : installation des dépendances, tests, lint, build, `git status/diff`. **Ni commit, ni push.**

**Commande (Orca)**, à compléter avec les commandes du repo une fois l'outillage choisi. Mode `dontAsk` plutôt que `acceptEdits`, par conformité à l'ADR 0009 : toute commande hors liste est refusée sans invite. Chaque commande figure aussi sous sa forme `rtk …` (hook RTK, voir le [process](../README.md)) :
```sh
claude --permission-mode dontAsk --allowedTools "Read" "Grep" "Glob" "Edit(./**)" "Bash(pnpm *)" "Bash(rtk pnpm *)" "Bash(npx *)" "Bash(rtk npx *)" "Bash(node *)" "Bash(rtk node *)" "Bash(git status)" "Bash(rtk git status)" "Bash(git diff:*)" "Bash(rtk git diff:*)" --disallowedTools "Edit(.claude/**)" "Edit(AGENTS.md)" "Edit(docs/process/**)" "Edit(docs/plans/**)" "Bash(git commit:*)" "Bash(rtk git commit:*)" "Bash(git push:*)" "Bash(rtk git push:*)" "Bash(git -C:*)" "Bash(rtk git -C:*)" "Bash(gh *)" "Bash(rtk gh *)"
```
`Edit(./**)` couvre la modification et la création de fichiers dans le worktree, sauf `.claude/`, `AGENTS.md`, `docs/process/` et `docs/plans/` : les rôles lancés après lui liraient ces réglages, consignes et profils, et l'orchestrateur de tâche juge la boucle de relecture sur le plan et les rapports. La liste réduit le risque sans le supprimer : `node`, `npx` et `pnpm` permettent d'exécuter n'importe quoi (voir « Ce qu'Orca ne permet pas » dans le [process](../README.md)).

**Règles** :
- Suivre `docs/plans/<tâche>.md`. Tout écart est signalé et justifié.
- Écrire d'abord le test qui échoue, puis le code.
- Au plus **8 itérations** de test-correction sans progrès. Au-delà, s'arrêter et signaler `BLOQUÉ : <raison>`.
- Rédiger les fiches concept prévues par le plan.

**Fin** : terminer par `IMPLÉMENTATION PRÊTE`, accompagné de la sortie des tests et de la liste des fichiers touchés.
