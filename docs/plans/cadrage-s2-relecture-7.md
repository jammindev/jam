# Relecture — cadrage `cadrage-s2`, tour 7

> Relecteur seul (deux axes), contexte neuf. Objet : la rédaction non commitée (`git diff` : `docs/plans/specs-retours-dora-issues.md`, `docs/process/roles/recetteur.md`, `docs/references/orca.md`, `docs/specs/OPEN-QUESTIONS.md`) et le nouveau brouillon `docs/plans/cadrage-s2-issues.md`.

## Vérifications faites

- **Carte d'Orca** (`docs/references/orca.md`, lignes 50 à 53) : les huit fichiers des quatre lignes ajoutées existent dans le clone de référence, vérifié au tag `v1.4.218` (ref du tag et version `1.4.218` du `package.json`). Chaque description correspond au code :
  - `src/main/github/issues.ts` : `listIssues` filtre les entrées qui portent `pull_request`, et une erreur rend `{ items: [], error }` classée par `classifyListIssuesError`, donc distincte d'une liste vide ;
  - `src/main/github/gh-error-classification.ts` définit `classifyListIssuesError` (réexporté par `gh-utils.ts`) ; `src/main/github/auth-diagnose.ts` repère `gh` absent (`ENOENT`) et les comptes connectés ;
  - `src/shared/workspace-name.ts` : `slugifyForWorkspaceName` remplace tout caractère hors `[a-z0-9._-]` par un tiret, lettres accentuées comprises ; `getLinkedWorkItemWorkspaceName` existe ; `src/main/ipc/worktree-logic.ts` : `sanitizeWorktreeName` garde `\p{L}\p{N}` et lève une erreur sur un nom vide, `.` ou `..` ;
  - `src/shared/commit-message-agent-specs-primary.ts` : `claude -p --output-format text --permission-mode plan`, `promptDelivery: 'stdin'` ; `src/main/text-generation/source-control-local-process.ts` : délai `SOURCE_CONTROL_GENERATION_TIMEOUT_MS`, arrêt par `SIGKILL` ;
  - `src/main/claude/claude-result-outcome.ts` : c'est `is_error` qui décide, jamais le sous-type.
  Les entrées existantes citées par les blocs **Orca** des issues (`worktree-add.ts`, `source-control-agent-launch.ts`, `claude-stream-json-frame-schema.ts`, `preamble.ts`, `agent-status-types.ts`) existent aussi au tag.
- **État GitHub** (`gh api 'repos/jammindev/jam/milestones?state=all'`, `gh issue list`) : conforme au §1 et au §2 du brouillon. Milestone #1 `E0-S1 Squelette` fermé ; #2 `E0-S2 Issue → worktree → un rôle`, #3 `E0-S3 Pipeline jusqu'à la PR`, #4 `E0-S4 Merge et parallélisme`, ouverts, sans échéance, avec les anciennes descriptions courtes. Issues #2, #3 et #4 ouvertes, titres conformes au §2.
- **Code cité** : l'app passe `--db <userData>/jam.db` au cœur (`apps/desktop/src/main/index.ts`, `core-process.ts`) ; le cœur suit déjà `JAM_DATA_DIR` en CLI (`packages/core/src/paths.ts`) et crée le dossier de la base ; l'app envoie `SIGKILL` au cœur au bout de 2 s (`STOP_TIMEOUT_MS`). Les affirmations de S2-a et du hors-périmètre de S2-g sont exactes.
- **Couverture du jalon** : chaque élément du critère S2 de `04-ROADMAP.md` est porté par une issue (choix de l'issue et worktree : S2-c, S2-h ; profil ADR 0009 : S2-d ; brief : S2-e ; début et fin de l'étape : S2-g ; fil résumé et redémarrage : S2-h ; fiches worktree et stream-json : S2-c, S2-f). Les textes de milestones du §1 suivent la roadmap.
- **Numérotation** : aucune RET, ni ADR nouvelle ; Q-052 et Q-053 suivent Q-051. Les renvois « S2-x » de `OPEN-QUESTIONS.md` et du profil du recetteur donnent chacun le titre de l'issue.
- **Publication (§6)** : les seuls textes passés en ligne n'ont pas d'apostrophe ; `gh issue close` n'a pas d'option de fichier pour le commentaire ; aucun corps ne contient de « S2- » autre que les renvois à substituer.
- **Repo public** : aucun chemin propre au poste, aucune donnée personnelle, aucune mention d'assistant dans le diff ni dans le brouillon.

## Constats

### Bloquant

Aucun.

### À corriger

1. **`docs/process/roles/recetteur.md`, ligne 9 (et ligne 16)** : la ligne 16 pose que l'orchestrateur de tâche lance **toujours** le recetteur avec `JAM_DATA_DIR=<dossier de recette>/data` devant `claude`, mais la commande du profil, ligne 9, commence toujours par `claude --permission-mode dontAsk …`, sans la variable. Or c'est ce bloc que l'orchestrateur de tâche recopie pour lancer le rôle (process, « Lancement d'un rôle » : `--command '<commande du rôle>'`). Un oubli fait tourner la recette sur la base du mainteneur, ce que Q-050 veut justement empêcher. **Correction attendue** : faire commencer la commande de la ligne 9 par `JAM_DATA_DIR=<dossier de recette>/data claude …`, pour que le bloc et la règle disent la même chose.

2. **`docs/plans/cadrage-s2-issues.md`, ligne 173 (S2-d, critère de fin)** : « la ligne de commande construite pour le planificateur contient exactement les options de son profil » est circulaire. Si le profil est une donnée (Q-012), le test compare la sortie du constructeur à ce que le constructeur a lu, et il passerait avec un profil qui donne l'écriture ou le réseau. Ce critère ne prouve donc pas la conformité à l'ADR 0009, que le jalon exige (« le planificateur est lancé avec son profil de permissions »). **Correction attendue** : faire vérifier par le test la liste attendue, écrite d'après l'ADR 0009 et le périmètre de S2-d : `--permission-mode dontAsk` ; outils de lecture seulement, sans outil d'écriture ; shell limité à `git diff`, `git log`, `git status` et à la commande de tests du repo ; ni `WebSearch` ni `WebFetch`.

### Suggestions

1. **`docs/plans/cadrage-s2-issues.md`, ligne 4, et `docs/plans/specs-retours-dora-issues.md`, ligne 3** : « L'ancien fichier reste tel quel », alors que le diff y ajoute la mention « Remplacé ». Écrire par exemple « reste tel quel, à la mention de remplacement près ».

2. **`docs/plans/cadrage-s2-issues.md`, ligne 64, à rapprocher des lignes 99 et 101 (S2-a), et de `docs/process/roles/recetteur.md`, ligne 16** : la règle « toute recette, de l'agent comme du mainteneur, lance l'app avec `JAM_DATA_DIR` » contredit le critère de S2-a, qui fait lancer à la check-list une instance **sans** la variable. Le cas est sans risque (S2-a n'ajoute pas de migration), mais le recetteur qui suit son profil peut se croire en faute. Ajouter l'exception : « sauf l'étape de S2-a qui vérifie l'instance lancée sans la variable ».

3. **`docs/plans/cadrage-s2-issues.md`, ligne 257 (S2-g, critère de fin)** : le test d'arrêt normal ne borne pas le temps. Or l'app laisse 2 s au cœur avant `SIGKILL` (le hors-périmètre de la ligne 260 le cite) : un cœur qui attend la sortie de Claude Code plus longtemps est tué, et l'agent devient orphelin malgré un test vert. Ajouter au critère : « le cœur sort avant le délai que l'app lui laisse (2 s) ».

4. **`docs/plans/cadrage-s2-issues.md`, ligne 148 (S2-c, tests)** : ajouter le cas d'un titre dont le slug est vide (un titre fait seulement d'émojis ou de lettres accentuées, si le plan suit Orca qui les remplace par des tirets) : le nom reste valide, sans tiret final. La carte relève déjà que `getLinkedWorkItemWorkspaceName` renvoie `null` dans ce cas.

5. **`docs/references/orca.md`, ligne 53** : `claude-result-outcome.ts` distingue aussi une **annulation** d'un échec (`is_error` avec `terminal_reason` `aborted_streaming` ou `aborted_tools`). Cela touche l'état « interrompue » de S2-g et l'état final de S2-f : à mentionner dans la parenthèse de la ligne, pour que le planificateur de S2-f le lise.

6. **`docs/plans/cadrage-s2-issues.md`, lignes 247 à 252 (S2-g) et 272 à 275 (S2-h)** : ce sont les deux plus gros lots. S2-g porte le lancement, une migration, une commande de palette, l'arrêt de l'enfant et le marquage au démarrage. S2-h ajoute peut-être des notifications au protocole (Q-015, Q-017). Le §3 pourrait dire qu'un plan qui dépasse un petit lot (ADR 0011) le signale au feu vert plan, par exemple en sortant l'arrêt de l'enfant (R-02) de S2-g, ou les notifications de S2-h.

7. **`docs/specs/OPEN-QUESTIONS.md`, Q-053** : la liste des recettes qui passent par la palette omet S2-a (« Lister les repos » reste à la check-list, ligne 101 du brouillon). Sans effet sur le critère principal de S2-a, que l'agent vérifie (`jam.db` créé) ; à ajouter pour que la liste soit complète.

RELECTURE : CORRECTIONS (2)
