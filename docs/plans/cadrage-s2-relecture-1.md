# Relecture — cadrage `cadrage-s2`, tour 1

> Relecteur seul (les deux axes), contexte neuf. Objet : `git diff` (quatre fichiers modifiés) et le nouveau `docs/plans/cadrage-s2-issues.md`.

## Ce qui a été vérifié et tient

- **Carte d'Orca** (`docs/references/orca.md`, lignes 50 à 53) : les huit fichiers ajoutés existent au tag `v1.4.218`, et chaque parenthèse dit vrai.
  - `issues.ts` : `listIssues` filtre `pull_request` et renvoie `{ items: [], error }` sur un échec. `classifyListIssuesError` est dans `gh-error-classification.ts`, et `auth-diagnose.ts` détecte `gh` absent (`ENOENT`) ou non authentifié.
  - `workspace-name.ts` : `slugifyForWorkspaceName` ne décompose pas les accents (`[^a-z0-9._-]` devient `-`). À l'inverse, `sanitizeWorktreeName` (`worktree-logic.ts`) garde `\p{L}\p{N}` et lève une erreur pour un nom vide, `.` ou `..`.
  - `commit-message-agent-specs-primary.ts` : `-p --output-format text --permission-mode plan`, avec le prompt sur l'entrée standard (`promptDelivery: 'stdin'`).
  - `source-control-local-process.ts` : un délai maximal (`SOURCE_CONTROL_GENERATION_TIMEOUT_MS`) et `kill('SIGKILL')`.
  - `claude-result-outcome.ts` : c'est `is_error` qui décide, pas le sous-type. Le fichier dépend des types du journal de session de l'Agent SDK.
  - Les fichiers cités par les blocs « Orca » des issues et déjà présents dans la carte existent aussi au tag.
- **Chemin du clone** : il n'apparaît nulle part dans `docs/`. Le diff n'ajoute aucun autre chemin propre au poste, aucune donnée personnelle et aucune mention d'assistant.
- **État GitHub** (`gh api 'repos/jammindev/jam/milestones?state=all'`, `gh issue list`, `gh issue view 2`) : le milestone #1 est fermé ; #2 à #4 sont ouverts, avec les anciennes descriptions courtes ; le titre du #4 est encore `E0-S4 Merge et parallélisme` ; les issues #2, #3 et #4 sont ouvertes. Le label `enhancement` existe. Le §1 et le §2 du brouillon décrivent cet état sans erreur.
- **Numérotation** : Q-052 est le numéro libre suivant. Le cadrage n'ajoute ni RET ni ADR.
- **Faits sur le code de jam** :
  - l'app passe `--db <userData>/jam.db` au cœur (`apps/desktop/src/main/index.ts:43`, `core-process.ts:25`), et seul le cœur en CLI suit `JAM_DATA_DIR` (`packages/core/src/paths.ts`) ;
  - le cœur crée le dossier de la base (`mkdirSync` dans `database.ts`) : `<dossier de recette>/data` n'a pas à exister d'avance ;
  - « Lister les repos » est bien le titre de la commande.
- **Cohérence d'ensemble** :
  - le milestone S2 reprend la roadmap ;
  - les fiches concept sont réparties sur S2-c et S2-f ;
  - chaque issue a son bloc RET-010 et son bloc « Orca », liste noire comprise ;
  - les dépendances et les migrations (S2-c, puis S2-g) se tiennent ;
  - S2-a passe avant la première migration (Q-050), et la raison donnée est juste.

## Constats

### Bloquant

Aucun.

### À corriger

**1. Les commandes du §6 échouent telles qu'écrites.** `docs/plans/cadrage-s2-issues.md`, lignes 293 à 298.
- Ligne 293 : `gh api repos/jammindev/jam/milestones?state=all` n'a pas de guillemets. Sous zsh, le `?` est un joker : la commande s'arrête sur « no matches found ». Le profil du relecteur écrit d'ailleurs la forme entre guillemets.
- Lignes 294 à 298 : les textes sont passés entre apostrophes simples (`-f description='…'`, `--title '…'`, `--comment '…'`). Or ils contiennent des apostrophes : « l'issue », « d'E0 », « jusqu'à la PR », « d'un rôle », « l'app suit ». Le shell coupe la chaîne à la première.
- **Correction attendue** :
  - écrire `gh api 'repos/jammindev/jam/milestones?state=all'` ;
  - passer les descriptions par fichier (`-F description=@<fichier>`), comme les corps (`--body-file`) ;
  - pour `--title` et `--comment`, prendre des guillemets doubles, ou un fichier pour le commentaire (`gh issue close` n'en accepte pas : le poster d'abord avec `gh issue comment --body-file`).

**2. Le choix « plan écrit dans un fichier » contredirait l'ADR 0009.** `docs/plans/cadrage-s2-issues.md`, ligne 172 (S2-d, « Questions renvoyées au plan »).
- La question laisse au plan le choix entre deux options :
  - un fichier écrit par le planificateur dans le worktree ;
  - le texte final de l'étape.
- Or l'ADR 0009, acceptée, donne au planificateur « Lecture seule ». La première option demanderait donc une nouvelle ADR (AGENTS.md : « une décision actée ne se contourne pas »). La question ne le dit pas : un plan pourrait la trancher seul, en élargissant le profil.
- **Correction attendue** : trancher au cadrage pour le texte final, qui est conforme à l'ADR 0009 et que S2-g enregistre déjà (ligne 236). À défaut, ajouter que l'option « fichier » demande une ADR qui précise l'ADR 0009, et ne peut donc pas être retenue par le seul plan.

**3. FR-011 n'est porté par aucune issue.** `docs/plans/cadrage-s2-issues.md`, ligne 205 (S2-f, « Exigences »), et ligne 209.
- FR-011, de priorité M en E0, demande que Claude Code et le harness passent par une même interface « backend d'agent ».
- L'ADR 0004 dit que c'est le format d'événements normalisé qui « donne corps » à cette interface.
- S2-f construit justement ces événements normalisés (« le backend Claude Code »), sans citer FR-011. Aucun autre jalon d'E0 ne construit le backend.
- **Correction attendue** : ajouter FR-011 aux exigences de S2-f, avec une ligne de périmètre : « les événements normalisés ne dépendent pas de Claude Code : ce sont ceux que tout backend d'agent émettra (FR-011) ». Ou bien, si le mainteneur le préfère, inscrire FR-011 en « hors périmètre » de S2-f, avec son renvoi (E2).

**4. S2-g promet « aucun agent orphelin » sans dire quel arrêt du cœur est couvert.** `docs/plans/cadrage-s2-issues.md`, lignes 238 et 243.
- L'app arrête le cœur en fermant son entrée standard, puis par `SIGKILL` au bout de 2 s (`apps/desktop/src/main/core-process.ts`, `STOP_TIMEOUT_MS`).
- Un cœur tué par `SIGKILL`, ou qui plante, ne peut pas arrêter son enfant : Claude Code continue alors et consomme le quota (R-02). Le test de la ligne 243 ne peut prouver qu'un arrêt propre.
- **Correction attendue** : écrire « si le cœur s'arrête normalement (fermeture de son entrée standard, signal d'arrêt) » à la ligne 238, et le même cas à la ligne 243. Le cas d'un cœur tué ou planté va dans « Hors périmètre » ou dans une question ouverte : l'étape y est seulement marquée interrompue au démarrage suivant, et l'agent orphelin reste possible. Le plan peut aussi lancer Claude Code dans son propre groupe de processus, mais ce n'est pas exigé.

**5. Pour S2-a, S2-c, S2-g et S2-h, la recette ne dit pas ce que l'agent ne peut pas reproduire.** `docs/plans/cadrage-s2-issues.md` :
- S2-a, lignes 95 à 97 ;
- S2-c, ligne 143 ;
- S2-g, lignes 241 et 244 ;
- S2-h, lignes 264 et 268.

Le recetteur ne simule pas le clavier (profil du recetteur, « Clavier »), et sa seule commande vers le cœur est `pnpm core:ping`. Il ne peut donc ni choisir une issue, ni lancer « Lancer le planificateur », ni lister les repos par la palette. Pour S2-a, il hérite en plus de `JAM_DATA_DIR` pour toutes ses commandes : il ne peut pas lancer l'instance « sans la variable » du critère. S2-b le dit (ligne 117 : « Cmd+K n'est pas reproduit par l'agent : il reste à la check-list »), les autres non. Le critère principal de S2-c, S2-g et S2-h (l'essai réel sur `house`) reposerait alors sur la seule check-list, sans que le brouillon le dise. Cela affaiblit RET-010.

**Correction attendue** : dans chacune de ces quatre issues, une phrase comme celle de S2-b, qui dit ce qui reste à la check-list du mainteneur. Autre option : renvoyer au plan de S2-c (ou de S2-g) une question : le recetteur peut-il envoyer une requête du protocole au cœur en CLI (un script du repo sur le modèle de `core:ping`), pour reproduire l'essai sans clavier ?

**6. La phrase ajoutée au profil du recetteur désigne mal la tâche, et elle est fausse dans le worktree de S2-a.** `docs/process/roles/recetteur.md`, ligne 16.
- « la tâche qui le permet (cadrage `cadrage-s2`) » renvoie au cadrage, pas à la tâche. Le lecteur ne sait pas quelle issue attendre.
- « L'app ne suit la variable qu'une fois mergée la tâche » : dans le worktree de S2-a, l'app la suit déjà, avant le merge. Et la recette de S2-a s'y lance avec la variable (ligne 95 du brouillon).
- **Correction attendue** : nommer la tâche comme le fait Q-012, par exemple « la tâche S2-a du cadrage `cadrage-s2` (« Une base par instance en développement ») ». Puis écrire : « L'app suit la variable dans le worktree de cette tâche, puis partout une fois qu'elle est mergée ; d'ici là… ».

### Suggestions

- **`--verbose` avec `stream-json`** (`cadrage-s2-issues.md`, ligne 159, S2-d) : avec `-p`, Claude Code refuse `--output-format stream-json` sans `--verbose`. C'est à vérifier sur la version testée (R-04). Le citer dans la ligne de commande attendue éviterait un test de S2-d qui passe sur une commande que Claude Code refusera à l'essai réel de S2-g.
- **« issue » pour l'issue d'une étape** (`cadrage-s2-issues.md`, lignes 214 et 236) : « issue du tour » et « issue de l'étape (réussie, en échec, interrompue) » emploient « issue » au sens de dénouement. Le même texte parle d'issues GitHub, et le glossaire définit la tâche par l'issue. Un nom de colonne `issue` dans la table des étapes serait ambigu. Proposer « statut final » ou « résultat ».
- **Taille de S2-g et de S2-h** (ADR 0011).
  - S2-g est le plus gros lot : lancement, migration, une dizaine de champs, commande de palette, arrêt de l'enfant, étape marquée interrompue au démarrage, faux Claude Code, essai réel. On pourrait sortir en une issue l'arrêt de l'enfant et le marquage des étapes interrompues.
  - Pour S2-h, la piste de l'interrogation régulière du cœur, notée dans le plan, éviterait que les notifications (Q-015, Q-017) grossissent le lot.
- **S2-d et S2-f en parallèle** (`cadrage-s2-issues.md`, ligne 56) : les deux créent « le backend Claude Code ». Lancées en même temps, elles risquent de créer le même module chacune de son côté, d'où des conflits au merge. À signaler au coordinateur s'il les parallélise.
- **« même issue »** (`cadrage-s2-issues.md`, ligne 136, S2-c) : préciser « la même issue du même repo ». Avec plusieurs repos (FR-030), deux issues de même numéro sont distinctes.
- **Check-list de 5 étapes au plus** (profil du recetteur, « Sortie ») : la recette de S2-c compte déjà 6 étapes environ :
  1. lancement avec `JAM_DATA_DIR` ;
  2. ajout de `house` ;
  3. choix de l'issue ;
  4. vérification du worktree ;
  5. redémarrage ;
  6. suppression du worktree et de la branche.

  Celles de S2-g et S2-h aussi. Dire si la suppression compte, ou regrouper des étapes.
- **Q-040** (`OPEN-QUESTIONS.md`, ligne 44) : la question dit « À traiter avec Q-012 ». Or Q-012 part au plan de S2-d, et le brouillon décide de les découpler (ligne 281). Reporter ce découplage dans le statut de Q-040, pour que le plan de S2-d ne croie pas devoir la trancher.
- **Ordre du tableau** (`OPEN-QUESTIONS.md`, lignes 49 et 50) : Q-052 est placée avant Q-051. La mettre après.
- **« Les quatre dernières lignes »** (`docs/references/orca.md`, ligne 38) : la mention vieillira dès que le cadrage du S3 ajoutera des lignes. Marquer plutôt ces lignes (par exemple « (S2) » dans la colonne Section), ou citer leurs briques par leur nom.

RELECTURE : CORRECTIONS (6)
