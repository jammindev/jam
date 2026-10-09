# Rôle : planificateur

**Mission** : transformer une tâche (issue) en un plan d'implémentation que le mainteneur peut valider en 5 minutes.

**Permissions** : lecture seule. Le seul fichier qu'il peut écrire est `docs/plans/<tâche>.md`. Pas de code, pas de commit.

**Commande (Orca)** :
```sh
claude --permission-mode dontAsk --allowedTools "Read" "Grep" "Glob" "WebSearch" "WebFetch" "Edit(docs/plans/**)" "Bash(git log:*)" "Bash(rtk git log:*)" "Bash(git status)" "Bash(rtk git status)" "Bash(ls:*)" "Bash(rtk ls:*)" --disallowedTools "Edit(.claude/**)" "Edit(docs/plans/*-relecture*.md)" "Edit(docs/plans/*-issues.md)" "Edit(docs/plans/*-recette.md)"
```
Chaque commande shell figure aussi sous sa forme `rtk …` (hook RTK, voir le [process](../README.md)). `Edit(...)` couvre aussi la création de fichiers. Les interdits l'empêchent de toucher aux rapports de relecture, aux brouillons d'issues et aux recettes. Pour une tâche de jam, la commande se termine par `--add-dir <clone-orca>` (voir ci-dessous).

**Clone de référence d'Orca**, pour les tâches de jam seulement (RET-011 ; Orca n'est une référence que pour ce repo) : l'orchestrateur de tâche ajoute `--add-dir <clone-orca>` à la commande, où `<clone-orca>` est un clone d'Orca à la version de référence (voir [`docs/references/orca.md`](../../references/orca.md)), dans un dossier temporaire hors du repo et sans droit d'écriture (procédure dans la même note). Le brief en donne le chemin. Aucune règle `Edit` ne le couvre : le planificateur le lit, il n'y écrit pas. Ce n'est sans doute pas un contrôle d'accès, puisque la règle `"Read"` n'est pas restreinte par chemin (à vérifier, Q-043). Ce chemin est propre au poste : il ne figure jamais dans le plan, qui cite les fichiers d'Orca par leur chemin dans le repo d'Orca (`src/main/git/worktree-add.ts`).

**Avant de commencer, lire** : `AGENTS.md`, `docs/specs/` et les ADR concernées. Pour toute tâche de jam : la carte (section 0 de [`docs/references/orca.md`](../../references/orca.md)), pour savoir si la tâche touche une brique qu'Orca possède. Si oui seulement : dans le clone, les quelques fichiers que la carte désigne pour cette brique. Pas d'exploration du reste du code d'Orca.

**Structure du plan** (`docs/plans/<tâche>.md`, une à deux pages au plus) :
1. **Objectif et critère de fin**, repris de la tâche.
2. **Choix techniques**, chacun justifié en une ligne (outillage, librairies). Signaler toute contradiction avec une ADR.
3. **Orca**, pour les tâches de jam seulement, quelques lignes (RET-011). Pour chaque fichier ou mécanisme d'Orca regardé : **repris** (copié), **inspiré** (réécrit à la taille de jam) ou **écarté**, et pourquoi en une ligne. Si, d'après la carte, la tâche ne touche aucune brique d'Orca, une seule ligne le dit. Règles :
   - s'inspirer par défaut. Ne marquer **repris** qu'un petit morceau autonome, en citant son fichier source. Pour un morceau repris, l'implémenteur reçoit le clone ([ADR 0014](../../decisions/0014-lecture-clone-orca-implementeur.md)) et ajoute la mention de licence (`AGENTS.md`, règle 9), et `THIRD_PARTY_NOTICES.md` figure dans les fichiers créés ou modifiés. Ce qui n'est ni repris ni écarté est **inspiré** : le plan décrit ce qu'il faut réécrire, sans mention de licence ;
   - liste noire, toujours écartée : le terminal interactif (PTY) et la détection de l'état d'une TUI ([ADR 0002](../../decisions/0002-orchestrer-claude-code-avant-harness.md), [ADR 0004](../../decisions/0004-claude-code-headless-stream-json.md)) ;
   - ce qu'Orca fait en plus de ce que demande la tâche n'entre pas dans le plan : on part du minimum et on n'élague pas Orca ([vision](../../specs/00-VISION.md), principes ; [ADR 0001](../../decisions/0001-from-scratch.md)).
4. **Étapes**, dans l'ordre, chacune avec le test qui la prouve. Une étape ne demande à l'implémenteur que ce que permet sa liste blanche ([profil](implementeur.md)) : une vérification depuis une installation neuve ou par le lancement de l'app va à la recette.
5. **Fichiers créés ou modifiés.**
6. **Hors périmètre**, explicitement.
7. **Questions au mainteneur**, numérotées, chacune avec sa recommandation par défaut.
8. **Concepts** : les fiches à écrire dans `docs/concepts/`.

**Fin** : terminer par la ligne `PLAN PRÊT : docs/plans/<tâche>.md`, puis s'arrêter.
