# Relecture — cadrage `cadrage-s2`, tour 9

Relecteur seul (les deux axes), contexte neuf. Objet relu : `git diff` (quatre fichiers) et le nouveau fichier `docs/plans/cadrage-s2-issues.md`.

## Vérifications faites

- **Carte d'Orca** (§0 de `docs/references/orca.md`, quatre lignes ajoutées) : les sept fichiers cités existent au tag `v1.4.218` (clone superficiel du tag, en lecture seule) et disent ce que la ligne annonce :
  - `src/main/github/issues.ts` : `listIssues` filtre les entrées qui portent `pull_request` ; une erreur `gh` renvoie `items: []` avec un champ `error` (`classifyListIssuesError`), distinct d'une liste vide ;
  - `src/main/github/gh-error-classification.ts` : `classifyListIssuesError` existe ;
  - `src/main/github/auth-diagnose.ts` : `gh auth status`, `ghAvailable` à faux si `gh` est absent, comptes vides si non authentifié ;
  - `src/shared/workspace-name.ts` : `slugifyForWorkspaceName` remplace tout caractère hors `[a-z0-9._-]` par un tiret, sans normalisation des accents (une lettre accentuée devient bien un tiret) ; `getLinkedWorkItemWorkspaceName` existe ;
  - `src/main/ipc/worktree-logic.ts` : `sanitizeWorktreeName` garde `\p{L}\p{N}` et lève une erreur sur un nom vide, `.` ou `..` (sauf nom fait d'émojis, ramené à `workspace` : détail sans effet sur la ligne) ;
  - `src/shared/commit-message-agent-specs-primary.ts` : `claude -p --output-format text … --permission-mode plan`, `promptDelivery: 'stdin'` ;
  - `src/main/text-generation/source-control-local-process.ts` : délai maximal (`SOURCE_CONTROL_GENERATION_TIMEOUT_MS`) et arrêt par `SIGKILL` ;
  - `src/main/claude/claude-result-outcome.ts` : `is_error` décide, pas le sous-type ; le fichier n'est importé que par les modules de sessions structurées (Agent SDK).
  
  Les noms d'entrées cités dans les blocs **Orca** des huit issues correspondent exactement aux libellés du tableau.
- **État GitHub** (`gh` en lecture) : milestones #1 (fermé), #2, #3, #4 ouverts ; titre de #4 encore `E0-S4 Merge et parallélisme` ; descriptions en ligne plus courtes que les textes du §1, comme l'affirme le brouillon. Issues #2, #3, #4 ouvertes ; label `enhancement` présent (sur #2). Aucune date d'échéance.
- **Code du repo** cité par le brouillon : l'app passe `--db <userData>/jam.db` au cœur (`apps/desktop/src/main/index.ts`, `core-process.ts`) ; le cœur en CLI suit `JAM_DATA_DIR` et crée le dossier (`mkdirSync`) ; il refuse une base « written by a newer version of jam » (`database.ts`) ; l'app envoie `SIGKILL` au bout de 2 s si le cœur ne s'est pas arrêté ; la commande « Lister les repos » existe (`commands.ts`).
- **Exigences et ADR** : FR-011, FR-012, FR-020, FR-022, FR-027, FR-028, FR-033, FR-036, FR-038 et NFR-011 correspondent à ce que les issues leur font porter. Profil du planificateur conforme à l'ADR 0009 (lecture seule, `git diff/log/status`, commande de tests, pas de réseau, `dontAsk`). Conduite par un orchestrateur de tâche et remontée par la carte conformes aux ADR 0013 et 0015 ; consultation d'Orca par issue et liste noire conformes à RET-011 et à l'ADR 0014. Recettes conformes à RET-010 (installation neuve, check-list du mainteneur d'abord), écarts dus au clavier signalés et renvoyés à Q-053.
- **Roadmap** : chaque point du critère de fin du S2 est porté par une issue (choix de l'issue et plan affiché : S2-h ; profil : S2-d, S2-g ; brief : S2-e ; heures de l'étape : S2-g ; fil : S2-h ; redémarrage : S2-c, S2-h ; fiches : S2-c, S2-f).
- **Petits lots** (ADR 0011) : découpage justifié au §3 ; dépendances et migrations cohérentes (S2-c puis S2-g, seules à migrer).
- **Publication** (§6) : `gh api -X PATCH … -F description=@<fichier>`, `--title "$(cat …)"`, `--body-file`, commentaire avant `gh issue close --reason 'not planned'` : syntaxe correcte ; ordre milestones → issues → fermetures cohérent avec les renvois des commentaires.
- **Numérotation** : Q-052 et Q-053 suivent Q-051 ; aucun RET ni ADR ajouté.
- **Repo public** : aucun chemin propre au poste, aucune donnée personnelle, aucune mention d'assistant dans le diff ni dans le brouillon.

## Constats

### Bloquant

Aucun.

### À corriger

1. **`docs/specs/OPEN-QUESTIONS.md`, ligne 44 (Q-040)** ; voir aussi `docs/plans/cadrage-s2-issues.md`, ligne 297.
   Q-040 reste « Process / E0 S2 » et dit « À traiter avec Q-012 ». Or le cadrage renvoie Q-012 au plan de S2-d (ligne 16 de `OPEN-QUESTIONS.md`) et décide, au §5 du brouillon, que Q-040 ne pèse pas sur S2-d (`house` n'a pas de référence de lecture). Cette décision ne figure que dans le brouillon (colonne « Où » : « — »). Le planificateur de S2-d, qui lira Q-012 et Q-040 dans `OPEN-QUESTIONS.md`, croira devoir trancher les deux ensemble.
   **Correction attendue** : reporter dans le statut de Q-040 la décision du §5 (« Laissée ouverte par `cadrage-s2` : le S2 lance le planificateur sur `house`, sans référence de lecture ; le plan de S2-d tranche Q-012 sans elle »), et mettre `OPEN-QUESTIONS.md` dans la colonne « Où » de la ligne Q-040 du §5.

### Suggestions

1. **`docs/process/roles/recetteur.md`, ligne 16** : « Les commandes du recetteur (`pnpm dev`, `pnpm core:ping`) en héritent ». `pnpm core:ping` lance le cœur avec `--db :memory:` (`packages/core/package.json`) : il n'ouvre aucune base fichier, avec ou sans la variable. Proposition : ne citer que `pnpm dev` (et `pnpm check`, dont les tests héritent aussi de l'environnement), ou préciser que `core:ping` ne touche aucune base.
2. **`docs/plans/cadrage-s2-issues.md`, lignes 251 et 257 (S2-g)** : le serveur du cœur, quand son entrée standard se ferme, attend la fin de toutes les requêtes en cours avant de sortir (`packages/core/src/server.ts`, « Resolves once `input` has ended and every pending response is written »). Si « Lancer le planificateur » est une requête qui dure le temps de l'étape, un arrêt normal attendra la fin de l'étape, et l'app tuera le cœur au bout de 2 s : le cas « cœur tué », hors périmètre, deviendrait le cas courant. Le test du critère de fin attrape l'absence d'arrêt, mais pas le délai. Proposition : ajouter aux « Questions renvoyées au plan » de S2-g que l'arrêt sur fermeture de l'entrée standard doit interrompre l'étape en cours (et non l'attendre), dans le délai de 2 s de l'app.

RELECTURE : CORRECTIONS (1)
