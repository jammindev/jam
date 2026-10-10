# Relecture — cadrage `cadrage-s2`, tour 3

> Relecteur seul (les deux axes), contexte neuf. Objet : `docs/plans/cadrage-s2-issues.md` (nouveau) et le diff non commité de `docs/plans/specs-retours-dora-issues.md`, `docs/process/roles/recetteur.md`, `docs/references/orca.md`, `docs/specs/OPEN-QUESTIONS.md`.

## Vérifications faites

- **Carte d'Orca** (`docs/references/orca.md`, lignes 50 à 53) : les neuf fichiers ajoutés existent dans le clone du tag `v1.4.218`, et chaque parenthèse correspond au code :
  - `src/main/github/issues.ts` : `listIssues` filtre les entrées qui portent `pull_request` et renvoie `{ items: [], error }` en cas d'échec, distinct d'une liste vide ;
  - `src/main/github/gh-error-classification.ts` : `classifyListIssuesError` existe ;
  - `src/main/github/auth-diagnose.ts` : `diagnoseGhAuth` repère `gh` absent (`ghAvailable`) et les comptes connectés ;
  - `src/shared/workspace-name.ts` : `slugifyForWorkspaceName` remplace tout caractère hors `[a-z0-9._-]` par un tiret, sans normalisation des accents ; `getLinkedWorkItemWorkspaceName` existe ;
  - `src/main/ipc/worktree-logic.ts` : `sanitizeWorktreeName` garde `\p{L}\p{N}` et lève une erreur pour un nom vide, `.` ou `..` ;
  - `src/shared/commit-message-agent-specs-primary.ts` : `-p --output-format text --permission-mode plan`, `promptDelivery: 'stdin'` ;
  - `src/main/text-generation/source-control-local-process.ts` : délai maximal (`SOURCE_CONTROL_GENERATION_TIMEOUT_MS`) et `child.kill('SIGKILL')` ;
  - `src/main/claude/claude-result-outcome.ts` : `is_error` décide, pas le sous-type ;
  - `src/main/runtime/orchestration/preamble.ts` : existe (entrée déjà présente sur `main`).

  « Les quatre dernières lignes » correspond bien aux quatre lignes ajoutées. Le chemin du clone n'apparaît nulle part dans le repo.
- **État GitHub** (`gh api 'repos/jammindev/jam/milestones?state=all'`, `gh issue list`) : milestone #1 fermé ; #2 et #3 aux titres annoncés ; #4 encore intitulé `E0-S4 Merge et parallélisme` ; descriptions en ligne courtes, anciennes ; aucune échéance. Issues #2, #3, #4 ouvertes, label `enhancement`, chacune dans son milestone. PR #6 mergée. Le §1 et le §2 du brouillon sont exacts.
- **Code cité** : l'app passe `--db <userData>/jam.db` au cœur (`apps/desktop/src/main/index.ts:43`, `core-process.ts:25`) ; le cœur suit `JAM_DATA_DIR` sans `--db` (`packages/core/src/paths.ts:10`) et refuse une base plus récente (`database.ts:50`) ; l'app envoie `SIGKILL` au bout de 2 s (`core-process.ts:39-46`) ; `pnpm core:ping` existe. Les affirmations de S2-a, S2-g et Q-050 tiennent.
- **Numérotation** : Q-052 et Q-053 suivent Q-051 ; aucun RET ni ADR nouveau.
- **Repo public** : aucun chemin propre au poste, aucune donnée personnelle, aucune mention d'assistant dans les fichiers relus.
- **Cohérence** : ADR 0009 (planificateur en lecture seule, plan rendu comme texte final, sans réseau), ADR 0010 (migrations numérotées, deux seulement, en série), ADR 0011 (petits lots, découpage motivé), ADR 0013 et 0015 (conduite par un orchestrateur de tâche, publication par le coordinateur après merge), ADR 0014 et RET-011 (bloc « Orca » par issue, liste noire), RET-010 (installation neuve, check-list d'abord) : rien de contraire relevé. Le §6 (publication) est exécutable tel quel : textes passés par fichier, titres de milestones inline sans apostrophe, deux passes pour les renvois.

## Bloquant

Aucun.

## À corriger

1. **L'état de l'étape n'est observable par personne à la recette** — `docs/plans/cadrage-s2-issues.md:243` (S2-g) et `:267` (S2-h).
   - Le critère principal de S2-g est « L'état de l'étape contient la ligne de commande, le brief (…), l'identifiant de session, le coût et les heures de début et de fin ». Or S2-g n'ajoute aucun moyen de lire une étape : « Lister les tâches » (S2-c) montre des tâches, et la vue de la tâche n'arrive qu'avec S2-h. Le recetteur n'a pas de `sqlite3`, et l'essai réel est de toute façon à la check-list du mainteneur, qui ne peut pas vérifier ce qu'il ne voit pas.
   - S2-h écrit « visible dans l'état de l'étape », alors que son périmètre (ligne 262) ne met dans la vue que l'étape, son état et son fil, pas la ligne de commande.
   - Correction attendue : dire dans S2-g par quel moyen le mainteneur lit l'étape (par exemple : « Lancer le planificateur » affiche, à la fin de l'étape, l'étape enregistrée, ou une commande de palette montre la dernière étape d'une tâche ; à défaut, une commande `sqlite3` donnée dans la check-list), et dans S2-h, soit ajouter la ligne de commande à la vue de la tâche, soit écrire « visible dans la vue de la tâche » à la place de « dans l'état de l'étape ».

2. **« Relevés dans le rapport » : une consigne que le recetteur ne peut pas suivre** — `docs/plans/cadrage-s2-issues.md:143` (S2-c), `:246` (S2-g), `:270` (S2-h).
   - Chaque recette dit que « le worktree et la branche créés dans `house` (…) sont relevés dans le rapport », puis, quelques mots plus loin, que l'agent ne peut ni ajouter `house` ni créer la tâche sans clavier. Le recetteur ne crée donc aucun worktree : il n'a rien à relever, et son rapport est écrit avant que le mainteneur déroule sa check-list. Un recetteur ou un orchestrateur de tâche qui lit la consigne à la lettre cherchera un worktree qui n'existe pas.
   - Correction attendue : attribuer le relevé à la check-list du mainteneur, par exemple « La check-list fait noter au mainteneur le chemin du worktree et le nom de la branche créés dans `house`, et se termine par leur suppression, avec les commandes à lancer. »

3. **S2-f : issue d'un flux qui contient une ligne invalide, ambiguë** — `docs/plans/cadrage-s2-issues.md:217`.
   - « Un test couvre une ligne invalide et un flux coupé avant son résultat : le tour n'est pas compté comme réussi. » Deux lectures : la ligne invalide fait elle aussi échouer le tour, ou seule la coupure le fait. Le périmètre (ligne 211) dit seulement qu'une ligne invalide n'arrête pas la lecture. Les deux lectures donnent des tests et un comportement différents : un flux réel réussi qui contient une ligne d'un type nouveau serait compté en échec dans la première.
   - Correction attendue : séparer les deux cas, par exemple « Un test couvre une ligne invalide au milieu d'un flux réussi : la lecture continue, les événements suivants sont normalisés et le tour est réussi. Un autre couvre un flux coupé avant son résultat : le tour n'est pas compté comme réussi. »

## Suggestions

1. **`--verbose` avec `stream-json`** — `docs/plans/cadrage-s2-issues.md:159` (S2-d). La liste d'options entre parenthèses se lit comme exhaustive, et le critère (ligne 165) demande « exactement les options de son profil ». Claude Code demande sans doute `--verbose` avec `-p --output-format stream-json` (Orca le passe partout où il lit ce format, par exemple `src/shared/claude-model-list-probe.ts` au tag). Écrire « notamment » ou ajouter `--verbose`, à vérifier sur la version testée (R-04), éviterait un test vert sur une commande que l'essai réel de S2-g refuserait.
2. **Description du milestone E0-S4 et la fiche concept** — `docs/plans/cadrage-s2-issues.md:29`. La roadmap (`04-ROADMAP.md:46`) dit que la seconde phrase **et** la fiche « métriques DORA » tombent si l'écran est coupé ; le brouillon ne fait tomber que le critère. Le texte se dit « aligné sur `04-ROADMAP.md` » (ligne 20) : écrire « Ce second critère, comme la fiche concept, tombe si l'écran est coupé ».
3. **« L'ancien fichier reste tel quel »** — `docs/plans/cadrage-s2-issues.md:4`, alors que le diff ajoute une note en tête de `specs-retours-dora-issues.md` (ligne 3). Écrire « L'ancien fichier reste, avec une note qui renvoie ici, comme trace de son cadrage ».
4. **`pnpm core:ping` n'hérite de rien** — `docs/process/roles/recetteur.md:16`. Le script tourne sur `--db :memory:` (`packages/core/package.json:13`) : `JAM_DATA_DIR` ne change rien pour lui. Citer seulement `pnpm dev`, ou préciser que `core:ping` ne touche aucune base.
5. **ADR 0010 et ce que l'étape enregistre** — `docs/plans/cadrage-s2-issues.md:237`. L'ADR 0010 dit que l'outil « ne garde que l'identifiant de session de chaque étape, plus un résumé d'événements » ; S2-g enregistre en plus le brief et le texte final du résultat (le plan). Ce n'est pas une transcription, et l'ADR vise les transcriptions détaillées, mais une demi-phrase le dirait au planificateur et au relecteur de conformité de S2-g : « le brief et le texte final sont des données de l'étape, pas une transcription (ADR 0010) ».

RELECTURE : CORRECTIONS (3)
