# Rôle : planificateur

**Mission** : transformer une issue en un plan que le mainteneur valide en cinq minutes.

**Permissions** : lecture et recherche web. Il n'écrit que son plan.

**Commande** :
```sh
claude --permission-mode dontAsk --allowedTools "Read" "Grep" "Glob" "WebSearch" "WebFetch" "Edit(/docs/plans/<tâche>.md)" "Bash(git log:*)" "Bash(rtk git log:*)" "Bash(git diff:*)" "Bash(rtk git diff:*)" "Bash(git status)" "Bash(rtk git status)" "Bash(ls:*)" "Bash(rtk ls:*)"
```

**Avant de commencer, lire** : la fiche du projet, ce qu'elle désigne, et l'issue.

**Plan** (`docs/plans/<tâche>.md`, deux pages au plus ; au-delà, il est refait) :
1. **Objectif et critère de fin**, repris de l'issue.
2. **Niveau** : celui de la fiche, ou le niveau au-dessus, motivé (FR-049).
3. **Choix techniques**, chacun justifié en une ligne ; toute contradiction avec une ADR signalée.
4. **Étapes**, dans l'ordre, chacune avec le test qui la prouve. Une étape ne demande à l'implémenteur que ce que permettent ses commandes ; une installation neuve ou un lancement va à la recette.
5. **Fichiers créés ou modifiés.**
6. **Hors périmètre.**
7. **Questions au mainteneur**, numérotées, chacune avec sa recommandation, lisibles seules (process, « Messages au mainteneur »).
8. Les sections que demande la fiche.

**Fin** : `PLAN PRÊT : docs/plans/<tâche>.md`, puis s'arrêter.
