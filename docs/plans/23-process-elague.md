# Plan — #23 Process élagué (K1-2), niveau *standard*

## À décider au feu vert plan

1. **Seuil « assez bon »** (FR-050). Un constat n'est « à corriger » que s'il écrit un scénario d'échec (entrée → mauvais résultat) ou cite l'exigence, l'ADR ou le critère de fin qu'il viole ; sinon c'est une suggestion (cosmétique). Un tour sans bloquant ni « à corriger » conclut `RELECTURE : OK`. Une suggestion reclassée « à corriger » au tour suivant sans nouveau scénario reste une suggestion. **Reco : oui.**
2. **Temps du mainteneur** (FR-055). Des messages à moins de 10 min l'un de l'autre forment un moment ; un moment vaut (dernier − premier) + 3 min de lecture. Les commandes `!` ne comptent pas. Écart toléré à la recette : même nombre de moments à ±1 près, total à ±15 % ou ±5 min (on prend le plus large des deux). **Reco : oui.**
3. **Plafonds** (FR-051) : 6 agents en cours pour tout le poste, valeur écrite dans le process ; 3 pour jam, dans sa fiche. **Reco : oui** (une tâche *standard* avec deux relecteurs et trois coordinateurs ouverts tient dans 6).
4. **Q-058** : l'orchestrateur de tâche écrit l'analyse d'un retour dans `docs/plans/<tâche>-retours.md`, dans son worktree, et la commite avec la tâche. Cette note de suivi n'est pas un livrable relu. **Reco : oui.**
5. **Feu vert pour une action du coordinateur** (merge, publication) donné dans le worktree : le segment `✓` reste, et le coordinateur fait confirmer le mainteneur dans son propre terminal avant d'agir (FR-053, garde de sortie). **Reco : oui.**
6. **Numéros réservés** : ADR 0018 « Process élagué », qui porte aussi le tableau des origines retirées du process ; RET-017 (veille et relais) ; RET-018 (mesure par script). **Reco : oui.**

## 1. Objectif et critère de fin

L'objectif et le critère de fin sont ceux de l'issue #23 : la méthode passe dans `process/` et `roles/` ; elle devient générique et passe sous 4904 mots (plafond de NFR-015, `docs/process/` comptant 9808 mots sur `main` à a4794df) ; elle porte les règles de RET-014 à RET-016 ; la fiche de jam existe au niveau *léger* ; `watch_cards.py` gagne deux réveils ; un script mesure le temps du mainteneur, et ses tests passent en CI.

## 2. Choix techniques

- **Ordre des passages** : l'implémenteur passe d'abord, puis le rédacteur. Ensuite, deux relecteurs (justesse et conformité) relisent tout ensemble, puis vient la recette. Les déplacements `git mv` doivent précéder la recréation de `docs/process/README.md`. L'implémenteur cite d'avance les numéros réservés au point 6 ; le rédacteur les crée ensuite.
- **Partage** :
  - *implémenteur* : `git mv`, `process/` (README et `fiche-projet.md`), `roles/`, `hooks/`, `scripts/`, les tests et la fiche concept ;
  - *rédacteur* : `docs/process/README.md` réduit à un renvoi, `docs/methode.md`, `AGENTS.md`, `docs/specs/`, l'ADR 0018 et l'index des ADR, RETOURS, ainsi que les liens de `docs/` qui visent l'ancien `docs/process/` (seuls les liens changent dans les ADR).
- **Origines** : chaque « Origine : … » devient un renvoi (ADR 0018, ADR ou RET existants). Les origines sans trace (#7, Q-022, Q-023) vont dans le tableau de l'ADR 0018.
- **Profils lus** (point 4 de l'issue) : le hook de reprise désigne le process et les profils **du plugin qui l'exécute**, trouvés depuis son propre fichier, jamais depuis le worktree. Les copies du worktree d'une tâche de jam restent donc inertes, et il n'y a pas besoin d'interdire `process/` ni `roles/`. Les interdits transposés protègent ce que les rôles suivants lisent dans le worktree : `.claude/`, `AGENTS.md`, `CLAUDE.md`, `docs/methode.md` (commande de test, grille) et `docs/plans/`.
- **Friction 18** (diagnostic d'après la doc des permissions de Claude Code) : une règle `Edit(chemin)` relative se résout depuis le **dossier courant** de la session, qui suit les `cd` du recetteur. Une règle `Edit(/chemin)` se résout depuis le dossier de travail principal, fixe. La forme absolue s'écrit `//` suivi du chemin **sans** son `/` initial : écrire `//<worktree>` avec un chemin qui commence déjà par `/` donne `///…`, qui ne correspond à rien. C'est la cause probable de l'échec de la forme absolue. L'écriture dans le dossier de recette passait, car le profil l'écrit `/<dossier>`, ce qui donne bien `//…`. `--plugin-dir` n'y est pour rien : un refus de hook commencerait par `[jam]`. **Règle** : toute règle `Edit` des profils est ancrée par `/` (`Edit(/docs/plans/<tâche>-recette.md)`). **Repli** : le recetteur écrit son rapport dans le dossier de recette, et un rédacteur le recopie tel quel.
- **Mesure** : `scripts/maintainer_time.py` reprend le tri « message du mainteneur » de la garde de sortie. Une refonte sans changement de comportement en extrait une fonction (`maintainer_words(event)`), prouvée par les tests existants de la garde. On évite ainsi deux définitions qui divergent.
- **Veille** : la veille repose sur des transitions (baseline au lancement, comme aujourd'hui), voir l'annexe B. Pas de fichier d'état.
- **Taille et généricité** : un test CI compte les mots de `process/` et `roles/` (`split()`, comme `wc -w`) contre 4904, et refuse `pnpm` et les chemins de dossier personnel. Les noms d'autres projets se vérifient à la recette, d'après une liste du mainteneur jamais versionnée.
- **Q-027** : le planificateur garde `WebSearch` et `WebFetch` (ils ont servi au diagnostic ci-dessus), gagne `git diff`, et n'écrit plus que son plan.

## 3. Orca

Aucune brique d'Orca n'est reprise : pas de clone de référence (ADR 0014 historique).

## 4. Étapes (implémenteur)

1. `git mv docs/process/roles roles`, puis `git mv docs/process process`. Preuve : `git status` montre des renommages.
2. **Test d'abord** : `hooks/test_plugin.py` vérifie la taille (≤ 4904 mots pour `process/` et `roles/`, `fiche-projet.md` comprise) et l'absence de `pnpm` et de `/Users/` ou `/home/`. Le test est rouge tant que l'élagage n'est pas fait.
3. **Hook de reprise, test d'abord** :
   - avec `docs/methode.md` dans le repo, une ligne « Méthode » donne la fiche ainsi que `<racine du plugin>/process/README.md` et `<racine du plugin>/roles/`, en chemins absolus déduits du fichier du hook ;
   - cas à couvrir : un repo de test qui a son propre `process/` n'est pas désigné, et sans fiche il n'y a pas de ligne ;
   - la ligne « Process du repo » disparaît, et le message de refus de `guard_coordinator.py` renvoie au process du plugin.
4. **Refonte de la garde de sortie** : extraire `maintainer_words(event)` de `last_user_message`. Preuve : `hooks.test_guard_outbound` reste vert, sans test modifié.
5. **Veille, tests d'abord** (faux `orca`, fixture de l'annexe B) : réveil sur un agent `waiting` ; réveil sur une carte `▶` sans agent au travail depuis N minutes, y compris sans aucun agent ; pas de réveil avant N, ni sur une carte `main`, `completed`, `⏸`, `⛔` ou sans segment d'état ; un seul réveil par épisode ; option `--idle-minutes` (10 par défaut).
6. **Mesure, tests d'abord** (transcripts synthétiques, annexe B) : moments et marge ; messages injectés écartés ; rattachement à la tâche ; fenêtre ; dossier des transcripts pris en argument, sinon dans `CLAUDE_CONFIG_DIR`, sinon dans le dossier personnel. La sortie ne contient aucun contenu de message (un test le vérifie avec un mot témoin).
7. **Élaguer `process/README.md` et les sept profils**, puis écrire `process/fiche-projet.md` :
   - retirer ce qui est propre à l'app et les passages « Kit » ;
   - écrire les commandes génériques (annexe A), qui prennent la commande de test et la recette dans la fiche ;
   - écrire les règles de l'issue (point 3) et du plan, et retirer la vérification à la main d'une carte longtemps `in-progress` (NFR-016) ;
   - placer les règles des frictions traitées (annexe C).
   Preuve : le test de l'étape 2 passe au vert.
8. Écrire la fiche concept `docs/concepts/veille-et-mesure.md` et mettre à jour les liens internes de `process/` et `roles/`. Preuve : `python3 -m unittest` tout vert.

Le rédacteur passe ensuite, avec la liste de la section 2. Il trouve les liens visés avec Grep sur `docs/process` dans `docs/`, sauf dans `docs/plans/`, qui est historique.

**Recette** (recetteur, `--plugin-dir <worktree>`) : la check-list de l'issue, dont chaque point est une demande à une session, faisable depuis un téléphone. Pour la veille, l'orchestrateur crée un worktree jetable (`essai-veille`, supprimé ensuite) et y lance un agent bloqué sur une invite, sans toucher à une vraie carte. La mesure se recoupe sur #22 : l'orchestrateur donne dans le brief les chemins et la fenêtre de #22, propres au poste. Le recetteur ne versionne que des comptes et des totaux. **Point 4 de l'issue** : la recette vérifie, avec un repo de test qui a son propre `process/`, que le chemin affiché est celui du plugin. La vérification en vraie grandeur, une session dans un worktree de tâche sans `--plugin-dir` qui désigne le clone installé, se fait après l'installation par le mainteneur ; elle est notée dans le rapport de #24.

## 5. Fichiers créés ou modifiés

- **Créés** : `process/` (README et `fiche-projet.md`), `roles/` (renommés), `scripts/maintainer_time.py`, `scripts/test_maintainer_time.py`, `docs/concepts/veille-et-mesure.md`, `docs/process/README.md` (renvoi), `docs/methode.md`, `docs/decisions/0018-process-elague.md`.
- **Modifiés** :
  - hooks : `hooks/session_start_recap.py`, `hooks/guard_coordinator.py`, `hooks/guard_outbound.py` (refonte) et leurs tests, `hooks/test_plugin.py` ;
  - scripts : `scripts/watch_cards.py`, `scripts/test_watch_cards.py`, `scripts/fixtures/orca/worktree-ps.json`, `scripts/test_launch_task.py` (chemin du profil dans le brief de test) ;
  - docs : `AGENTS.md` (règles 6 et 10, environnement), `docs/specs/01-REQUIREMENTS.md` (FR-046, FR-055, FR-056), `OPEN-QUESTIONS.md` (Q-027 et Q-058 tranchées, Q-060 complétée), `RETOURS.md` (RET-017, RET-018), `GLOSSARY.md` (« Agent en cours », « Épisode »), `02-ARCHITECTURE.md` (scripts), `docs/decisions/README.md`, liens de `docs/`.

## 6. Hors périmètre

Contenu du niveau *renforcé* (Q-061) ; skills et modèles (Q-062) ; adoption par d'autres projets ; installation du plugin (mainteneur, après le merge) ; tout changement de comportement des gardes ; fenêtre d'autorisation du système invisible pour la veille, car l'agent reste `working` (Q-059 ouverte) ; lancement des rôles en sous-agents (Q-054) ; nombre maximal de tours de relecture.

## 7. Questions au mainteneur

Elles sont en tête du plan, points 1 à 6.

## 8. Concepts

Une fiche, `docs/concepts/veille-et-mesure.md` : le réveil sur transition, une fois par épisode, et l'estimation du temps à partir des transcripts, avec ses limites.

---

## Annexe A — Commandes pour #23, et forme générique

Chaque `Bash(x)` figure aussi en `Bash(rtk x)`. Toute règle `Edit` est ancrée par `/`. Les refus `git commit`, `git push`, `git -C` et `gh` restent ceux d'aujourd'hui.

- **Implémenteur** :
  - autorisés : `Read`, `Grep`, `Glob`, `Edit(/**)`, `Bash(python3 -m unittest)`, `Bash(python3 -m unittest *)`, `Bash(git status)`, `Bash(git diff:*)`, `Bash(git mv docs/process/roles roles)`, `Bash(git mv docs/process process)` ;
  - interdits : `Edit(/.claude/**)`, `Edit(/AGENTS.md)`, `Edit(/CLAUDE.md)`, `Edit(/docs/methode.md)`, `Edit(/docs/plans/**)`, `Edit(/docs/process/**)`, `Edit(/docs/specs/**)`, `Edit(/docs/decisions/**)`.
  - Forme générique : sans les `git mv` ; la commande de test vient de la fiche.
- **Rédacteur** : celle d'aujourd'hui, avec ses règles ancrées par `/`.
- **Relecteurs** : `Edit(/docs/plans/23-process-elague-relecture-*.md)`, `git diff`, `git log`, `git status` et `python3 -m unittest` (avec `*`). Forme générique : la commande de test de la fiche.
- **Recetteur** :
  - session lancée avec `--plugin-dir <worktree>` et `--add-dir <dossier de recette>` ;
  - autorisés : `Edit(/docs/plans/23-process-elague-recette.md)`, `Edit(//<dossier de recette sans / initial>/**)`, `python3 -m unittest`, `python3 scripts/watch_cards.py *`, `python3 scripts/maintainer_time.py *`, `wc -w process/README.md process/fiche-projet.md roles/*.md`, `git status`, `ls` ;
  - plus de `JAM_DATA_DIR` ni de commandes de l'app.
  - Forme générique : la recette de la fiche.
- **Planificateur** :
  - autorisés : `Read`, `Grep`, `Glob`, `WebSearch`, `WebFetch`, `Edit(/docs/plans/<tâche>.md)`, `git log`, `git diff`, `git status`, `ls` ;
  - plus de liste d'interdits : une seule règle `Edit`.
- **Coordinateur et orchestrateur** : `JAM_ROLE=<rôle> claude`, inchangé. Les rôles se lancent par `launch_task.py --cap 6 --project-cap <fiche>`.

## Annexe B — Veille et mesure : mécanismes et fixtures

**États**. Un agent est *bloqué* si `state` ou `mainAgent.state` vaut `waiting`, l'état que prend un agent sur une invite d'autorisation. Il est *au travail* si l'un des deux vaut `working`, ou si `workingMode` vaut `monitoring` (attente en tâche de fond). `done` n'est ni l'un ni l'autre. Seules les cartes dont le premier segment commence par `▶`, hors `main` et `completed`, sont visées par ces deux réveils.

**Une fois par épisode**, sans fichier d'état :
- *bloqué* : on réveille quand un `paneKey` entre dans l'ensemble des agents bloqués de la carte. L'ensemble relevé au lancement compte comme déjà vu : après une relance de la veille, un agent toujours bloqué ne réveille plus ;
- *inactif* : l'âge de la carte vaut maintenant − le plus récent `stateStartedAt` de ses agents. Sans aucun agent, c'est l'horloge du script depuis la première lecture. On réveille quand l'âge franchit N entre deux lectures. Une carte déjà au-delà de N au lancement ne réveille pas. Une carte sans agent peut réveiller de nouveau N minutes après une relance : le coordinateur relance alors l'orchestrateur ou passe la carte en `⛔`, ce qui clôt l'épisode (règle du process).

**Fixture** (`worktree-ps.json`, valeurs inventées) :
- chaque carte gagne `status` et `agents` ;
- un agent a les champs `agentType` `"claude"`, `displayName` `"orchestrateur"`, `interrupted` `false`, `lastAssistantMessage` `"…"`, `mainAgent` `{state, stateStartedAt}`, `paneKey` `"pane-1"`, `parentPaneKey` `null`, `prompt` `"brief"`, `state`, `stateStartedAt`, `taskTitle` `"tâche"`, `toolInput` `{}`, `toolName` `"Bash"`, `updatedAt`, et `workingMode` facultatif ;
- la carte de tâche a un agent `working`, la carte `main` un agent `done`, l'autre projet un agent `working` ;
- l'orchestrateur relève dans le relevé réel le **type** de `stateStartedAt` (nombre ou chaîne ISO) et le donne dans le brief. Le script n'accepte que ce type ; une valeur illisible retombe sur l'horloge du script.

**Mesure**. Les sessions retenues sont celles dont le `cwd` est le worktree principal (coordinateur) ou le worktree de la tâche. On écarte :
1. ce qu'écarte `maintainer_words` (isMeta, résumé de compaction, résultats d'outil, notifications, sorties `!` et `/`) ;
2. les évènements `isSidechain` ;
3. le premier message de chaque session du worktree de la tâche : c'est un brief, puisque toutes ces sessions sont lancées par un agent ;
4. tout message identique au `--text` d'un `orca terminal send` lu dans les appels Bash des transcripts retenus : c'est un relais.

Un message de la session du coordinateur est rattaché à la tâche s'il nomme `#<n>` ou le nom du worktree, ou si la dernière réponse du coordinateur avant lui les nomme. Les messages entre agents ne sont pas prévus par la méthode (rôles en terminaux Orca). Limites écrites dans la PR : un « ok » qui suit un résumé de plusieurs tâches compte pour chacune ; un message non rattaché est perdu ; une session libre ouverte par le mainteneur dans le worktree perd son premier message.

**Transcripts synthétiques** : du JSONL avec `type`, `timestamp` (ISO), `cwd`, `sessionId`, `isSidechain` et `message.content` (blocs `text`, `tool_use` Bash, `tool_result`). Le recoupement sur #22 valide ce format sur de vrais transcripts.

## Annexe C — Les 24 frictions de #22

| # | Sort | Où, ou pourquoi |
|---|---|---|
| 1 | Traitée | process, lancement : brief par le terminal, ou fichier temporaire lu par `launch_task.py` |
| 2 | Laissée | sans objet : hooks dans le plugin |
| 3 | Traitée | profil du planificateur : au-delà de deux pages, plan refait |
| 4 | Laissée | relevé fourni au brief pour #23 ; cas rare (gel) |
| 5 | — | constat positif |
| 6 | Traitée | recette prise dans la fiche, lancée par le recetteur |
| 7 | Laissée | Q-060 (plan modifié après le feu vert) |
| 8 | Laissée | « Read » sans chemin, sandbox (R-03) |
| 9 | Laissée | Q-060 |
| 10 | Traitée | process, règle commune : rien lire hors du worktree et du brief, transcripts compris |
| 11 | — | règle existante |
| 12, 13 | Traitées | seuil « assez bon » (point 1) |
| 14 | Traitée | profil générique du recetteur |
| 15 | Traitée pour #23 | worktree jetable à la recette ; pas de règle |
| 16 | — | déjà géré par `orca_cli.py` |
| 17 | Laissée | ajoutée à Q-060 par le rédacteur |
| 18 | Traitée | règles `Edit` ancrées par `/`, repli (§2) |
| 19, 20, 22 | Traitées | profil du recetteur : check-list faite de demandes à une session, phrases testées contre le vocabulaire de la garde |
| 21 | Traitée | process : terminal d'un rôle fermé dès sa ligne de fin (il compte dans les agents en cours) |
| 23 | Traitée | process : un brief ne contredit pas un profil, le profil prime |
| 24 | Traitée | process et profil du coordinateur : relais court, sans négation ; « ok » pour le plan et la recette ; 30 s après, `orca terminal read` |

PLAN PRÊT : docs/plans/23-process-elague.md
