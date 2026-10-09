# Développer jam avec Orca, en appliquant notre propre pipeline

> En attendant que jam sache dérouler son pipeline ([ADR 0008](../decisions/0008-boucle-exterieure-pipeline.md)), on le **déroule à la main dans Orca**. Deux bénéfices : jam est construit selon sa propre méthode, et on éprouve le pipeline sur papier avant de le coder. Chaque friction rencontrée est notée dans `OPEN-QUESTIONS.md` et alimente E0. Chaque remarque du mainteneur est consignée dans [`RETOURS.md`](../specs/RETOURS.md).

## Acteurs

- **Mainteneur** : donne les feux verts et fait la recette.
- **Coordinateur** : une session d'agent conversationnelle sur le worktree principal (`main`), dans laquelle le mainteneur parle (RET-008). Il crée les worktrees, lance un orchestrateur de tâche par tâche, suit les cartes Orca, tient le mainteneur informé, merge et publie **après** les feux verts. C'est l'interlocuteur unique du mainteneur s'il le souhaite. **Il orchestre et ne produit aucun livrable** (RET-001) : ni code, ni spec, ni ADR, ni issue, ni doc. C'est un rôle lui aussi, protégé par une garde quand il est lancé avec `JAM_ROLE=coordinateur` ([profil](roles/coordinateur.md), [ADR 0012](../decisions/0012-coordinateur-role-garde-fous-hook.md)).
- **Orchestrateur de tâche** : une session d'agent conversationnelle dans le worktree d'une tâche, lancée par le coordinateur (RET-009). Il lance les rôles de sa tâche, tient ses boucles et ses garde-fous, committe, pousse et ouvre la PR **après** les feux verts, et remonte l'avancement au coordinateur. Le mainteneur peut lui parler pour discuter de la tâche en détail. Il ne produit aucun livrable non plus ([profil](roles/orchestrateur-tache.md), [ADR 0013](../decisions/0013-orchestration-deux-niveaux.md)).
- **Rôles du pipeline et du cadrage** : rédacteur, planificateur, implémenteur, relecteur, recetteur. Chacun est une session d'agent **neuve**, lancée dans le worktree avec son profil ([`roles/`](roles/)) et ses permissions ([ADR 0009](../decisions/0009-permissions-par-role.md), [ADR 0012](../decisions/0012-coordinateur-role-garde-fous-hook.md) pour le rédacteur).

Tout livrable, code ou non, suit le même chemin : **production par un rôle → relecture indépendante → feu vert**.

L'orchestration à deux niveaux est décrite par l'[ADR 0013](../decisions/0013-orchestration-deux-niveaux.md) (RET-008, RET-009).

## Tâches, issues et milestones

- **Une tâche = une issue GitHub** sur [`jammindev/jam`](https://github.com/jammindev/jam).
- **Les milestones GitHub sont les jalons** de `04-ROADMAP.md` (S1, S2…).
- Le worktree d'une tâche porte le numéro de son issue : `<numéro>-<slug>`, par exemple `12-file-a-toi`.
- Un cadrage n'a pas d'issue : son worktree s'appelle `cadrage-<slug>`, par exemple `cadrage-s3`. C'est aussi le `<tâche>` de ses fichiers dans `docs/plans/`.
- Un jalon est découpé en petites issues au début du jalon, par un cadrage ([ADR 0011](../decisions/0011-pratiques-et-metriques-dora.md), petits lots).

## Cadrage et retours du mainteneur

Un cadrage a son worktree `cadrage-<slug>` et son orchestrateur de tâche, comme une tâche. Avant qu'une tâche entre dans le pipeline, le cadrage produit les specs, les ADR et les issues :

1. **Retour** : le coordinateur reformule la remarque du mainteneur, l'analyse, et la transmet dans le brief de l'orchestrateur de tâche du cadrage, qui la reprend dans le brief du rédacteur. Le rédacteur l'inscrit dans `RETOURS.md` (RET-NNN). Un retour donné directement à un orchestrateur de tâche suit le même chemin : il le reformule et l'analyse, prévient le coordinateur par un message court, et le transmet au rédacteur si sa tâche est un cadrage. Sinon, le coordinateur le confie à un cadrage.
2. **Rédaction** : le [rédacteur](roles/redacteur.md) modifie les docs et écrit les brouillons d'issues (`docs/plans/<tâche>-issues.md`).
3. **Relecture** : un [relecteur](roles/relecteur.md) neuf relit la rédaction. Les tours s'enchaînent jusqu'à `RELECTURE : OK` (voir « Relecture » ci-dessous).
4. **Feu vert cadrage** : le mainteneur valide. Le rédacteur passe alors les ADR concernées de « proposée » à « acceptée », reporte les mentions qu'elles prévoient dans le statut des ADR qu'elles complètent ou précisent, et passe les retours concernés à « appliqué ». L'orchestrateur de tâche committe, pousse et ouvre la PR.
5. **Feu vert merge** : la PR d'un cadrage passe, comme toute PR, par un feu vert merge (décision du mainteneur, RET-009). Le coordinateur merge, puis publie les issues et les milestones avec `gh` : leurs liens vers les docs du cadrage fonctionnent alors sur `main`.

## Correspondance entre le pipeline cible et Orca

| Étape | Cible (jam E0) | Aujourd'hui, dans Orca |
|---|---|---|
| Interlocuteur, niveau projet | Le cockpit (tableau des tâches, file « À toi ») et la session conversationnelle de `main`, le coordinateur (FR-040, après E0 selon l'ADR 0008, Q-039) | Le coordinateur, sur `main` |
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
| PR + CI | Le cœur via `gh` | L'orchestrateur de tâche : push, `gh pr create` + CI |
| **Feu vert 3** | File « À toi » | Commentaire « ⏸ feu vert merge » |
| Merge | `gh pr merge` | Le coordinateur, seul à merger : `gh pr merge`, puis `git pull` sur `main` |
| Nettoyage | Le cœur | Le coordinateur : fermeture des terminaux du worktree, `orca worktree rm` + suppression de la branche |
| État d'une tâche et remontée | Persisté par le cœur (FR-027). Remontée structurelle : les deux niveaux lisent le même état | Carte Orca, tenue par l'orchestrateur de tâche, plus un message court au coordinateur quand le mainteneur est attendu |
| Feu vert relayé | Sans objet : le feu vert est une action du cockpit, enregistrée par le cœur | Message court qui cite les mots exacts du mainteneur, l'heure et la session (voir « Remontée vers le coordinateur ») |

## Lancement du coordinateur

Dans un **terminal Orca** du worktree principal, sur `main` (RET-008). Le terminal Orca lui donne un handle : sans lui, les orchestrateurs de tâche ne pourraient pas lui envoyer de messages (`orca terminal send`).
```sh
JAM_ROLE=coordinateur claude
```
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

Le brief d'un orchestrateur de tâche contient : le chemin de son profil, la tâche, le handle du terminal du coordinateur pour les messages, le nombre d'agents qu'il peut lancer à la fois, le critère de fin et, pour un cadrage, les retours du mainteneur avec leur analyse.

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

- **La carte Orca est la référence** : l'orchestrateur de tâche y tient le statut et le commentaire (table « Signalement d'attente » ci-dessous). Le coordinateur lit les cartes avec `orca worktree ps`.
- **Message court** : pour un événement qui attend le mainteneur (feu vert, blocage), l'orchestrateur de tâche prévient aussi le coordinateur, dans son terminal (`orca terminal send`). Une ligne : la tâche, l'événement et le fichier à lire. Le fichier est désigné **dans le worktree de la tâche** : chemin du worktree, tel que le donne `orca worktree ps`, suivi du chemin relatif, par exemple `12-file-a-toi : ⏸ feu vert plan, <chemin du worktree>/docs/plans/12-file-a-toi.md`. Un chemin relatif seul se résoudrait sur `main`, où le fichier n'existe pas encore ou est périmé. Jamais un long texte : le contexte du coordinateur doit rester léger. Le canal reste à éprouver (Q-037).
- **Feux verts** : le mainteneur les donne à l'un ou l'autre. Un feu vert donné dans le worktree est remonté au coordinateur par un message court ; un feu vert donné au coordinateur est transmis à l'orchestrateur de tâche.
- **Format de tout feu vert relayé** (cadrage, plan, recette, merge) : il cite **les mots exacts du mainteneur, l'heure et la session** où il l'a donné, par exemple `12-file-a-toi : feu vert merge, « ok merge », 14:32, session du coordinateur`. Il vaut alors feu vert, et accord explicite au sens de la règle 6 d'`AGENTS.md` **pour l'action que ce feu vert ouvre, et elle seule** : commit, push et PR après le feu vert recette ou le feu vert de cadrage ; merge après le feu vert merge ; publication des issues et des milestones après le feu vert de cadrage. Un feu vert plan n'ouvre aucune de ces actions. Sans ces trois éléments, il ne vaut qu'information : la session qui doit agir demande la confirmation au mainteneur avant de passer à l'étape suivante. Limite : l'expéditeur d'un message relayé n'est pas authentifié (ADR 0013).
- **Invites de permission** : une invite de l'orchestrateur de tâche s'affiche dans son terminal. Bloqué sur elle, il ne peut ni mettre à jour sa carte ni prévenir le coordinateur : seul l'état de l'agent affiché par Orca le montre. Quand une carte reste longtemps `in-progress` sans changer, le coordinateur vérifie l'état de l'agent dans Orca (ADR 0013).

## Relecture

- **Code applicatif** : au moins **deux relecteurs neufs en parallèle**, un par axe (RET-007) :
  - **A, justesse** : bugs, tests, cas limites ;
  - **B, conformité** : plan, ADR, lisibilité, sur-ingénierie, sécurité du repo public.

  Si le diff est gros, l'orchestrateur de tâche ajoute des relecteurs et leur partage le diff par zones, dans chaque axe, dans la limite du plafond d'agents actifs (voir « Garde-fous »).
- **Docs et petites corrections hors code applicatif** : un seul relecteur, qui couvre tout.
- **Boucle** (RET-006) : chaque tour relance **tous** les relecteurs, neufs, puisqu'une correction peut casser un axe déjà OK. La boucle s'arrête quand tous disent `RELECTURE : OK`.
- **Indépendance** : un relecteur ne lit pas les relectures des tours précédents, et le brief ne le lui demande pas. C'est l'**orchestrateur de tâche** qui compare les rapports d'un tour à l'autre pour repérer un constat qui revient (voir « Garde-fous »).
- **Rapport toujours dans un fichier** : `docs/plans/<tâche>-relecture-<axe>-<tour>.md` (`<axe>` vaut `justesse` ou `conformite`, sans accent ; par exemple `12-file-a-toi-relecture-justesse-2.md`), ou `docs/plans/<tâche>-relecture-<tour>.md` s'il n'y a qu'un relecteur. Jamais seulement dans le terminal : le terminal d'un agent ne garde que l'écran affiché, et un rapport rendu seulement là a déjà été perdu (friction constatée par le coordinateur, Q-023). On garde les tours précédents pour la comparaison.
- Les relecteurs sont des instances Claude neuves. La diversité de modèles est reportée à E2 (Q-034).

## Recette

La recette est une étape obligatoire, et celle de l'agent doit attraper ce que trouvera le mainteneur (RET-010). Le [recetteur](roles/recetteur.md) :
1. part d'une **installation neuve** : dépendances réinstallées depuis zéro dans le worktree, sans binaire ni cache préparé par un autre contrôle ;
2. déroule **d'abord la check-list du mainteneur**, qu'il a écrite avant tout contrôle, avec ses commandes et dans son ordre ;
3. lance ensuite les contrôles outillés (Playwright, etc.).

Pourquoi : à la recette du S1, le pilotage par Playwright avait téléchargé le binaire d'Electron avant que `pnpm dev` soit vérifié. Un contrôle avait préparé le terrain du suivant : la recette de l'agent est passée, celle du mainteneur a échoué.

## Signalement d'attente (file « À toi » provisoire)

L'orchestrateur de tâche tient sa carte ; le coordinateur la passe à « ✓ mergé » après le merge.

| Situation | Statut Orca | Commentaire de la carte | Message au coordinateur |
|---|---|---|---|
| Un rôle travaille | `in-progress` | `▶ <rôle> en cours` | Non |
| Feu vert attendu | `in-review` | `⏸ feu vert <cadrage / plan / recette / merge>` | Oui |
| Bloqué (garde-fou, refus de permission) | `in-review` | `⛔ bloqué : <raison>` | Oui |
| Terminé | `completed` | `✓ mergé` | Non : c'est le coordinateur qui merge |

Le mainteneur n'a qu'une chose à regarder : les cartes en `in-review`. Le coordinateur les lui résume s'il préfère lui parler.

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
- La « file » se réduit aux cartes `in-review` : il n'y a pas de vue dédiée.
- Les boucles sont tenues par l'orchestrateur de tâche, donc par un agent : c'est lui qui relance les relecteurs et compare les constats d'un tour à l'autre. Dans jam, c'est le cœur, en code.
- L'état d'avancement vit dans les commentaires de cartes et dans `docs/plans/`, pas dans une base. La remontée vers le coordinateur dépend de l'orchestrateur de tâche, qui peut oublier un message ; la carte reste la référence.
