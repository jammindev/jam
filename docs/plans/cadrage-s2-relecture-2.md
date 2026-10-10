# Relecture — cadrage `cadrage-s2`, tour 2

> Relecteur seul (les deux axes), contexte neuf. Objet : `git diff` (quatre fichiers modifiés) et le nouveau `docs/plans/cadrage-s2-issues.md`.
> Lus : `AGENTS.md`, `docs/process/README.md`, profils du relecteur, du rédacteur, du planificateur et du recetteur, `01-REQUIREMENTS.md`, `04-ROADMAP.md`, `GLOSSARY.md`, `OPEN-QUESTIONS.md`, `RETOURS.md` (RET-010, RET-011), ADR 0009, 0010, 0011, 0014, la note `docs/references/orca.md`, l'ancien brouillon `specs-retours-dora-issues.md`.

## Vérifications faites, sans constat

- **Carte d'Orca** (`docs/references/orca.md:50-53`) : les huit fichiers des quatre lignes ajoutées existent au tag `v1.4.218` et disent bien ce que la ligne annonce :
  - `src/main/github/issues.ts` : `listIssues` filtre les entrées qui portent `pull_request` et renvoie l'erreur classée au lieu d'une liste vide ;
  - `src/main/github/gh-error-classification.ts` : `classifyListIssuesError` ;
  - `src/main/github/auth-diagnose.ts` : `ghAvailable` (`gh` absent) et liste des comptes de `gh auth status` ;
  - `src/shared/workspace-name.ts` : `slugifyForWorkspaceName` remplace tout ce qui sort de `[a-z0-9._-]` par un tiret, sans normalisation Unicode, donc une lettre accentuée devient un tiret ; `getLinkedWorkItemWorkspaceName` existe ;
  - `src/main/ipc/worktree-logic.ts` : `sanitizeWorktreeName` garde `\p{L}\p{N}` et lève une erreur sur un nom vide, `.` ou `..` ;
  - `src/shared/commit-message-agent-specs-primary.ts` : `claude -p --output-format text --permission-mode plan`, prompt sur l'entrée standard ;
  - `src/main/text-generation/source-control-local-process.ts` : délai maximal et `killSourceControlAgentProcess` ;
  - `src/main/claude/claude-result-outcome.ts` : `is_error` décide, pas le sous-type ; fichier des sessions de l'Agent SDK.

  Le chemin du clone n'apparaît nulle part dans le repo.
- **État GitHub** (`gh api 'repos/jammindev/jam/milestones?state=all'`, `gh issue list`) : milestone #1 fermé ; #2 et #3 aux titres annoncés ; #4 encore intitulé `E0-S4 Merge et parallélisme` ; les quatre descriptions en ligne sont les anciennes, plus courtes ; aucune date d'échéance. Issues #2, #3 et #4 ouvertes, aux titres du §2. PR #6 = `specs-retours-dora` (historique git). Les affirmations du §1 et du §2 sont exactes.
- **Code cité** : l'app passe `--db <userData>/jam.db` au cœur (`apps/desktop/src/main/index.ts:43`, `core-process.ts:25`) ; `productName` vaut `jam`, donc le dossier par défaut de l'app et celui du cœur en CLI coïncident ; le cœur refuse une base plus récente (`packages/core/src/db/database.ts:50`) ; l'app envoie `SIGKILL` au bout de 2 s (`core-process.ts:39-46`) ; la commande « Lister les repos » existe (`packages/core/src/commands.ts:12`).
- **Numérotation** : seule Q-052 est ajoutée ; aucune nouvelle RET ni ADR. Rien n'est réutilisé.
- **Repo public** : aucun chemin propre au poste, aucune donnée personnelle, aucune mention d'assistant. Les mentions de « Claude Code » désignent le backend d'agent.
- **ADR** : le planificateur sans écriture (S2-d) applique la lecture seule de l'ADR 0009 ; le profil sans réseau tranche Q-027 pour jam sans contourner l'ADR ; chaque issue est conduite par un orchestrateur de tâche (ADR 0013, 0015) ; RET-010 est repris dans chaque critère de recette.

## Bloquant

Aucun.

## À corriger

### 1. Publication : les renvois vers des issues pas encore créées ne peuvent pas être substitués

- **Fichier** : `docs/plans/cadrage-s2-issues.md:303` (et `:7`).
- **Constat** : l'étape 2 du §6 crée les issues dans l'ordre S2-a → S2-h « pour que chaque renvoi pointe vers une issue déjà créée », et remplace chaque « S2-x » avant la création. Or plusieurs corps renvoient à des issues **suivantes** :
  - S2-b → S2-c, S2-e (`:119`) ;
  - S2-c → S2-g, S2-h (`:146`, `:150`) ;
  - S2-d → S2-g, S2-f (`:163`, `:170`, `:172`) ;
  - S2-e → S2-g (`:195`, `:197`) ;
  - S2-f → S2-g (`:223`, `:225`).

  À leur création, le numéro de ces issues n'existe pas encore. Les lettres, qui « n'existent que dans ce brouillon » (`:7`), seraient donc publiées telles quelles.
- **Correction attendue** :
  1. créer les huit issues ;
  2. relever leurs numéros ;
  3. dans une seconde passe, réécrire chaque corps avec tous les numéros substitués : `gh issue edit <n> --repo jammindev/jam --body-file <fichier>` ;
  4. corriger la phrase « pour que chaque renvoi pointe vers une issue déjà créée ».

### 2. Une question « renvoyée au plan » que le plan ne peut pas trancher

- **Fichiers** : `docs/plans/cadrage-s2-issues.md:150`, et les clauses « sauf si » de `:143`, `:248` et `:272`.
- **Constat** : la question 2 de S2-c demande si le recetteur peut envoyer une requête du protocole par un script du repo. Elle précise elle-même que le profil du recetteur devrait alors l'autoriser, « ce qui demande un cadrage ». Or le process veut qu'un cadrage qui change un profil soit mergé avant les tâches qui l'appliquent (`docs/process/README.md:81`). Le plan de S2-c ne peut donc pas ouvrir cette voie. Les critères de S2-c, S2-g et S2-h restent pourtant suspendus à « sauf si le plan […] a donné au recetteur un script du protocole ».

  Conséquence : la part principale des trois recettes reste à la check-list du mainteneur, ce que RET-010 cherche à éviter, et rien ne dit qui tranche ni quand.
- **Correction attendue** :
  - retirer la question 2 des « Questions renvoyées au plan » ;
  - l'inscrire dans `OPEN-QUESTIONS.md` (nouvelle Q, Ben, au cadrage qui la traitera), en citant l'autre voie déjà notée au profil du recetteur : le test e2e de l'app (Q-017) ;
  - dans les trois critères de recette, remplacer « sauf si… » par un renvoi à cette question ;
  - autre voie possible : la trancher dans ce cadrage, profil du recetteur compris.

### 3. « Issue » employé pour le résultat d'un tour ou d'une étape

- **Fichier** : `docs/plans/cadrage-s2-issues.md:217` (« coût et issue du tour relevés »), `:239` (« issue de l'étape (réussie, en échec, interrompue) »).
- **Constat** : dans tout le cadrage, et au glossaire (« Tâche : une issue GitHub »), « issue » désigne une issue GitHub. Le même mot, pris au sens de dénouement, dans le corps d'une issue, sur un champ qui voisine avec « numéro et titre de l'issue » (`:245`), prête à confusion pour un mainteneur qui ne code pas, et pour le nommage du champ dans le code.
- **Correction attendue** : employer un autre terme, par exemple « sort du tour », « sort de l'étape », ou « état final de l'étape (réussie, en échec, interrompue) ».

### 4. Q-052 : place dans la table, et un statut que les recettes du S2 contredisent

- **Fichier** : `docs/specs/OPEN-QUESTIONS.md:49-50` ; renvois `docs/plans/cadrage-s2-issues.md:143`, `:248`, `:272`, `:291`.
- **Constat** :
  1. Q-052 est insérée avant Q-051 : la table n'est plus dans l'ordre des numéros.
  2. Le statut dit « au S2 […] aucun worktree n'est supprimé ». Or les recettes de S2-c, S2-g et S2-h se terminent par la suppression, par le mainteneur, du worktree et de la branche créés dans `house`. Deux recettes sur la même issue n recréeraient le même chemin `<n>-<slug>`, et la deuxième hériterait de l'historique de la première, propre à Claude Code. C'est exactement la situation que décrit Q-052 : elle se produit dès le S2. Le cas compte surtout pour S2-h, qui relance un vrai planificateur après l'essai réel de S2-g.
- **Correction attendue** :
  - placer Q-052 après Q-051 ;
  - écrire au statut : « jam ne supprime aucun worktree au S2 ; les recettes de S2-c, S2-g et S2-h en suppriment à la main » ;
  - dans les check-lists de S2-g et S2-h, demander une issue de `house` qui n'a pas servi à une recette précédente, ou noter l'héritage.

### 5. Recette de S2-b : `gh auth status` est interdit au recetteur

- **Fichier** : `docs/plans/cadrage-s2-issues.md:117` ; profil `docs/process/roles/recetteur.md:9` (`--disallowedTools … "Bash(gh *)" "Bash(rtk gh *)"`).
- **Constat** : la check-list « commence par `gh auth status` », et le recetteur la déroule « avec ses commandes et dans son ordre ». Sa première commande sera donc refusée. Le brouillon dit ce qui reste au mainteneur pour Cmd+K, pas pour `gh`.
- **Correction attendue** : ajouter que `gh auth status` n'est pas lancé par l'agent (`gh` est interdit à son profil) et reste à la check-list du mainteneur ; le rapport le note « non reproduit ».

## Suggestions

1. **`--verbose` avec `stream-json`** (`docs/plans/cadrage-s2-issues.md:161`).
   - Selon toute vraisemblance, Claude Code refuse `-p --output-format stream-json` sans `--verbose` ; à vérifier par le plan, R-04.
   - Le critère « contient exactement les options de son profil » (`:167`) risque de figer une liste qui échouerait à l'essai réel de S2-g.
   - Suggestion : écrire « notamment » devant la liste d'options, ou ajouter `--verbose` à vérifier.
2. **`pnpm core:ping` et `JAM_DATA_DIR`** (`docs/process/roles/recetteur.md:16`). Le script lance le cœur avec `--db :memory:` (`packages/core/package.json:13`) : il hérite de la variable, mais n'ouvre aucune base. Suggestion : ne citer que `pnpm dev`, ou dire que `core:ping` ne touche aucune base.
3. **Lettres S2-x dans des docs durables** (`docs/process/roles/recetteur.md:16`, `docs/specs/OPEN-QUESTIONS.md:16`, `:19`, `:31`, `:48`). Ces renvois à « la tâche S2-a / S2-d / S2-h du cadrage `cadrage-s2` » resteront en lettres après la publication, alors que les numéros réels seront connus. Suggestion : prévoir au §6 que le prochain cadrage, ou la tâche concernée, remplace ces lettres par les numéros.
4. **Bloc Orca de S2-e** (`docs/plans/cadrage-s2-issues.md:201`). S2-e lit le corps de l'issue avec `gh` et le valide. L'entrée « `gh` : issues, PR, checks » (`gh-utils.ts`) y servirait autant qu'à S2-b. Suggestion : l'ajouter au bloc.
5. **Slug vide** (`docs/plans/cadrage-s2-issues.md:142`). La carte relève qu'Orca refuse un nom vide. Un titre fait seulement de ponctuation ou d'emoji donne un slug vide, donc un nom `<n>-`. Suggestion : ajouter ce cas aux tests de S2-c.
6. **« En développement »** (`docs/plans/cadrage-s2-issues.md:81` contre `:91`). Le titre limite S2-a au développement, mais le périmètre fait suivre la variable à l'app dans tous les cas. Suggestion : retirer « en développement » du titre, ou le dire dans le périmètre (l'ADR 0010 place la base dans le dossier de données de l'app).
7. **Q-043 au plan de S2-a** (`docs/plans/cadrage-s2-issues.md:286`). Le bloc Orca de S2-a dit qu'aucune entrée de la carte ne la couvre : son planificateur reçoit le clone mais n'a pas de raison d'y lire. L'observation de Q-043 a plus de chances de se faire au plan de S2-b. Suggestion : « au premier plan qui lit le clone ».

RELECTURE : CORRECTIONS (5)
