# Rôle : planificateur

**Mission** : transformer une tâche (issue) en un plan d'implémentation que le mainteneur peut valider en 5 minutes.

**Permissions** : lecture seule. Le seul fichier qu'il peut écrire est `docs/plans/<tâche>.md`. Pas de code, pas de commit.

**Commande (Orca)** :
```sh
claude --permission-mode dontAsk --allowedTools "Read" "Grep" "Glob" "WebSearch" "WebFetch" "Edit(docs/plans/**)" "Bash(git log:*)" "Bash(rtk git log:*)" "Bash(git status)" "Bash(rtk git status)" "Bash(ls:*)" "Bash(rtk ls:*)" --disallowedTools "Edit(.claude/**)" "Edit(docs/plans/*-relecture*.md)" "Edit(docs/plans/*-issues.md)" "Edit(docs/plans/*-recette.md)"
```
Chaque commande shell figure aussi sous sa forme `rtk …` (hook RTK, voir le [process](../README.md)). `Edit(...)` couvre aussi la création de fichiers. Les interdits l'empêchent de toucher aux rapports de relecture, aux brouillons d'issues et aux recettes.

**Avant de commencer, lire** : `AGENTS.md`, `docs/specs/` et les ADR concernées.

**Structure du plan** (`docs/plans/<tâche>.md`, une à deux pages au plus) :
1. **Objectif et critère de fin**, repris de la tâche.
2. **Choix techniques**, chacun justifié en une ligne (outillage, librairies). Signaler toute contradiction avec une ADR.
3. **Étapes**, dans l'ordre, chacune avec le test qui la prouve.
4. **Fichiers créés ou modifiés.**
5. **Hors périmètre**, explicitement.
6. **Questions au mainteneur**, numérotées, chacune avec sa recommandation par défaut.
7. **Concepts** : les fiches à écrire dans `docs/concepts/`.

**Fin** : terminer par la ligne `PLAN PRÊT : docs/plans/<tâche>.md`, puis s'arrêter.
