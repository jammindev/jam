# Relecture — cadrage `cadrage-s2`, tour 11

Relecteur seul (les deux axes), contexte neuf. Objet : la rédaction non commitée, soit `docs/plans/cadrage-s2-issues.md` (nouveau) et le diff de `docs/plans/specs-retours-dora-issues.md`, `docs/process/roles/recetteur.md`, `docs/references/orca.md` et `docs/specs/OPEN-QUESTIONS.md`.

## Vérifications faites

- **Carte d'Orca** (§0 de `docs/references/orca.md`, quatre lignes ajoutées) : les huit fichiers cités existent au tag `v1.4.218` (clone de référence en lecture seule), et chaque parenthèse correspond au code :
  - `src/main/github/issues.ts` : `listIssues` filtre les entrées qui portent `pull_request` et renvoie `{ items, error }`, une erreur n'étant pas confondue avec une liste vide ;
  - `src/main/github/gh-error-classification.ts` : `classifyListIssuesError` y est défini ;
  - `src/main/github/auth-diagnose.ts` : `gh` absent (ENOENT) et lecture de `gh auth status` ;
  - `src/shared/workspace-name.ts` : `slugifyForWorkspaceName` remplace tout caractère hors `[a-z0-9._-]` par un tiret, donc une lettre accentuée aussi ; `getLinkedWorkItemWorkspaceName` existe ;
  - `src/main/ipc/worktree-logic.ts` : `sanitizeWorktreeName` garde `\p{L}\p{N}` et lève une erreur sur un nom vide, `.` ou `..` ;
  - `src/shared/commit-message-agent-specs-primary.ts` : `claude -p --output-format text … --permission-mode plan`, prompt sur l'entrée standard (`promptDelivery: 'stdin'`) ;
  - `src/main/text-generation/source-control-local-process.ts` : délai maximal (`SOURCE_CONTROL_GENERATION_TIMEOUT_MS`) et arrêt de l'enfant (`SIGKILL`) ;
  - `src/main/claude/claude-result-outcome.ts` : `is_error` décide, jamais le sous-type ; le commentaire rattache le fichier aux résultats de l'Agent SDK.
- **État GitHub** (`gh` en lecture) : milestone #1 `E0-S1 Squelette` fermé ; #2, #3 et #4 ouverts, sans échéance, avec les descriptions courtes d'origine ; #4 s'appelle encore `E0-S4 Merge et parallélisme`. Les issues #2 « Issue → worktree → un rôle », #3 « Pipeline jusqu'à la PR » et #4 « Merge, nettoyage et parallélisme » sont ouvertes ; le label `enhancement` existe (porté par #2). Les affirmations du §1 et du §2 sont exactes.
- **Code de jam** cité par les issues : l'app passe `--db <userData>/jam.db` au cœur (`apps/desktop/src/main/index.ts`), le cœur en CLI suit `JAM_DATA_DIR` (`packages/core/src/paths.ts`), le cœur refuse une base d'une version plus récente que son code (`packages/core/src/db/database.ts`), l'app laisse 2 s au cœur avant `SIGKILL` (`apps/desktop/src/main/core-process.ts`), et `serve` attend chaque réponse en cours avant de se terminer (`packages/core/src/server.ts`). Les justifications de S2-a et de S2-g tiennent.
- **Exigences et ADR** : FR-011, FR-012, FR-020, FR-022, FR-027, FR-028, FR-033, FR-036, FR-038 et NFR-011 existent et sont cités à bon escient. Le profil du planificateur suit la ligne de l'ADR 0009 (lecture seule, `git diff/log/status`, commande de tests, pas de réseau). Les migrations suivent l'ADR 0010. La conduite par un orchestrateur de tâche et la carte seule suivent les ADR 0013 et 0015 ; la section « Orca » de chaque issue suit RET-011 et l'ADR 0014. La recette de chaque issue suit RET-010.
- **Numérotation** : Q-052 et Q-053 suivent Q-051 ; ni RET ni ADR nouveaux. Aucune référence restante aux lettres de l'ancien brouillon hors de `docs/plans/` : les renvois S2-x de `OPEN-QUESTIONS.md` et du profil du recetteur donnent le titre de l'issue.
- **Repo public** : aucun chemin propre au poste, aucune donnée personnelle, aucune mention d'assistant dans les fichiers relus.
- **Taille des lots** (ADR 0011) : huit issues, chacune avec un critère de fin vérifiable ; dépendances et migrations (S2-c, S2-g seulement) cohérentes entre le §3 et les sections d'issue.

## Bloquant

Aucun.

## À corriger

Aucun.

## Suggestions

1. **`docs/plans/cadrage-s2-issues.md`, ligne 100 (S2-a, critère de fin)** : le recetteur est désormais toujours lancé avec `JAM_DATA_DIR`, et `pnpm check` en hérite. Un test « sans la variable » qui lirait l'environnement du processus échouerait donc à la recette. Correction proposée : préciser que les tests du chemin de la base passent l'environnement en paramètre, comme `packages/core/test/paths.test.ts`, et ne lisent pas celui du processus.
2. **`docs/process/roles/recetteur.md`, ligne 16** : « Les commandes du recetteur (`pnpm dev`, `pnpm core:ping`) en héritent » laisse croire que `pnpm core:ping` touche une base. Or le script lance le cœur avec `--db :memory:` (`packages/core/package.json`), et la variable n'a aucun effet sur lui. Correction proposée : ne citer que `pnpm dev`, ou préciser que `core:ping` n'ouvre aucune base de fichier. Le même détail vaut pour Q-053 (`OPEN-QUESTIONS.md`, ligne 51) : un script « sur le modèle de `core:ping` » devra viser la base de `JAM_DATA_DIR`, pas `:memory:`, pour voir les repos et les tâches de la recette.
3. **`docs/plans/cadrage-s2-issues.md`, ligne 174 (S2-d, critère de fin)** : « aucune ligne de commande construite, quel que soit le profil, ne contient `bypassPermissions` » ne se teste pas sur tous les profils. Correction proposée : « un profil qui demande `bypassPermissions` ou `--dangerously-skip-permissions` est refusé, et le mode de permission de la ligne construite est toujours `dontAsk` ». C'est vérifiable par un cas de test.
4. **`docs/plans/cadrage-s2-issues.md`, lignes 247 à 252 (S2-g, périmètre)** : c'est l'issue la plus lourde du jalon : lancement, migration des étapes, commande de palette, arrêt propre sur fermeture de l'entrée standard et sur signal (avec un changement de `serve`), marquage des étapes interrompues au démarrage, essai réel. Elle reste un petit lot au sens du glossaire, mais l'arrêt sans agent orphelin (R-02) formerait une issue autonome, après S2-g. À trancher par le mainteneur s'il veut des lots plus fins. Sinon, rien à changer.

RELECTURE : OK
