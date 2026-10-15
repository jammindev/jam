# La méthode

Une tâche = une issue GitHub = un worktree Orca. Des rôles d'agents neufs la font avancer (plan, implémentation en TDD, relecture, recette) ; le mainteneur donne les feux verts et ne code pas. Ce process est générique : ce qui est propre à un projet est dans sa **fiche**, `docs/methode.md` ([gabarit](fiche-projet.md)). L'origine des règles est dans les ADR du plugin (`docs/decisions/`) ; l'ADR 0018 dit aussi ce que chaque règle remplace.

## Acteurs

- **Mainteneur** : donne les feux verts et recette.
- **Coordinateur** ([profil](../roles/coordinateur.md)) : une session sur le worktree principal (`main`) du projet, où parle le mainteneur ; une par projet. Il lance les tâches, suit les cartes, merge et publie après les feux verts.
- **Orchestrateur de tâche** ([profil](../roles/orchestrateur-tache.md)) : au niveau *standard*, une session dans le worktree d'une tâche. Il lance les rôles, tient les boucles et la carte, committe, pousse et ouvre la PR après les feux verts.
- **Rôles** : [rédacteur](../roles/redacteur.md), [planificateur](../roles/planificateur.md), [implémenteur](../roles/implementeur.md), [relecteur](../roles/relecteur.md), [recetteur](../roles/recetteur.md). Chacun est une session **neuve**, lancée dans le worktree avec son profil et ses permissions.

Coordinateur et orchestrateur de tâche ne produisent aucun livrable. Tout livrable suit le même chemin : production par un rôle, relecture indépendante, feu vert (RET-001).

## Niveaux

La fiche fixe le niveau par défaut du projet. Une tâche peut monter d'un niveau, sur un motif écrit dans l'issue ou au plan (FR-049).

| Niveau | Pour | Déroulé |
|---|---|---|
| *léger* | tout projet, sauf ci-dessous | Ni orchestrateur de tâche ni planificateur : l'issue tient lieu de plan, sans feu vert plan. Le coordinateur, qui conduit aussi les cadrages, lance l'implémenteur (ou le rédacteur), puis **un seul relecteur**, tient la carte et la boucle de relecture, committe et ouvre la PR après le feu vert recette, merge après le feu vert merge. Pas de recetteur : l'implémenteur (ou le rédacteur) écrit en fin de travail la check-list du mainteneur (`docs/plans/<tâche>-recette.md`, format du recetteur), et le mainteneur recette (FR-052). |
| *standard* | projet en production qui touche à l'argent ou à des données de personnes | Le déroulé ci-dessous. |
| *renforcé* | au-dessus de *standard* | Sans contenu à ce jour (Q-061). |

## Déroulé *standard*

1. **Plan** : le planificateur écrit `docs/plans/<tâche>.md`. **Feu vert plan.**
2. **Implémentation** : l'implémenteur suit le plan en TDD, jusqu'au vert.
3. **Relecture** : relecteurs neufs, en boucle jusqu'à `RELECTURE : OK`.
4. **Recette** : le recetteur, puis le mainteneur. **Feu vert recette.**
5. **PR** : l'orchestrateur de tâche committe, pousse et ouvre la PR ; la CI passe. **Feu vert merge.**
6. **Merge** : le coordinateur merge, puis nettoie le worktree.

En conflit avec `main` : `⛔ bloqué : conflit avec main`, et le coordinateur décide avec le mainteneur ; s'il se résout, la session qui conduit la tâche fusionne `main` sans rebase et relance l'implémenteur (le rédacteur pour des docs) sur le conflit, puis les tests, et le push après un nouveau feu vert.

Un cadrage (worktree `cadrage-<slug>`, sans issue ; c'est son `<tâche>`) produit specs, ADR et brouillons d'issues (`docs/plans/<tâche>-issues.md`) : rédacteur, un relecteur en boucle, **feu vert de cadrage**, PR, feu vert merge. Après le merge, le coordinateur publie les issues et les milestones : leurs liens vers les docs marchent alors sur `main`.

**Retour du mainteneur** : reçu par le coordinateur, il le reformule et l'analyse dans le brief d'un cadrage, dont le rédacteur l'inscrit dans les retours du projet. Reçu dans un worktree, l'orchestrateur de tâche l'analyse dans `docs/plans/<tâche>-retours.md`, note de suivi non relue, committée avec la tâche, et le signale par un segment `💬` (remplace le dossier temporaire, Q-058). Au niveau *léger*, le retour remonte au coordinateur, comme reçu par lui.

## Lancement

Toute session d'agent est lancée par Orca, sur le poste de travail, jamais par SSH, qui n'a pas les identifiants. Rien d'indispensable ne vit dans un dossier temporaire (ADR 0017, NFR-013).

- **Coordinateur**, dans un terminal du worktree principal : `JAM_ROLE=coordinateur claude` (`--continue` pour reprendre).
- **Orchestrateur de tâche et rôles**, par le script de lancement, qui compte les agents en cours, crée le worktree s'il manque, ouvre le terminal avec `JAM_ROLE=<rôle>` et y envoie le brief, une fois l'agent prêt :

```sh
python3 <plugin>/scripts/launch_task.py --repo <repoId> --worktree <tâche> --role <rôle> \
  --command '<commande du profil>' --brief <fichier> --cap 6 --project-cap <plafond de la fiche>
```

`<plugin>` est le dossier du plugin installé : le hook de démarrage affiche, quand le repo a une fiche, une ligne « Méthode » avec la fiche, ce process et les profils, en chemins absolus. Les profils se lisent là, jamais dans un worktree (ADR 0018).

- **Brief** : le chemin du profil, la tâche, les livrables, le critère de fin ; pour un orchestrateur de tâche, aussi le nombre d'agents qu'il peut lancer à la fois, et les retours analysés d'un cadrage. Le profil prime sur le brief.
- **Lecture** : un rôle ne lit rien hors du worktree et des chemins de son brief, transcripts des autres sessions compris.
- **Fin d'un rôle** : `orca terminal read` lit sa ligne de fin (`PLAN PRÊT`, `RELECTURE : OK`…) ; le contenu est dans le fichier qu'il a écrit. Son terminal est fermé dès cette ligne : ouvert, il compte dans les agents en cours.

## Carte, feux verts et veille

La carte Orca est le **seul canal** de l'orchestrateur de tâche vers le coordinateur. Il n'écrit jamais dans le terminal du coordinateur, dont la saisie est celle du mainteneur (RET-013, ADR 0015).

**Messages au mainteneur** : tout message qui lui est adressé (la carte, où le nom du worktree désigne la tâche ; la tête « À décider » d'un fichier ouvert pour lui ; le résumé du coordinateur) se lit seul. Il nomme le projet et la tâche en mots, la tâche suivie de son numéro d'issue sous la forme `(#<n>)`, que lit la mesure, et remplace toute autre référence interne (friction, ADR, RET, FR) par ce qu'elle désigne, le numéro au plus entre parenthèses (RET-019).

Le commentaire de la carte est fait de segments séparés par ` · `. En tête, un seul segment d'état, qui fixe le statut :

| Situation | Statut | Segment d'état |
|---|---|---|
| Un rôle travaille | `in-progress` | `▶ <rôle> en cours` |
| Feu vert attendu | `in-review` | `⏸ feu vert <plan / recette / cadrage / merge> : <chemin du worktree>/<fichier à lire>`, ou `PR #<n>` pour le merge |
| Bloqué | `in-review` | `⛔ bloqué : <raison>` |
| Terminé | `completed` | `✓ mergé`, posé par le coordinateur |

Ensuite, ce qui attend le coordinateur : `✓ feu vert <merge / de cadrage> : « <mots exacts> », <heure>, session de l'orchestrateur de tâche`, ou `💬 retour : <une ligne>, <chemin du worktree>/docs/plans/<tâche>-retours.md`. Chacun reste jusqu'à l'accusé de réception du coordinateur, dans le terminal de l'orchestrateur de tâche. Une carte sans segment d'état passe en `in-review`. Un fichier se désigne par le chemin du worktree, puisque `main` ne l'a pas encore.

**Relais d'un feu vert** (FR-053) :
- feu vert plan ou recette : un « ok » transmis suffit ;
- tout autre feu vert, merge compris : les mots exacts du mainteneur, l'heure et la session. Sans eux, il ne vaut qu'information : la session qui doit agir demande confirmation au mainteneur ;
- un feu vert n'ouvre que son action : commit, push et PR après le feu vert recette ou de cadrage ; merge après le feu vert merge ; publication après le feu vert de cadrage. Le feu vert plan n'en ouvre aucune ;
- un feu vert donné dans le worktree pour une action du coordinateur (merge, publication) remonte par un segment `✓`, puis **le mainteneur le confirme dans le terminal du coordinateur** avant qu'il agisse : la garde de sortie ne lit que les messages de la session qui agit ;
- dans un terminal (`orca terminal send`), un relais est court et sans négation, que la garde lirait comme un refus ; 30 s après, `orca terminal read` vérifie qu'il est arrivé (RET-017).

**Veille** (RET-017) : le coordinateur garde en arrière-plan `python3 <plugin>/scripts/watch_cards.py <projet>`, qui rend la main quand une carte passe en `⏸` ou `⛔`, porte un segment `✓` ou `💬`, ou, sur une carte `▶`, quand un agent attend une autorisation ou qu'aucun agent n'y travaille depuis 10 min (`--idle-minutes`). Un seul réveil par épisode. Elle est relancée aussitôt, avant de traiter le réveil : ce qui change entre-temps compterait comme vu. Pour une carte inactive, le coordinateur relance l'orchestrateur de tâche (au niveau *léger*, il lit la fin du rôle et reprend la tâche) ou passe la carte en `⛔`, ce qui clôt l'épisode (remplace la vérification à la main d'une carte longtemps `in-progress`). Une carte `▶` au commentaire figé alors que son agent travaille peut cacher une fenêtre d'autorisation du système : le coordinateur prévient le mainteneur (ADR 0017, Q-059).

## Relecture

- **Code** : deux relecteurs neufs par tour, en parallèle : **justesse** (bugs, tests, cas limites) et **conformité** (plan, ADR, lisibilité, sur-ingénierie, sécurité d'un repo public), plus la grille de la fiche. Sur un gros diff, l'orchestrateur de tâche ajoute des relecteurs par zones, sous les plafonds. **Docs, petites corrections, niveau *léger*** : un seul relecteur, sur les deux axes.
- **Constats** : bloquant, à corriger ou suggestion. **Seuil « assez bon »** (FR-050) : un constat n'est « à corriger » que s'il écrit un scénario d'échec (entrée, mauvais résultat) ou cite l'exigence, l'ADR ou le critère de fin qu'il viole ; sinon c'est une suggestion. Une suggestion reclassée « à corriger » au tour suivant sans nouveau scénario reste une suggestion.
- **Boucle** : chaque tour relance tous les relecteurs, neufs. Elle s'arrête quand aucun ne trouve de bloquant ni de « à corriger » (`RELECTURE : OK`), ou, décision au mainteneur, quand un même constat revient en substance au tour suivant (absence de progrès). Un relecteur ne lit pas les tours précédents : c'est la session qui conduit la tâche qui compare.
- **Suggestions** : elles ne bloquent pas. Celles qui reviennent sont remontées avec le feu vert suivant, le segment désignant le dernier rapport où chacune revient. Le mainteneur les ignore, les fait traiter, ou en fait une issue (ADR 0018).
- **Rapport** dans un fichier (le terminal ne garde que l'écran) : `docs/plans/<tâche>-relecture-<axe>-<tour>.md` (`justesse` ou `conformite`), ou `docs/plans/<tâche>-relecture-<tour>.md` pour un relecteur seul (ADR 0018).

## Recette

Au niveau *standard*, le recetteur part d'une installation neuve, déroule d'abord la check-list du mainteneur, écrite avant tout contrôle, avec ses commandes et dans son ordre, puis les tests et les contrôles outillés : un contrôle ne doit pas préparer le terrain du suivant (RET-010). Pour une interface, quand un navigateur piloté est disponible, il livre des captures ou un enregistrement du parcours (FR-054). Puis le mainteneur recette.

## Garde-fous

- Implémentation : 8 itérations sans progrès au plus, puis `BLOQUÉ`.
- **Plafonds** (FR-051) : au plus **6 agents en cours** sur le poste, tous projets confondus, et au plus le plafond de la fiche pour le projet, borne propre au projet. Un agent en cours est une session d'agent que liste `orca terminal list`, qu'elle travaille ou attende (remplace le plafond d'« agents actifs »). Toute session qui lance un agent les compte d'abord : le script de lancement le fait.
- Aucun rôle ne committe, ne pousse, ne merge ni ne publie.
- Hooks du plugin, messages préfixés `[jam]` : **garde de sortie** (commit, push et écritures `gh`, dont `gh pr merge`, refusés sans accord dans le dernier message du mainteneur de la session ; un `git merge` local passe) ; **garde du coordinateur** (écritures de fichiers, si `JAM_ROLE=coordinateur` au lancement) ; reprise de contexte ; état git.

## Permissions

- Les rôles tournent en `--permission-mode dontAsk` avec une liste blanche : toute commande hors liste est refusée sans invite. Coordinateur et orchestrateur de tâche sont interactifs : hors des réglages du poste, le mainteneur accorde.
- `Edit(…)` couvre aussi la création. Une règle `Edit` s'écrit ancrée par `/` (`Edit(/docs/plans/x.md)`, résolue depuis le dossier de lancement de la session) ou absolue (`//` suivi du chemin sans son `/` initial). **Une session lancée avec `--plugin-dir <dossier>` ne peut écrire dans ce dossier**, quelle que soit la règle : sous `--plugin-dir <worktree>`, le recetteur écrit d'emblée son rapport dans son dossier de recette, et un rédacteur le recopie tel quel. Même repli du recetteur si une autre écriture permise est refusée.
- Les interdits protègent ce que lisent les rôles suivants : `.claude/`, `AGENTS.md`, `CLAUDE.md`, la fiche, le plan et les rapports de relecture.
- **RTK** : un hook du poste peut réécrire une commande (`git status` devient `rtk git status`), et la permission porte sur la forme réécrite. Chaque règle `Bash` existe donc aussi en `rtk …`, aussi étroite (ADR 0018).
- Limites : une liste blanche réduit le risque sans le supprimer. Par la commande de test, que l'implémenteur a pu modifier, n'importe quelle commande reste accessible (Q-025). L'expéditeur d'un feu vert relayé n'est pas authentifié.

## Mesure

Le corps de chaque PR note le temps du mainteneur sur l'issue (FR-055, RET-018), estimé par `python3 <plugin>/scripts/maintainer_time.py --main <worktree principal> --worktree <worktree de la tâche> --issue <n>`. Le script ne lit que les sessions du worktree principal, celles de la tâche mêlant des relais d'agents : la recette du mainteneur, faite dans une session du worktree de la tâche, n'est pas comptée, ni un feu vert tapé là. Un message compte s'il nomme la tâche (`#<n>` ou le nom du worktree) ou répond à un tour du coordinateur qui la nomme ; les messages à moins de 10 min l'un de l'autre forment un moment, qui vaut sa durée plus 3 min de lecture. Les commandes `!` ne comptent pas.
