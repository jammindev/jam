# Relecture — cadrage `cadrage-s2`, tour 10

Relecteur seul, les deux axes. Objet relu : `git diff` (`specs-retours-dora-issues.md`, `roles/recetteur.md`, `references/orca.md`, `OPEN-QUESTIONS.md`) et le nouveau fichier `docs/plans/cadrage-s2-issues.md`.

## Vérifications faites

- **Carte d'Orca** (§0 de `docs/references/orca.md`, quatre lignes ajoutées) : chaque fichier relu dans un clone du tag `v1.4.218`. Tout existe et correspond à ce que la ligne annonce :
  - `src/main/github/issues.ts` : `listIssues` filtre les entrées qui portent `pull_request`, et une erreur renvoie `error` (via `classifyListIssuesError`), jamais une liste vide seule ;
  - `src/main/github/gh-error-classification.ts` : `classifyListIssuesError` existe. `src/main/github/auth-diagnose.ts` traite `gh` absent (`ENOENT`) et lit `gh auth status` ;
  - `src/shared/workspace-name.ts` : `slugifyForWorkspaceName` remplace tout ce qui sort de `[a-z0-9._-]` par un tiret, donc une lettre accentuée devient bien un tiret ; `getLinkedWorkItemWorkspaceName` existe. `src/main/ipc/worktree-logic.ts` : `sanitizeWorktreeName` garde `\p{L}\p{N}` et lève une erreur sur un nom vide, `.` ou `..` ;
  - `src/shared/commit-message-agent-specs-primary.ts` : `claude -p --output-format text --permission-mode plan`, prompt sur l'entrée standard (`promptDelivery: 'stdin'`). `src/main/text-generation/source-control-local-process.ts` : délai maximal (`SOURCE_CONTROL_GENERATION_TIMEOUT_MS`) et `SIGKILL` de l'enfant ;
  - `src/main/claude/claude-result-outcome.ts` : `is_error` décide, pas le sous-type.

  Les entrées citées par les blocs **Orca** des huit issues existent toutes dans la carte, sous le même intitulé.
- **État GitHub** (`gh` en lecture) : milestone #1 `E0-S1 Squelette` fermé ; #2, #3 et #4 ouverts, sans échéance, avec les anciennes descriptions courtes ; #4 s'appelle encore `E0-S4 Merge et parallélisme`. Issues #2, #3, #4 ouvertes, titres conformes au §2. Le label `enhancement` existe (porté par #2). PR #6 = `specs-retours-dora` (`git log`). Le §1 et le §2 disent vrai.
- **Code cité** : le cœur refuse une base de version plus récente (`packages/core/src/db/database.ts:46`) ; l'app passe `--db` (`apps/desktop/src/main/index.ts:43`, `core-process.ts:25`) ; elle envoie `SIGKILL` au bout de 2 s (`core-process.ts:39-46`).
- **Numérotation** : seules Q-052 et Q-053 sont ajoutées, à la suite de Q-051. Aucun RET ni ADR nouveau. Aucune référence à un numéro inexistant.
- **Renvois** : les titres d'issues cités dans `OPEN-QUESTIONS.md` (Q-012, Q-015, Q-022, Q-027, Q-040, Q-050, Q-052, Q-053) et dans le profil du recetteur correspondent mot pour mot aux titres du §4. Le §5 et `OPEN-QUESTIONS.md` disent la même chose pour chaque question.
- **Repo public** : aucun chemin propre au poste, aucune donnée personnelle, aucune mention d'assistant dans le diff ni dans le brouillon.
- **Cohérence avec les specs** : FR-020, FR-022, FR-027, FR-028, FR-033, FR-036, FR-038, NFR-011 et ADR 0009, 0010, 0011, 0013 à 0015 respectés ; vocabulaire du glossaire (tâche, étape, rôle, feu vert, file « À toi ») ; ordre et dépendances justifiés (§3).

## Bloquant

Aucun.

## À corriger

**C1. S2-g : l'arrêt normal le plus courant, la fermeture de l'app pendant une étape, n'est pas couvert, et le serveur actuel du cœur y mène droit à un agent orphelin.**
`docs/plans/cadrage-s2-issues.md:251` (périmètre), `:257` (critère), `:260` (hors périmètre).
- Le cœur, à la fermeture de son entrée standard, attend que toutes les requêtes en cours aient leur réponse avant de sortir (`packages/core/src/server.ts:49` et `:81`). Or « Lancer le planificateur » (`:250`) répond à la fin de l'étape, donc des minutes plus tard. Quand le mainteneur quitte l'app pendant une étape, le cœur attend cette réponse, l'app le tue au bout de 2 s (`core-process.ts:46`), et Claude Code reste orphelin : c'est le cas « cœur tué » que le hors-périmètre accepte, alors que c'est un arrêt normal.
- Le test du critère (« entrée standard fermée, puis signal d'arrêt : le processus enfant est arrêté ») n'impose aucun délai ni de requête en attente : il peut passer sur le cœur seul tandis que la sortie de l'app laisse l'orphelin.
- **Correction attendue** : dans le critère de fin, préciser le test : « Un test ferme l'entrée standard du cœur pendant une étape, alors que la requête qui l'a lancée attend sa réponse : le processus enfant est arrêté et le cœur sort en moins de 2 s, le délai que lui laisse l'app (`apps/desktop/src/main/core-process.ts`). » Et au périmètre (`:251`), ajouter « dans le délai de 2 s que l'app lui laisse avant de le tuer ». Le plan choisit le moyen (répondre à la requête en attente par une étape interrompue, ou ne pas attendre la fin de l'étape pour répondre).

## Suggestions

**S1. S2-a : nommer le cas limite de la variable vide.** `docs/plans/cadrage-s2-issues.md:95` et `:100`. Le cœur ignore un `JAM_DATA_DIR` vide (`packages/core/src/paths.ts:10`, testé dans `packages/core/test/paths.test.ts:13`). « Quand `JAM_DATA_DIR` est défini » laisse l'app libre de traiter `JAM_DATA_DIR=` comme un dossier. Proposition : au critère, « avec et sans la variable, et avec une variable vide (traitée comme absente, comme le cœur) ».

**S2. S2-h : rendre observable « l'app reste utilisable pendant l'étape ».** `docs/plans/cadrage-s2-issues.md:280`. Proposition : « pendant l'étape, Cmd+K s'ouvre et « Lister les tâches » répond ». C'est aussi ce qui révélerait un cœur bloqué par la requête longue de C1.

**S3. S2-h : dire par quelle commande s'ouvre la vue de la tâche.** `docs/plans/cadrage-s2-issues.md:274`. Chaque action d'UI passe par le registre de commandes (ADR 0007). Proposition : « La vue s'ouvre par une commande de palette (par exemple « Ouvrir une tâche ») et s'ouvre aussi d'elle-même après « Choisir une issue » ».

**S4. S2-h : aligner les états de l'étape sur ceux de S2-g.** `docs/plans/cadrage-s2-issues.md:280` dit « passe d'« en cours » à « terminée » », alors que S2-g (`:249`) définit « réussie, en échec, interrompue ». Proposition : « passe d'« en cours » à son état final (réussie, en échec ou interrompue) ».

**S5. S2-d : l'environnement hérité par le Claude Code que lance jam.** `docs/plans/cadrage-s2-issues.md:183`. La question renvoyée au plan parle des réglages et des hooks ; l'environnement compte aussi. Lancée depuis un terminal d'Orca, l'app transmet au cœur, puis à Claude Code, les variables que lisent les hooks d'Orca (`docs/references/orca.md`, §4 : `ORCA_AGENT_HOOK_ENDPOINT`), et peut-être `JAM_ROLE`, que lit la garde du poste (ADR 0012). Proposition : ajouter « et quelles variables d'environnement il transmet à Claude Code » au choix du plan.

**S6. S2-b : un test pour l'exclusion des pull requests.** `docs/plans/cadrage-s2-issues.md:116` le met au périmètre, mais aucun critère ne le vérifie (`:122`). Si le plan lit l'API REST comme Orca, qui renvoie les PR avec les issues, proposition : « une sortie qui contient une pull request : elle n'est pas listée ».

RELECTURE : CORRECTIONS (1)
