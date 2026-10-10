# Relecture — cadrage `cadrage-s2`, tour 6

Relecteur seul, deux axes. Objet : `docs/plans/cadrage-s2-issues.md` (nouveau) et le diff non commité de `docs/plans/specs-retours-dora-issues.md`, `docs/process/roles/recetteur.md`, `docs/references/orca.md` et `docs/specs/OPEN-QUESTIONS.md`.

## Vérifications faites

- **Carte d'Orca** (`docs/references/orca.md`, lignes 50 à 53) : les huit fichiers ajoutés existent dans le clone du tag `v1.4.218` et disent ce qu'annonce la ligne :
  - `src/main/github/issues.ts` : `listIssues` filtre les entrées qui portent `pull_request` et renvoie `{ items, error }`, donc une erreur n'est pas une liste vide ;
  - `src/main/github/gh-error-classification.ts` : `classifyListIssuesError` ;
  - `src/main/github/auth-diagnose.ts` : `diagnoseGhAuth` relève `ghAvailable` (ENOENT) et les comptes connectés ;
  - `src/shared/workspace-name.ts` : `slugifyForWorkspaceName` remplace tout ce qui sort de `[a-z0-9._-]` par un tiret, sans normalisation des accents ; `getLinkedWorkItemWorkspaceName` présent ;
  - `src/main/ipc/worktree-logic.ts` : `sanitizeWorktreeName` garde `\p{L}\p{N}` et lève une erreur pour un nom vide, `.` ou `..` ;
  - `src/shared/commit-message-agent-specs-primary.ts` : `claude -p --output-format text --permission-mode plan`, prompt sur l'entrée standard ;
  - `src/main/text-generation/source-control-local-process.ts` : délai maximal (`SOURCE_CONTROL_GENERATION_TIMEOUT_MS`) et `killSourceControlAgentProcess` ;
  - `src/main/claude/claude-result-outcome.ts` : `is_error` décide, pas le sous-type ; le fichier est importé par le code des sessions structurées (Agent SDK).
  
  Les entrées déjà présentes et citées par les corps d'issues (`preamble.ts`, `source-control-agent-launch.ts`, `claude-stream-json-frame-schema.ts`, `gh-utils.ts`, `worktree-add.ts`) existent aussi. Aucun chemin du poste dans la carte.
- **État GitHub** (`gh` en lecture) : milestones #1 `E0-S1 Squelette` fermé, #2 `E0-S2 Issue → worktree → un rôle`, #3 `E0-S3 Pipeline jusqu'à la PR`, #4 `E0-S4 Merge et parallélisme`, ouverts, sans échéance, avec les anciennes descriptions courtes : le §1 est exact. Issues #2, #3, #4 ouvertes, chacune dans son milestone. Le label `enhancement` existe (porté par #1).
- **Code cité par S2-a et S2-g** : l'app lance le cœur avec `--db <userData>/jam.db` (`apps/desktop/src/main/index.ts:43`), le cœur suit `JAM_DATA_DIR` seulement sans `--db` (`packages/core/src/paths.ts`), refuse une base plus récente que son code (`packages/core/src/db/database.ts:46-50`), crée le dossier parent de la base, et l'app tue le cœur au bout de 2 s (`apps/desktop/src/main/core-process.ts:39-53`). Les commandes « Lister les repos » et « Ajouter un repo » existent (`packages/core/src/commands.ts`). Les scripts `pnpm check` et `pnpm core:ping` existent.
- **Exigences et ADR** : FR-011, FR-012, FR-020, FR-022, FR-027, FR-028, FR-033, FR-036, FR-038 et NFR-011 existent et sont cités à bon escient. S2-d est conforme à l'ADR 0009 (lecture seule, `git diff/log/status` et commande de tests, sans réseau, jamais `bypassPermissions`). Le §0 et le bloc « Orca » de chaque issue suivent RET-011 et l'ADR 0014. La conduite par orchestrateur de tâche suit les ADR 0013 et 0015.
- **Numérotation** : aucun RET, aucune ADR ajoutés ; Q-052 et Q-053 suivent Q-051.
- **Dépendances** : le tableau du §3 et les lignes « Dépend de » des corps concordent. Les renvois « S2-x » cités au §6 sont bien dans les corps. Le seul « S2- » hors lettres a à h est hors des corps.
- **Repo public** : aucun chemin propre au poste, aucune donnée personnelle, aucune mention d'assistant dans le diff et le brouillon.

## Bloquant

Aucun.

## À corriger

### 1. Une tâche lancée tôt peut trouver la base partagée déjà migrée

- **Fichiers** : `docs/plans/cadrage-s2-issues.md`, ligne 56 (S2-d et S2-f lancées plus tôt) et ligne 60 ; `docs/process/roles/recetteur.md`, ligne 16.
- **Constat** : le §3 ne traite le risque de Q-050 que dans un sens : un worktree plus récent que la base. Le sens inverse n'est pas couvert. S2-d peut être lancée « plus tôt, en parallèle », donc partir de `main` avant le merge de S2-c. Si S2-c est mergée pendant ce temps et que le mainteneur relance son instance depuis `main`, la base partagée passe à la migration 2. La recette de S2-d (« l'app se lance comme avant », ligne 168) tourne sur cette base, puisque le profil du recetteur ne met `JAM_DATA_DIR` que « pour une tâche qui écrit dans la base ». Le cœur de S2-d ne connaît qu'une migration et refuse d'ouvrir la base (`database.ts:46`) : la recette échoue pour une raison étrangère à la tâche. La check-list du mainteneur échoue de même.
- **Correction attendue** :
  - dans `recetteur.md`, ligne 16 : la variable vaut pour toute tâche dont la recette lance l'app ou le cœur, pas seulement pour une tâche qui écrit dans la base ;
  - au §3 : S2-d (et S2-f si sa recette change) n'est lancée plus tôt qu'une fois S2-a mergée, pour que son app suive la variable. Autre possibilité : l'orchestrateur de tâche intègre `main` avant la recette. Le §5 (ligne Q-050) et Q-050 dans `OPEN-QUESTIONS.md` (« Une tâche qui écrit dans la base est recettée avec un dossier de données propre ») suivent la même formulation.

### 2. La vérification des réglages du poste, dans la recette de S2-g, n'est pas observable

- **Fichier** : `docs/plans/cadrage-s2-issues.md`, ligne 248 (« Réglages et hooks du poste… »).
- **Constat** :
  - « aucun contexte d'Orca dans le brief » est toujours vrai. Le brief enregistré est le texte que jam envoie. Le contexte du hook de démarrage est ajouté par Claude Code à la session et n'apparaît jamais dans ce brief, que les réglages soient écartés ou non. Par ailleurs, ce hook n'ajoute le contexte d'Orca que si l'app est lancée depuis un terminal d'Orca.
  - « aucun refus sur `git log`, `git diff` et `git status` », ou « les refus attendus », dépendent de ce que le planificateur décide de lancer. S'il ne lance aucune commande git, les deux branches passent ou échouent sans rien prouver.
- **Correction attendue** : vérifier ce qui se lit dans l'étape enregistrée.
  - Si jam écarte les réglages : la ligne de commande enregistrée contient l'option choisie au plan de S2-d.
  - Sinon : tout refus survenu est enregistré dans l'étape, avec la commande demandée, sans annoncer de « refus attendus ».
  - Si le plan veut prouver l'absence du hook, il désigne un événement du flux (par exemple un événement de hook dans le `stream-json`), pas le brief.

### 3. « Tour » employé hors du sens du glossaire

- **Fichiers** : `docs/plans/cadrage-s2-issues.md`, lignes 216, 218 et 219 (S2-f : « état final du tour », « le tour est réussi », « le tour n'est pas compté comme réussi ») ; `docs/references/orca.md`, ligne 53 (brique « Fin d'un tour : résultat `stream-json` »).
- **Constat** : le glossaire définit le **tour** comme « un aller-retour modèle → éventuels appels d'outils ». Le résultat `stream-json` clôt toute l'exécution headless, qui compte plusieurs tours (le résultat en donne le nombre). S2-g parle d'ailleurs de l'« état final de l'étape ».
- **Correction attendue** : « état final de l'exécution » (ou « du résultat ») dans S2-f, et « Fin d'une exécution headless : résultat `stream-json` » dans la carte. Le bloc « Orca » de S2-f (ligne 227), qui cite l'intitulé de la carte, suit.

## Suggestions

1. **S2-b, ligne 116** : le périmètre exclut les pull requests (ligne 110), mais aucun test ne le vérifie. Si le plan lit l'API REST, qui les renvoie avec les issues (voir la carte), ajouter un cas « réponse contenant une PR ». Un cas « sortie de `gh` mal formée, refusée par zod » serait utile aussi.
2. **S2-c, ligne 142** : ajouter aux tests un titre dont le slug serait vide (seulement des emojis ou de la ponctuation). La carte montre qu'Orca refuse un nom vide ; jam doit dire ce qu'il en fait (nom `<n>` seul, par exemple).
3. **S2-g, lignes 241 et 247** : l'app tue le cœur 2 s après avoir fermé son entrée standard (`core-process.ts:39`). Or, d'après le commentaire de ce fichier, le cœur répond d'abord aux requêtes en cours, et « Lancer le planificateur » en est une. Préciser dans le critère que le cœur arrête Claude Code et répond dans ce délai ; sinon, l'arrêt « normal » devient le cas tué, hors périmètre.
4. **Carte, ligne 53** : `claude-result-outcome.ts` distingue aussi une annulation par `terminal_reason` (`aborted_streaming`, `aborted_tools`). C'est utile pour l'état « interrompue » de S2-g : le mentionner dans la ligne.
5. **S2-c, ligne 134** : le glossaire définit la tâche comme « une issue GitHub qui traverse le pipeline dans son worktree ». « crée une **tâche** : un worktree et sa branche » la réduit à son worktree. Écrire plutôt « crée une **tâche**, avec son worktree et sa branche ».
6. **S2-h, taille** : enchaînement, première vue hors palette, fil résumé et suivi en direct, qui demandera peut-être un nouveau mécanisme du protocole (Q-015, Q-017). Si le plan retient les notifications du cœur vers l'UI, envisager de sortir le suivi en direct dans une issue à part, pour rester un petit lot (ADR 0011).

RELECTURE : CORRECTIONS (3)
