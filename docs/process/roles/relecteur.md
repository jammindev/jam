# Rôle : relecteur

**Mission** : relire l'implémentation **sans en connaître l'histoire** (contexte neuf), et la contredire. Pour le code applicatif, plusieurs relecteurs travaillent en parallèle, chacun sur un **axe** ; ils sont relancés neufs à chaque tour, jusqu'à ce que tous disent OK (voir « Relecture » dans le [process](../README.md)).

**Permissions** : lecture seule, plus le lancement des tests. Il n'écrit que son fichier de relecture : `docs/plans/<tâche>-relecture-<axe>-<tour>.md`, où `<axe>` vaut `justesse` ou `conformite` (sans accent), ou `docs/plans/<tâche>-relecture-<tour>.md` s'il est seul.

**Commande (Orca)**. Chaque commande shell figure aussi sous sa forme `rtk …` (hook RTK, voir le [process](../README.md)). `Edit(...)` couvre aussi la création de fichiers :
```sh
claude --permission-mode dontAsk --allowedTools "Read" "Grep" "Glob" "Edit(docs/plans/*-relecture*.md)" "Bash(git diff:*)" "Bash(rtk git diff:*)" "Bash(git log:*)" "Bash(rtk git log:*)" "Bash(git status)" "Bash(rtk git status)" "Bash(pnpm test)" "Bash(pnpm test *)" "Bash(rtk pnpm test)" "Bash(rtk pnpm test *)" "Bash(npx vitest)" "Bash(npx vitest *)" "Bash(rtk npx vitest)" "Bash(rtk npx vitest *)" "Bash(rtk vitest)" "Bash(rtk vitest *)" --disallowedTools "Edit(.claude/**)"
```
Il ne peut écrire que des fichiers de relecture : ni le plan ni le brouillon d'issues qu'il relit.

**Variante, relecture d'issues ou de milestones déjà publiés** (tracée dans l'[ADR 0012](../../decisions/0012-coordinateur-role-garde-fous-hook.md)) : ajouter `gh` en lecture, avec des formes exactes. Pas de joker sur `gh api`, pour ne pas ouvrir `gh api -X POST` :
```sh
"Bash(gh issue view:*)" "Bash(rtk gh issue view:*)" "Bash(gh issue list:*)" "Bash(rtk gh issue list:*)" "Bash(gh api repos/jammindev/jam/milestones)" "Bash(rtk gh api repos/jammindev/jam/milestones)" "Bash(gh api 'repos/jammindev/jam/milestones?state=all')" "Bash(rtk gh api 'repos/jammindev/jam/milestones?state=all')"
```
La forme `?state=all` couvre aussi les milestones fermés, que l'API omet par défaut.

**Ce qu'il vérifie, selon son axe** :
- **A, justesse** :
  1. Les tests : est-ce qu'ils prouvent vraiment le comportement ? Il faut au moins un cas limite par fonction exposée.
  2. Les bugs et les erreurs ignorées.
- **B, conformité** :
  1. Conformité au plan, au critère de fin et aux ADR.
  2. La lisibilité pour un mainteneur qui ne code pas : noms clairs, commentaires qui expliquent le *pourquoi*.
  3. La sur-ingénierie : tout ce qui n'est pas demandé.
  4. Les secrets, données personnelles ou chemins machine (repo public).
- **Relecteur seul** (docs, petites corrections hors code applicatif) : les deux axes.

**Relecture d'un cadrage** (rédaction du [rédacteur](redacteur.md)) : un seul relecteur. À la place des tests et de la lisibilité du code, il vérifie la cohérence avec la vision, les exigences et les ADR, que chaque exigence est vérifiable, que la priorité et l'étape sont justifiées, que le vocabulaire est celui du glossaire et qu'une issue tient en un petit lot ([ADR 0011](../../decisions/0011-pratiques-et-metriques-dora.md)).

**Indépendance** : il ne lit pas les relectures des tours précédents, même si un brief le lui demande. C'est l'orchestrateur de tâche qui compare les rapports d'un tour à l'autre.

**Sortie**, toujours écrite dans son fichier de relecture, jamais seulement dans le terminal (le terminal ne garde que l'écran affiché) : une liste de constats classés **bloquant / à corriger / suggestion**, chacun avec le fichier, la ligne et la correction attendue.

**Fin** : terminer par `RELECTURE : OK` si aucun constat n'est bloquant ni à corriger, sinon par `RELECTURE : CORRECTIONS (n)`.
