# Relecture — cadrage `cadrage-s2`, tour 8

Relecteur seul (les deux axes). Objet : la rédaction non commitée (`git diff` sur `docs/plans/specs-retours-dora-issues.md`, `docs/process/roles/recetteur.md`, `docs/references/orca.md`, `docs/specs/OPEN-QUESTIONS.md`) et le nouveau fichier `docs/plans/cadrage-s2-issues.md`.

## Vérifications faites

- **Carte d'Orca** (`docs/references/orca.md`, §0, quatre lignes ajoutées) : les huit fichiers cités existent au tag `v1.4.218` (clone de référence en lecture seule), et chaque précision entre parenthèses correspond au code :
  - `src/main/github/issues.ts` : `listIssues` filtre les entrées qui portent `pull_request` et renvoie une erreur classée (`classifyListIssuesError`) au lieu d'une liste vide ;
  - `src/main/github/gh-error-classification.ts` : `classifyListIssuesError` existe ;
  - `src/main/github/auth-diagnose.ts` : `ghAvailable` à faux quand `gh` est introuvable, aucun compte quand `gh` n'est pas authentifié (voir suggestion 5) ;
  - `src/shared/workspace-name.ts` : `slugifyForWorkspaceName` remplace tout caractère hors `[a-z0-9._-]` par un tiret, sans normalisation des accents ; `getLinkedWorkItemWorkspaceName` existe ;
  - `src/main/ipc/worktree-logic.ts` : `sanitizeWorktreeName` garde `\p{L}\p{N}` et lève une erreur sur un nom vide, `.` ou `..` ;
  - `src/shared/commit-message-agent-specs-primary.ts` : `-p --output-format text --permission-mode plan`, prompt sur l'entrée standard (`promptDelivery: 'stdin'`) ;
  - `src/main/text-generation/source-control-local-process.ts` : délai maximal (`SOURCE_CONTROL_GENERATION_TIMEOUT_MS`) et arrêt de l'enfant (`killSourceControlAgentProcess`) ;
  - `src/main/claude/claude-result-outcome.ts` : `is_error` décide, pas le sous-type ; importé par les fichiers de sessions structurées.
- **État GitHub** (`gh` en lecture) : milestone #1 `E0-S1 Squelette` fermé ; #2, #3, #4 ouverts, sans échéance ; #4 porte encore le titre `E0-S4 Merge et parallélisme` ; descriptions en ligne plus courtes que celles du §1, non mises à jour depuis le 2026-10-08. Issues #2, #3, #4 ouvertes, label `enhancement` présent. Le §1 et le §2 de `cadrage-s2-issues.md` sont exacts.
- **Faits sur le code de jam** cités par les issues : l'app ouvre `join(app.getPath('userData'), 'jam.db')` et le passe au cœur par `--db` ; le cœur en CLI suit `JAM_DATA_DIR` ; la migration refuse une base de version plus récente que le code ; l'app ferme l'entrée standard du cœur puis envoie `SIGKILL` au bout de 2 s ; le cœur crée le dossier de la base (`mkdirSync` récursif), donc `<dossier de recette>/data` n'a pas à exister ; les commandes de palette « Ajouter un repo » et « Lister les repos » existent.
- **Numérotation** : Q-052 et Q-053 suivent Q-051 ; aucun nouveau RET ni nouvelle ADR.
- **Cohérence** avec les ADR 0009 (planificateur en lecture seule, jamais sans permission), 0010 (migrations numérotées), 0011 (petits lots), 0013 et 0015 (une tâche, un orchestrateur, carte seule), 0014 et RET-011 (bloc « Orca » par issue, liste noire), RET-010 (installation neuve, check-list d'abord) : conforme. Les écarts à RET-010 (critère principal laissé au mainteneur faute de clavier) sont dits dans chaque issue et tracés par Q-053.
- **Glossaire** : tâche, étape, rôle, feu vert, brouillon d'issue, clone de référence employés dans leur sens.
- **Repo public** : aucun chemin propre au poste, aucune donnée personnelle nouvelle, aucune mention d'assistant dans le diff ni dans le nouveau fichier.
- Commandes `gh` du §6 : `-F description=@<fichier>` lit bien le fichier ; `gh issue close` n'a pas d'option de fichier pour son commentaire ; `--reason 'not planned'` est une valeur admise.

## Bloquant

Aucun.

## À corriger

1. **`docs/plans/cadrage-s2-issues.md`, ligne 4** : « L'ancien fichier reste tel quel, comme trace de son cadrage. » Or le diff modifie l'ancien fichier (`docs/plans/specs-retours-dora-issues.md`, ligne 3 : note « Remplacé pour les §1 à §3 par … »). La phrase contredit la rédaction elle-même.
   **Correction attendue** : par exemple « L'ancien fichier reste, comme trace de son cadrage, avec en tête un renvoi vers celui-ci. »

## Suggestions

1. **`docs/process/roles/recetteur.md`, ligne 16** : « Les commandes du recetteur (`pnpm dev`, `pnpm core:ping`) en héritent ». `pnpm core:ping` lance le cœur avec `--db :memory:` (`packages/core/package.json`) : il n'a jamais touché de base, la variable n'y change rien. Citer `pnpm dev` seul, ou préciser que `core:ping` n'ouvre aucune base.
2. **`docs/plans/cadrage-s2-issues.md`, ligne 174** (S2-d) : « aucune ligne de commande construite, quel que soit le profil, ne contient `bypassPermissions` » n'est pas vérifiable tel quel (un test ne parcourt pas tous les profils possibles). Forme vérifiable : « un profil qui demande `bypassPermissions` ou `--dangerously-skip-permissions` est refusé par le constructeur, avec un message lisible ».
3. **`docs/plans/cadrage-s2-issues.md`, ligne 257** (S2-g) : « Un test arrête normalement le cœur pendant l'étape (entrée standard fermée, puis signal d'arrêt) » se lit comme une seule séquence. Écrire « deux cas : entrée standard fermée ; signal d'arrêt », puisque le périmètre (ligne 251) les donne comme deux façons distinctes de s'arrêter.
4. **`docs/plans/cadrage-s2-issues.md`, ligne 280** (S2-h) : « l'app reste utilisable pendant l'étape » est flou pour une check-list. Proposer un fait observable, par exemple « pendant l'étape, Cmd+K s'ouvre et « Lister les repos » répond ».
5. **`docs/references/orca.md`, ligne 50** : `auth-diagnose.ts` traite surtout des scopes manquants et du jeton d'environnement qui masque le trousseau ; « `gh` absent ou non authentifié » n'en est qu'une partie (`ghAvailable`, liste de comptes vide). Ajouter « (le reste du fichier traite des scopes, propres à Orca) » éviterait au planificateur de le lire en entier.
6. **Taille de S2-g et S2-h** (`docs/plans/cadrage-s2-issues.md`, lignes 239 à 287) : S2-g réunit lancement, migration des étapes, commande de palette, arrêt propre et marquage des étapes interrompues ; S2-h, l'enchaînement, la vue de la tâche, le fil et le suivi en direct (dont, peut-être, les notifications du cœur vers l'UI, Q-015). Les deux restent plausibles en quelques jours, mais une phrase pourrait dire que le plan propose un redécoupage s'il dépasse un petit lot (ADR 0011), par exemple l'arrêt propre et l'étape interrompue pour S2-g.

RELECTURE : CORRECTIONS (1)
