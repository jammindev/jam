# Relecture — cadrage `specs-retours-dora`, tour 6

> Relecteur seul, contexte neuf. Objet : `git diff main` (un commit local), hors rapports de relecture des tours précédents, non lus.
> Décisions du mainteneur prises comme acquises : pas d'échéance sur les milestones ; RET-007 validé (instances Claude neuves, diversité de modèles en E2) ; les trois compléments DORA de RET-002 validés. Faits vérifiés par le coordinateur pris comme acquis : S1 mergé (PR #5), issue #1 fermée, hook de démarrage et garde du coordinateur installés hors repo, garde active seulement avec `JAM_ROLE=coordinateur`.

## Synthèse par point du brief

1. **Cohérence entre fichiers** : bonne. Les numéros sont libres et uniques (FR-036 à FR-038, Q-022 à Q-033, ADR 0011 et 0012, RET-001 à RET-007). Le glossaire, la roadmap, le process, les profils et les deux ADR disent la même chose sur l'absence de progrès, les axes, le cadrage, la garde et les mentions à reporter dans les ADR 0008 et 0009 à l'acceptation. Les définitions DORA citées dans l'ADR 0011 correspondent à celles de dora.dev. Deux écarts, ci-dessous.
2. **Fidélité aux retours** : les changements sont tous rattachés à un retour, ou présentés explicitement comme une friction du coordinateur (RTK, Q-022 à Q-025) ou comme un durcissement fait par précaution. Un seul changement de fond n'est pas tracé (coupe 4 de la roadmap, en suggestion).
3. **Repo public** : rien trouvé. Pas de secret, pas de donnée personnelle au-delà du prénom déjà présent dans le glossaire, pas de chemin propre à une machine (`~/.claude` dans Q-024 est générique).
4. **Clarté pour un mainteneur qui ne code pas** : correcte. La section RTK et « Ce qu'Orca ne permet pas » sont denses, mais elles s'expliquent seules.
5. **Permissions des profils** : aucun profil de rôle du pipeline ou du cadrage n'ouvre le commit, le push ou `gh` en écriture. La variante du relecteur s'en tient à des formes `gh` exactes, en lecture. Seul le coordinateur a ces droits, par exception tracée (ADR 0012). Les voies de contournement qui restent (`node -e`, script de test) sont reconnues dans le process et dans Q-025. Deux resserrages sont proposés en suggestion.
6. **Brouillon d'issues** : il couvre bien le critère du S2 (chaque élément du critère est porté par au moins une issue, avec ses fiches concept). Les issues sont petites et vérifiables. Une dépendance est fausse (à corriger n° 1).

## Bloquant

Aucun.

## À corriger

### 1. S2-c ne peut pas avancer en parallèle de S2-a sans S2-b

- **Fichier** : `docs/plans/specs-retours-dora-issues.md`, ligne 39 (et S2-c, ligne 83).
- **Constat** : le brouillon annonce que « S2-a et S2-c peuvent avancer en parallèle ». Or S2-c enregistre dans l'état « l'identifiant de session, le coût, et l'heure de début et de fin de l'étape ». Une étape appartient à une tâche, et la table des tâches n'arrive qu'avec S2-b (ligne 64). De plus, S2-b ajoute une migration numérotée, et S2-c devra en ajouter une pour les étapes. Les migrations s'ajoutent à la fin d'une même liste (`packages/core/src/db/migrations.ts`, ADR 0010) : deux worktrees en parallèle écriraient tous les deux la migration 2, d'où un conflit garanti au second merge. Or l'ordre publié guide le coordinateur quand il lance les tâches en parallèle.
- **Correction attendue** : au choix, de préférence la première option :
  - écrire que S2-c démarre après le merge de S2-b, et retirer la mention du parallélisme avec S2-a, ou la remplacer par un parallélisme réellement indépendant ;
  - ou bien sortir la persistance de l'étape de S2-c (S2-c relève seulement les valeurs, comme le dit déjà son test, ligne 86) et la confier à S2-f. Le parallélisme S2-a ∥ S2-c tient alors.

### 2. Le report de la diversité de modèles en E2 n'est noté dans aucune question ouverte

- **Fichiers** : `docs/process/README.md`, ligne 95 ; `docs/specs/RETOURS.md`, ligne 80 ; `docs/specs/OPEN-QUESTIONS.md`, après la ligne 37.
- **Constat** : le process et RET-007 reportent la diversité de modèles des relecteurs « à E2 ». Ce report n'apparaît ni dans `OPEN-QUESTIONS.md` ni dans la ligne E2 de la roadmap. La règle 4 d'`AGENTS.md` et le profil du rédacteur demandent pourtant que tout ce qui vient « pour plus tard » soit noté dans `OPEN-QUESTIONS.md`. Quand RET-007 passera à « appliqué », plus rien ne rappellera ce point en E2.
- **Correction attendue** : ajouter une question, par exemple `Q-034 | Relecture par des modèles différents (RET-007) : quels modèles, sur quels axes, quand le harness est branché comme deuxième backend | E2 | Ben | Ouvert. Instances Claude neuves d'ici là`. Le process (ligne 95) et RET-007 (ligne 80) peuvent y renvoyer.

## Suggestions

1. **`docs/specs/04-ROADMAP.md`, ligne 34** : la coupe 4 passe d'« un rôle livreur exécute les commandes `gh` » à « le cœur exécute les commandes `gh` ». Ce changement de fond est juste, puisqu'un rôle qui pousse contredirait NFR-012 et l'ADR 0009, mais aucun retour ne le porte. Le tracer en une demi-phrase, par exemple « (aucun rôle ne pousse, NFR-012) », ou dans l'impact de RET-005.
2. **`docs/specs/01-REQUIREMENTS.md`, ligne 87 (NFR-009)** : « trois feux verts, questions, blocages ». Le feu vert de cadrage est une quatrième occasion d'interrompre le mainteneur. Préciser « trois feux verts par tâche, plus le feu vert de cadrage », ou laisser tel quel si NFR-009 ne vise que le pipeline d'une tâche.
3. **`docs/process/README.md`, ligne 9** : les permissions des rôles renvoient à l'ADR 0009 seule, alors que le rédacteur est tracé dans l'ADR 0012. Écrire « ([ADR 0009](…), [ADR 0012](…) pour le rédacteur) ».
4. **`docs/decisions/0012-coordinateur-role-garde-fous-hook.md`, ligne 27** : la colonne « Réseau / Git distant » du coordinateur dit « Oui, après feu vert ». Or la lecture (`gh issue view`, `git fetch`) n'attend aucun feu vert. Écrire « Lecture : oui. Push, publication, merge : après feu vert ».
5. **`docs/process/README.md`, ligne 113** : « Sa garde refuse ses écritures de fichiers ». Ajouter « hors des emplacements autorisés (mémoire, plan, dossiers temporaires, hook relu) », pour rester d'accord avec l'ADR 0012 (ligne 22) et le profil.
6. **`docs/process/roles/relecteur.md`, ligne 9** : `Bash(npx vitest*)` et `Bash(pnpm test*)`, écrits sans espace avant `*`, autorisent aussi `npx vitest-<autre paquet>`, c'est-à-dire le téléchargement et l'exécution d'un paquet quelconque. Écrire `"Bash(npx vitest)" "Bash(npx vitest *)"` et `"Bash(pnpm test)" "Bash(pnpm test *)"`, sans oublier les formes `rtk`. Ce n'est pas un trou nouveau (Q-025 ouvre déjà toute commande par le script de test), mais c'est gratuit à fermer.
7. **`docs/process/roles/relecteur.md`, ligne 9** : `Edit(docs/plans/*-relecture*.md)` permet aussi de réécrire les rapports des tours précédents, sur lesquels le coordinateur s'appuie pour comparer. Le noter en une phrase dans « Ce qu'Orca ne permet pas », ou demander au coordinateur de donner le nom exact du fichier dans le brief.
8. **`docs/process/roles/relecteur.md`, ligne 15** : `gh api repos/jammindev/jam/milestones` ne renvoie que les milestones **ouverts** (valeur par défaut de l'API GitHub). Pour relire aussi un milestone fermé, ajouter la forme exacte `gh api 'repos/jammindev/jam/milestones?state=all'`, avec sa forme `rtk`.
9. **`docs/process/README.md`, ligne 94, et `docs/process/roles/relecteur.md`, ligne 5** : `<axe>` dans un nom de fichier. Fixer la valeur, `justesse` ou `conformite`, sans accent. Le S1 utilisait `A` et `B`.
10. **`AGENTS.md`, ligne 20** : « une tâche = une issue GitHub = un worktree ». Ajouter « (un cadrage : un worktree `cadrage-<slug>`, sans issue) », puisqu'un agent qui lit ce fichier peut justement tourner dans un cadrage.
11. **`docs/decisions/0011-pratiques-et-metriques-dora.md`, ligne 47** : l'issue `incident` « désigne la PR fautive ». Mais pour `house`, la livraison est un déploiement, qui peut emporter plusieurs PR. Préciser comment on passe de la PR à la livraison fautive, ou le laisser au cadrage du S4 avec une ligne dans `OPEN-QUESTIONS.md`.
12. **`docs/specs/01-REQUIREMENTS.md`, ligne 15** : FR-038 est rangée entre FR-022 et FR-023. Ce n'est pas faux, mais la lecture serait plus facile en fin de tableau.
13. **`docs/specs/04-ROADMAP.md`, ligne 46** : si la coupe 1 s'applique, la « fiche : métriques DORA » tombe avec l'écran. Le dire dans la même phrase.

RELECTURE : CORRECTIONS (2)
