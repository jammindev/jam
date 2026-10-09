# Développer jam avec Orca, en appliquant notre propre pipeline

> En attendant que jam sache dérouler son pipeline ([ADR 0008](../decisions/0008-boucle-exterieure-pipeline.md)), on le **déroule à la main dans Orca**. Deux bénéfices : jam est construit selon sa propre méthode, et on éprouve le pipeline sur papier avant de le coder. Chaque friction rencontrée est notée dans `OPEN-QUESTIONS.md` et alimente E0. Chaque remarque du mainteneur est consignée dans [`RETOURS.md`](../specs/RETOURS.md).

## Acteurs

- **Mainteneur** : donne les feux verts et fait la recette.
- **Coordinateur** : une session d'agent conversationnelle sur le worktree principal (`main`), dans laquelle le mainteneur parle (RET-008). Elle tourne dans le terminal flottant d'Orca, joignable depuis tous les worktrees (RET-012). Il crée les worktrees, lance un orchestrateur de tâche par tâche, suit les cartes Orca, tient le mainteneur informé, merge et publie **après** les feux verts. C'est l'interlocuteur unique du mainteneur s'il le souhaite. **Il orchestre et ne produit aucun livrable** (RET-001) : ni code, ni spec, ni ADR, ni issue, ni doc. C'est un rôle lui aussi, protégé par une garde quand il est lancé avec `JAM_ROLE=coordinateur` ([profil](roles/coordinateur.md), [ADR 0012](../decisions/0012-coordinateur-role-garde-fous-hook.md)).
- **Orchestrateur de tâche** : une session d'agent conversationnelle dans le worktree d'une tâche, lancée par le coordinateur (RET-009). Il lance les rôles de sa tâche, tient ses boucles et ses garde-fous, committe, pousse et ouvre la PR **après** les feux verts, et tient sa carte Orca, que suit le coordinateur. Le mainteneur peut lui parler pour discuter de la tâche en détail. Il ne produit aucun livrable non plus ([profil](roles/orchestrateur-tache.md), [ADR 0013](../decisions/0013-orchestration-deux-niveaux.md)).
- **Rôles du pipeline et du cadrage** : rédacteur, planificateur, implémenteur, relecteur, recetteur. Chacun est une session d'agent **neuve**, lancée dans le worktree avec son profil ([`roles/`](roles/)) et ses permissions ([ADR 0009](../decisions/0009-permissions-par-role.md), [ADR 0012](../decisions/0012-coordinateur-role-garde-fous-hook.md) pour le rédacteur).

Tout livrable, code ou non, suit le même chemin : **production par un rôle → relecture indépendante → feu vert**.

L'orchestration à deux niveaux est décrite par l'[ADR 0013](../decisions/0013-orchestration-deux-niveaux.md) (RET-008, RET-009), précisée par l'[ADR 0015](../decisions/0015-remontee-carte-seule-coordinateur-flottant.md) (RET-012, RET-013).

## Tâches, issues et milestones

- **Une tâche = une issue GitHub** sur [`jammindev/jam`](https://github.com/jammindev/jam).
- **Les milestones GitHub sont les jalons** de `04-ROADMAP.md` (S1, S2…).
- Le worktree d'une tâche porte le numéro de son issue : `<numéro>-<slug>`, par exemple `12-file-a-toi`.
- Un cadrage n'a pas d'issue : son worktree s'appelle `cadrage-<slug>`, par exemple `cadrage-s3`. C'est aussi le `<tâche>` de ses fichiers dans `docs/plans/`.
- Un jalon est découpé en petites issues au début du jalon, par un cadrage ([ADR 0011](../decisions/0011-pratiques-et-metriques-dora.md), petits lots).

## Cadrage et retours du mainteneur

Un cadrage a son worktree `cadrage-<slug>` et son orchestrateur de tâche, comme une tâche. Avant qu'une tâche entre dans le pipeline, le cadrage produit les specs, les ADR et les issues :

1. **Retour** : le coordinateur reformule la remarque du mainteneur, l'analyse, et la transmet dans le brief de l'orchestrateur de tâche du cadrage, qui la reprend dans le brief du rédacteur. Le rédacteur l'inscrit dans `RETOURS.md` (RET-NNN). Un retour donné directement à un orchestrateur de tâche suit le même chemin : il le reformule et l'analyse dans un fichier d'un dossier temporaire de sa session (le seul endroit où il peut écrire), le signale au coordinateur par un segment `💬` du commentaire de sa carte, qui désigne ce fichier (table « Signalement d'attente »), et le transmet au rédacteur si sa tâche est un cadrage. Sinon, le coordinateur le confie à un cadrage.
2. **Rédaction** : le [rédacteur](roles/redacteur.md) modifie les docs et écrit les brouillons d'issues (`docs/plans/<tâche>-issues.md`).
3. **Relecture** : un [relecteur](roles/relecteur.md) neuf relit la rédaction. Les tours s'enchaînent jusqu'à `RELECTURE : OK` (voir « Relecture » ci-dessous).
4. **Feu vert cadrage** : le mainteneur valide. Le rédacteur passe alors les ADR concernées de « proposée » à « acceptée », reporte les mentions qu'elles prévoient dans le statut des ADR qu'elles complètent ou précisent, et passe les retours concernés à « appliqué ». L'orchestrateur de tâche committe, pousse et ouvre la PR.
5. **Feu vert merge** : la PR d'un cadrage passe, comme toute PR, par un feu vert merge (décision du mainteneur, RET-009). Le coordinateur merge, puis publie les issues et les milestones avec `gh` : leurs liens vers les docs du cadrage fonctionnent alors sur `main`.

## Correspondance entre le pipeline cible et Orca

| Étape | Cible (jam E0) | Aujourd'hui, dans Orca |
|---|---|---|
| Interlocuteur, niveau projet | Le cockpit (tableau des tâches, file « À toi ») et la session conversationnelle de `main`, le coordinateur (FR-040, après E0 selon l'ADR 0008, Q-039) | Le coordinateur, sur `main`, dans le terminal flottant |
| Interlocuteur, niveau tâche | Le lead du worktree (FR-034) | L'orchestrateur de tâche |
| Tâche | Issue GitHub | Issue GitHub, rattachée au milestone de son jalon |
| Worktree | Créé par le cœur | Le coordinateur : `orca worktree create --name <numéro>-<slug> --no-parent` |
| Orchestration d'une tâche | Le cœur, en code ([ADR 0008](../decisions/0008-boucle-exterieure-pipeline.md)) : il enchaîne les étapes et tient l'état | L'orchestrateur de tâche, un agent dans le worktree, lancé par le coordinateur, qui tient ce rôle à la main faute de cœur |
| Plan | Rôle planificateur | Terminal dans le worktree, agent en `dontAsk` + lecture seule, écrit uniquement `docs/plans/<tâche>.md` |
| **Feu vert 1** | File « À toi » | Statut du worktree `in-review`, commentaire « ⏸ feu vert plan ». Le mainteneur répond au coordinateur ou à l'orchestrateur de tâche |
| Implémentation TDD | Rôle implémenteur, boucle jusqu'au vert | Nouveau terminal, agent en `dontAsk` + écriture dans le worktree + liste blanche shell. Ni commit ni push |
| Relecture | Rôle relecteur, contexte neuf, un par axe | Un terminal neuf par relecteur et par tour, lecture seule, un fichier de relecture chacun. Les corrections repartent vers l'implémenteur, jusqu'à OK de tous |
| Recette | Rôle recetteur, puis mainteneur | Contrôles de l'agent depuis une installation neuve, check-list du mainteneur en premier, puis test manuel du mainteneur (voir « Recette ») |
| **Feu vert 2** | File « À toi » | Statut `in-review`, commentaire « ⏸ feu vert recette ». L'orchestrateur de tâche committe une fois le feu vert donné |
| PR + CI | Le cœur via `gh` | L'orchestrateur de tâche : push, `gh pr create` (milestone désigné par son titre exact) + CI |
| **Feu vert 3** | File « À toi » | Commentaire « ⏸ feu vert merge » |
| Merge | `gh pr merge` | Le coordinateur, seul à merger : `gh pr merge`, puis `git pull` sur `main` |
| Nettoyage | Le cœur | Le coordinateur : fermeture des terminaux du worktree, `orca worktree rm` + suppression de la branche |
| État d'une tâche et remontée | Persisté par le cœur (FR-027). Remontée structurelle : les deux niveaux lisent le même état | Carte Orca seule, tenue par l'orchestrateur de tâche et surveillée par le coordinateur |
| Feu vert relayé | Sans objet : le feu vert est une action du cockpit, enregistrée par le cœur | Commentaire de carte vers le coordinateur, message dans le terminal de l'orchestrateur de tâche dans l'autre sens. Il cite les mots exacts du mainteneur, l'heure et la session (voir « Remontée vers le coordinateur ») |

## Lancement du coordinateur

Dans le **terminal flottant** d'Orca, que le mainteneur ouvre depuis n'importe quel worktree : il parle au coordinateur de partout, pendant une recette par exemple (RET-012). La session est lancée depuis le worktree principal, sur `main` (RET-008). Or le terminal flottant s'ouvre dans le dossier personnel : on se place d'abord dans le worktree principal.
```sh
cd <chemin du worktree principal>
JAM_ROLE=coordinateur claude              # ajouter --continue pour reprendre la session précédente
```
Sans le `cd`, la session ne lit ni `AGENTS.md` ni ce process : le hook de démarrage, qui affiche le worktree de la session, permet de le voir. La CLI `orca` voit ce terminal (`worktreeId` vaut `global-floating-terminal`, sans chemin de worktree). Les orchestrateurs de tâche n'ont pas besoin de le joindre : ils ne lui écrivent pas (voir « Remontée vers le coordinateur »).

Après chaque merge, le coordinateur fait `git pull` : il lit toujours la référence, `AGENTS.md` et ce process compris.

## Lancement d'un orchestrateur de tâche (coordinateur)

```sh
# 1. Worktree de la tâche
orca worktree create --repo id:<repoId> --name <tâche> --no-parent --json
# 2. Terminal de l'orchestrateur de tâche (profil dans roles/orchestrateur-tache.md)
orca terminal create --worktree id:<repoId>::<chemin> --title orchestrateur --command 'JAM_ROLE=orchestrateur-tache claude' --json
# 3. Attendre que l'agent soit prêt, puis envoyer le brief
orca terminal wait --terminal <handle> --for tui-idle --timeout-ms 60000 --json
orca terminal send --terminal <handle> --text "<brief>" --enter --json
```

Le brief d'un orchestrateur de tâche contient : le chemin de son profil, la tâche, le nombre d'agents qu'il peut lancer à la fois, le critère de fin et, pour un cadrage, les retours du mainteneur avec leur analyse.

Le worktree part de `main` : la tâche suit le process et les profils **mergés**, que ses rôles lisent dans le worktree. Un cadrage qui change le process ou un profil est donc mergé avant de lancer les tâches qui doivent l'appliquer. Origine : au premier essai (#7), le profil de l'orchestrateur de tâche et les règles de recette n'existaient que sur la branche d'un cadrage non mergé, et le recetteur a dû les lire dans un autre worktree.

## Lancement d'un rôle (orchestrateur de tâche)

```sh
# 1. Terminal du rôle, dans le worktree de la tâche (profil de permissions dans roles/<rôle>.md)
orca terminal create --worktree id:<repoId>::<chemin> --title <rôle> --command '<commande du rôle>' --json
# 2. Attendre que l'agent soit prêt, puis envoyer le brief
orca terminal wait --terminal <handle> --for tui-idle --timeout-ms 60000 --json
orca terminal send --terminal <handle> --text "<brief>" --enter --json
# 3. Suivre
orca terminal wait --terminal <handle> --for tui-idle --timeout-ms 1800000 --json
orca terminal read --terminal <handle> --json
```

Le brief d'un rôle contient toujours : le chemin du profil de rôle à lire, la tâche (numéro d'issue, ou `cadrage-<slug>`), les livrables attendus et le critère de fin.

`orca terminal read --json` ne rend que l'écran affiché (champ `result.terminal.tail`), pas l'historique. Il sert à lire la ligne de fin d'un rôle (`PLAN PRÊT`, `RELECTURE : OK`…) ou une invite bloquée. Le contenu se lit dans le fichier que le rôle a écrit (Q-023).

### Hook de démarrage du poste du mainteneur

Un hook personnel du poste, installé hors du repo, donne à chaque session d'agent son contexte dès le démarrage (RET-004) :
- le worktree, la branche et les autres worktrees actifs ;
- quand la session tourne dans Orca : la carte du worktree (statut, commentaire, issue et PR liées), le rôle de la session (`JAM_ROLE`, ou « session libre »), un avertissement par autre agent actif dans le même worktree, la CLI Orca et le chemin du process du repo.

L'orchestrateur de tâche vit dans le worktree : chaque rôle lancé reçoit donc un avertissement à son sujet. Cet avertissement est attendu et ne signifie pas qu'un autre agent écrit en même temps. Le hook pourrait le taire en reconnaissant `JAM_ROLE=orchestrateur-tache` (Q-036).

C'est la préfiguration de FR-038 : dans jam, c'est le cœur qui injectera ce contexte.

### Hook RTK du poste du mainteneur

> Origine : friction constatée par le coordinateur en déroulant le pipeline (refus de permissions dus à la réécriture RTK, Q-022). Ce n'est pas un retour du mainteneur.

RTK est un outil installé sur le poste du mainteneur : il compacte la sortie des commandes shell pour économiser le contexte des agents. Un hook de Claude Code réécrit chaque commande que RTK sait traiter : `git status` devient `rtk git status`, `cat <fichier>` devient `rtk read <fichier>`.

Le hook ne fait que réécrire la commande : il ne décide rien. **La permission est contrôlée ensuite, sur la forme réécrite.** Deux conséquences :
- une règle sur la forme simple ne couvre pas la commande réécrite. Les listes blanches et les listes d'interdits doivent donc **couvrir les deux formes**, par exemple `"Bash(git status)" "Bash(rtk git status)"` ;
- une règle large sur une forme `rtk` autorise plus qu'il n'y paraît : `Bash(rtk read *)` autorise tout `cat`, `Bash(rtk ls *)` tout `ls`, `Bash(rtk gh *)` tout `gh`, écritures comprises. Une règle `rtk …` s'écrit donc aussi étroitement que la règle simple qu'elle double.

Une commande que RTK réécrit sous une forme absente de la liste est refusée. Le refus remonte comme tout refus de permission, et la liste est ajustée ([ADR 0009](../decisions/0009-permissions-par-role.md)).

## Remontée vers le coordinateur

- **La carte Orca est le seul canal** de l'orchestrateur de tâche vers le coordinateur (RET-013, [ADR 0015](../decisions/0015-remontee-carte-seule-coordinateur-flottant.md)) : il y tient le statut et le commentaire (table « Signalement d'attente » ci-dessous). Il n'écrit jamais dans le terminal du coordinateur : un `orca terminal send` s'insère dans la saisie du mainteneur, qui parle au coordinateur dans ce même terminal (constaté le 2026-10-09, Q-037).
- **Fichier à lire** : pour un événement qui attend le mainteneur (feu vert, blocage), le commentaire désigne le fichier à lire **dans le worktree de la tâche** : chemin du worktree, tel que le donne `orca worktree ps`, suivi du chemin relatif, par exemple `⏸ feu vert plan : <chemin du worktree>/docs/plans/12-file-a-toi.md`. Un chemin relatif seul se résoudrait sur `main`, où le fichier n'existe pas encore ou est périmé. Une ligne, jamais un long texte : le contexte du coordinateur doit rester léger.
- **Surveillance** : le coordinateur lit les cartes en arrière-plan (`orca worktree ps`). Il prévient le mainteneur pour une carte `in-review` qui commence par `⏸` ou `⛔`, et traite lui-même les segments `✓` et `💬`, sur toutes les cartes (voir « Signalement d'attente »). Il ne voit donc un événement qu'à sa lecture suivante.
- **Vers l'orchestrateur de tâche** : le coordinateur, lui, écrit dans le terminal de l'orchestrateur de tâche (`orca terminal send`) pour lui transmettre un feu vert ou une consigne. C'est un agent ; le mainteneur n'y écrit que lorsqu'il vient discuter de la tâche.
- **Feux verts** : le mainteneur les donne à l'un ou l'autre. Un feu vert donné dans le worktree, qui ouvre une action du coordinateur (merge ; publication des issues et des milestones après le feu vert de cadrage), est cité dans le commentaire de la carte, dans un segment `✓` placé après le segment d'état. Les segments `✓` **se cumulent** : chacun reste sur la ligne tant que le coordinateur n'a pas agi et n'en a pas accusé réception. Par exemple, pour un cadrage :
  - après l'ouverture de la PR : `⏸ feu vert merge : PR #12 · ✓ feu vert de cadrage : « ok cadrage », 14:32, session de l'orchestrateur de tâche` ;
  - après le feu vert merge, donné lui aussi dans le worktree, la tâche n'attend plus que le coordinateur : plus de segment d'état, carte en `in-review`, `✓ feu vert merge : « ok merge », 15:10, session de l'orchestrateur de tâche · ✓ feu vert de cadrage : « ok cadrage », 14:32, session de l'orchestrateur de tâche`.

  Un feu vert donné au coordinateur est transmis dans le terminal de l'orchestrateur de tâche.
- **Format de tout feu vert relayé** (cadrage, plan, recette, merge) : il cite **les mots exacts du mainteneur, l'heure et la session** où il l'a donné, par exemple `12-file-a-toi : feu vert recette, « ok recette », 14:32, session du coordinateur` dans le terminal de l'orchestrateur de tâche, ou un segment `✓` comme ci-dessus dans un commentaire de carte. Il vaut alors feu vert, et accord explicite au sens de la règle 6 d'`AGENTS.md` **pour l'action que ce feu vert ouvre, et elle seule** : commit, push et PR après le feu vert recette ou le feu vert de cadrage ; merge après le feu vert merge ; publication des issues et des milestones après le feu vert de cadrage. Un feu vert plan n'ouvre aucune de ces actions. Sans ces trois éléments, il ne vaut qu'information : la session qui doit agir demande la confirmation au mainteneur avant de passer à l'étape suivante. Limite : l'expéditeur d'un feu vert relayé n'est pas authentifié. Un message dans un terminal arrive comme s'il avait été tapé par le mainteneur, et un commentaire de carte peut être écrit par toute session qui dispose de la CLI `orca` (ADR 0013, ADR 0015).
- **Invites de permission** : une invite de l'orchestrateur de tâche s'affiche dans son terminal. Bloqué sur elle, il ne peut plus mettre à jour sa carte : seul l'état de l'agent affiché par Orca le montre. Quand une carte reste longtemps `in-progress` sans changer, le coordinateur vérifie l'état de l'agent dans Orca (ADR 0013).

## Relecture

- **Code applicatif** : au moins **deux relecteurs neufs en parallèle**, un par axe (RET-007) :
  - **A, justesse** : bugs, tests, cas limites ;
  - **B, conformité** : plan, ADR, lisibilité, sur-ingénierie, sécurité du repo public.

  Si le diff est gros, l'orchestrateur de tâche ajoute des relecteurs et leur partage le diff par zones, dans chaque axe, dans la limite du plafond d'agents actifs (voir « Garde-fous »).
- **Docs et petites corrections hors code applicatif** : un seul relecteur, qui couvre tout.
- **Boucle** (RET-006) : chaque tour relance **tous** les relecteurs, neufs, puisqu'une correction peut casser un axe déjà OK. La boucle s'arrête quand tous disent `RELECTURE : OK`.
- **Indépendance** : un relecteur ne lit pas les relectures des tours précédents, et le brief ne le lui demande pas. C'est l'**orchestrateur de tâche** qui compare les rapports d'un tour à l'autre pour repérer un constat qui revient (voir « Garde-fous »).
- **Suggestions** : une suggestion ne bloque pas la boucle, même si elle revient d'un tour à l'autre ; ce n'est pas une absence de progrès. L'orchestrateur de tâche ne la fait pas traiter de lui-même. Il les remonte avec le feu vert suivant (recette, ou cadrage) : le segment du feu vert désigne aussi, entre parenthèses, le dernier rapport où chacune revient, par exemple `⏸ feu vert recette : <chemin du worktree>/docs/plans/12-file-a-toi-recette.md (suggestion récurrente : <chemin du worktree>/docs/plans/12-file-a-toi-relecture-justesse-2.md)`. Le coordinateur les présente au mainteneur avec le feu vert ; si le mainteneur est dans le worktree, l'orchestrateur de tâche les lui cite directement. Le mainteneur décide de les ignorer, de les faire traiter dans la tâche, ou d'en faire une issue par un cadrage. Origine : au premier essai (#7), la même suggestion est revenue au tour 2, et aucune règle ne disait quoi en faire.
- **Rapport toujours dans un fichier** : `docs/plans/<tâche>-relecture-<axe>-<tour>.md` (`<axe>` vaut `justesse` ou `conformite`, sans accent ; par exemple `12-file-a-toi-relecture-justesse-2.md`), ou `docs/plans/<tâche>-relecture-<tour>.md` s'il n'y a qu'un relecteur. Jamais seulement dans le terminal : le terminal d'un agent ne garde que l'écran affiché, et un rapport rendu seulement là a déjà été perdu (friction constatée par le coordinateur, Q-023). On garde les tours précédents pour la comparaison.
- Les relecteurs sont des instances Claude neuves. La diversité de modèles est reportée à E2 (Q-034).

## Recette

La recette est une étape obligatoire, et celle de l'agent doit attraper ce que trouvera le mainteneur (RET-010). Le [recetteur](roles/recetteur.md) :
1. part d'une **installation neuve** : dépendances réinstallées depuis zéro dans le worktree, sans binaire ni cache préparé par un autre contrôle ;
2. déroule **d'abord la check-list du mainteneur**, qu'il a écrite avant tout contrôle, avec ses commandes et dans son ordre ;
3. lance ensuite les contrôles outillés (Playwright, etc.).

Pourquoi : à la recette du S1, le pilotage par Playwright avait téléchargé le binaire d'Electron avant que `pnpm dev` soit vérifié. Un contrôle avait préparé le terrain du suivant : la recette de l'agent est passée, celle du mainteneur a échoué.

## Signalement d'attente (file « À toi » provisoire)

L'orchestrateur de tâche tient sa carte ; le coordinateur la passe à « ✓ mergé » après le merge. La carte est le seul canal vers le coordinateur (RET-013).

Le commentaire est fait de segments séparés par ` · `, toujours dans cet ordre.

**1. En tête, l'état de la tâche** : un seul segment, qui fixe le statut de la carte.

| Situation | Statut Orca | Segment d'état |
|---|---|---|
| Un rôle travaille | `in-progress` | `▶ <rôle> en cours` |
| Feu vert attendu | `in-review` | `⏸ feu vert <cadrage / plan / recette / merge> : <chemin du worktree>/<fichier à lire>`, ou le numéro de la PR pour le feu vert merge |
| Bloqué (garde-fou, refus de permission) | `in-review` | `⛔ bloqué : <raison>`, avec le fichier à lire s'il y en a un |
| Terminé | `completed` | `✓ mergé`, posé par le coordinateur, qui merge |

**2. Ensuite, ce qui attend le coordinateur** : aucun, un ou plusieurs segments, qui ne changent pas le statut.

| Situation | Segment |
|---|---|
| Feu vert donné dans le worktree, pour une action du coordinateur (merge, publication) | `✓ feu vert <merge / de cadrage> : « <mots exacts> », <heure>, session de l'orchestrateur de tâche` |
| Retour du mainteneur reçu dans le worktree | `💬 retour : <une ligne>, <chemin absolu du fichier de l'analyse>` |

Exemple : `▶ implémenteur en cours · 💬 retour : garder le port 9333, <chemin du fichier>`. Une carte qui n'a plus de segment d'état, par exemple après un feu vert merge donné dans le worktree, passe en `in-review`.

**Qui regarde quoi** :
- le mainteneur regarde le **début** des cartes `in-review` : `⏸` ou `⛔`, c'est pour lui. Le coordinateur les lui résume s'il préfère lui parler ;
- le coordinateur surveille toutes les cartes en arrière-plan et cherche les segments `✓` et `💬`, **quel que soit le statut**. Une fois l'action faite ou le retour pris en compte, il en accuse réception dans le terminal de l'orchestrateur de tâche, qui retire alors le segment. Jusque-là, l'orchestrateur de tâche le garde, même quand le segment d'état change.

## Garde-fous

- Implémentation : **8 itérations au plus** (cycles test-correction). Au-delà, la tâche passe en « bloqué ».
- Relecture : pas de nombre de tours fixé (RET-006). La boucle s'arrête et la décision revient au mainteneur dans deux cas : **absence de progrès**, c'est-à-dire qu'un seul constat bloquant ou à corriger revient, en substance, au tour suivant ; ou **budget de l'étape dépassé**. Dans Orca, rien ne mesure ce budget : seule l'absence de progrès s'applique, en plus de l'alerte de quota que voit le mainteneur.
- **Plafond d'agents actifs** : environ **3 agents actifs** en même temps, tous niveaux confondus (coordinateur, orchestrateurs de tâche, rôles). Un agent actif est un agent en train de travailler ; un agent qui attend une réponse, un feu vert ou la fin d'un autre agent (par exemple un orchestrateur de tâche dans `orca terminal wait`) ne compte pas. Le coordinateur décide combien d'orchestrateurs de tâche tournent en même temps et combien d'agents chacun peut lancer. Origine : la limite d'usage a été atteinte avec 5 agents actifs dans la nuit du 8 au 9 octobre (RET-009, Q-038).
- Aucun rôle du pipeline ni du cadrage (rédacteur, planificateur, implémenteur, relecteur, recetteur) ne committe, ne pousse, ne merge ni ne publie sur GitHub. Après le feu vert correspondant, l'orchestrateur de tâche committe, pousse sa branche et ouvre la PR ; le coordinateur merge et publie les issues et les milestones (ADR 0012, ADR 0013).
- Le coordinateur et l'orchestrateur de tâche ne produisent aucun livrable, même « petit » : ils le font produire puis relire. La garde du coordinateur refuse ses écritures de fichiers hors des emplacements autorisés (mémoire, plan de la session, dossiers temporaires, installation d'un hook relu), à condition que la session soit lancée avec `JAM_ROLE=coordinateur` (ADR 0012). La garde ne reconnaît pas encore `JAM_ROLE=orchestrateur-tache` (Q-036).

## Ce qu'Orca ne permet pas (et que jam fera)

- Les permissions par rôle passent par les options de la CLI de l'agent et, pour le coordinateur, par un hook personnel du poste (`JAM_ROLE`). C'est du code, mais il reste local au poste et ne voit pas tout : un shell autorisé peut écrire des fichiers, la garde du coordinateur ne voit pas ses écritures par le shell, et elle ne protège pas une session lancée sans la variable. L'orchestrateur de tâche n'a pas encore la sienne (Q-036).
- Les listes blanches réduisent le risque sans le supprimer : `Bash(node *)`, `Bash(npx *)` ou `Bash(pnpm *)` permettent d'exécuter n'importe quoi (`node -e …`, `pnpm exec git push`).
- Le relecteur peut écrire tout fichier `*-relecture*.md`, donc aussi réécrire les rapports des tours précédents sur lesquels l'orchestrateur de tâche compare les constats. Le brief lui donne le nom exact de son fichier.
- Le relecteur et le recetteur lancent le script de test du repo, que l'implémenteur a pu modifier : par ce script, n'importe quelle commande leur reste accessible, `git push` compris (Q-025).
- Un rôle qui écrit dans le worktree pourrait modifier ce que liront les rôles lancés après lui : les réglages de Claude Code du projet (`.claude/`), `AGENTS.md` ou les profils de rôle. Les profils qui écrivent interdisent donc `Edit(.claude/**)`, et l'implémenteur interdit aussi `AGENTS.md`, `docs/process/` et `docs/plans/`. Les voies `node -e` et script de test restent ouvertes : seul un sandbox système les fermera (risque R-03 de la roadmap).
- Le durcissement des profils ne vient pas d'un retour du mainteneur : les formes `rtk` répondent à une friction constatée par le coordinateur (Q-022) ; `Edit(.claude/**)` et `git -C` ont été ajoutés par précaution, à la relecture.
- La « file » se réduit aux cartes `in-review` marquées `⏸` ou `⛔` : il n'y a pas de vue dédiée.
- Les boucles sont tenues par l'orchestrateur de tâche, donc par un agent : c'est lui qui relance les relecteurs et compare les constats d'un tour à l'autre. Dans jam, c'est le cœur, en code.
- L'état d'avancement vit dans les commentaires de cartes et dans `docs/plans/`, pas dans une base. La remontée vers le coordinateur dépend de l'orchestrateur de tâche, qui peut oublier de tenir sa carte, et le coordinateur ne la voit qu'à sa lecture suivante.
- Pas de canal entre agents qui épargne la saisie du mainteneur : `orca terminal send` écrit dans la saisie d'un terminal, que le mainteneur partage. D'où la carte seule vers le coordinateur (RET-013). La mailbox de l'orchestration d'Orca, expérimentale, n'est pas utilisée.
