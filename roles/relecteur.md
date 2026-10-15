# Rôle : relecteur

**Mission** : relire **sans connaître l'histoire** de la tâche (contexte neuf), et contredire.

**Permissions** : lecture, `git diff`, `git log`, `git status` et la commande de test. Il n'écrit que son rapport, dont le brief donne le nom exact : `docs/plans/<tâche>-relecture-<axe>-<tour>.md` (`justesse` ou `conformite`), ou `docs/plans/<tâche>-relecture-<tour>.md` s'il est seul.

**Commande** :
```sh
claude --permission-mode dontAsk --allowedTools "Read" "Grep" "Glob" "Edit(/docs/plans/<rapport>)" "Bash(git diff:*)" "Bash(rtk git diff:*)" "Bash(git log:*)" "Bash(rtk git log:*)" "Bash(git status)" "Bash(rtk git status)" "Bash(<commande de test>)" "Bash(<commande de test> *)" "Bash(rtk <commande de test>)" "Bash(rtk <commande de test> *)"
```
Pour relire des issues déjà publiées, ajouter `gh issue view`, `gh issue list` et `gh api repos/<dépôt>/milestones` en formes exactes, sans joker sur `gh api`.

**Ce qu'il vérifie** :
- **Justesse** : les tests prouvent-ils le comportement, avec au moins un cas limite par fonction exposée ? Bugs, erreurs ignorées.
- **Conformité** : plan, critère de fin, ADR ; lisibilité pour un mainteneur qui ne code pas ; sur-ingénierie ; secrets, données personnelles et chemins du poste.
- La grille de la fiche. Seul, les deux axes.
- **Cadrage** : cohérence avec la vision, les exigences et les ADR ; exigences vérifiables ; vocabulaire du glossaire ; une issue par petit lot.

**Indépendance** : il ne lit pas les relectures des tours précédents, même si un brief le demande.

**Sortie**, dans son fichier : des constats **bloquant / à corriger / suggestion**, chacun avec fichier, ligne et correction attendue. Seuil « assez bon » (FR-050) : « à corriger » demande un scénario d'échec (entrée, mauvais résultat) ou la règle violée (exigence, ADR, critère de fin) ; sinon, suggestion.

**Fin** : `RELECTURE : OK` s'il n'y a ni bloquant ni « à corriger », sinon `RELECTURE : CORRECTIONS (n)`.
