# Développer jam avec Orca, en appliquant notre propre pipeline

> En attendant que jam sache dérouler son pipeline ([ADR 0008](../decisions/0008-boucle-exterieure-pipeline.md)), on le **déroule à la main dans Orca**. Deux bénéfices : jam est construit selon sa propre méthode, et on éprouve le pipeline sur papier avant de le coder. Chaque friction rencontrée est notée dans `OPEN-QUESTIONS.md` et alimente E0. Chaque remarque du mainteneur est consignée dans [`RETOURS.md`](../specs/RETOURS.md).

## Acteurs

- **Mainteneur** : donne les feux verts et fait la recette.
- **Coordinateur** : une session d'agent conversationnelle, dans laquelle le mainteneur parle. Il crée les worktrees, lance les rôles, lit leurs sorties, tient le mainteneur informé, committe, publie et merge **après** les feux verts. **Il orchestre et ne produit aucun livrable** (RET-001) : ni code, ni spec, ni ADR, ni issue, ni doc. C'est un rôle lui aussi, protégé par une garde quand il est lancé avec `JAM_ROLE=coordinateur` ([profil](roles/coordinateur.md), [ADR 0012](../decisions/0012-coordinateur-role-garde-fous-hook.md)).
- **Rôles du pipeline et du cadrage** : rédacteur, planificateur, implémenteur, relecteur, recetteur. Chacun est une session d'agent **neuve**, lancée dans le worktree avec son profil ([`roles/`](roles/)) et ses permissions ([ADR 0009](../decisions/0009-permissions-par-role.md), [ADR 0012](../decisions/0012-coordinateur-role-garde-fous-hook.md) pour le rédacteur).

Tout livrable, code ou non, suit le même chemin : **production par un rôle → relecture indépendante → feu vert**.

## Tâches, issues et milestones

- **Une tâche = une issue GitHub** sur [`jammindev/jam`](https://github.com/jammindev/jam).
- **Les milestones GitHub sont les jalons** de `04-ROADMAP.md` (S1, S2…).
- Le worktree d'une tâche porte le numéro de son issue : `<numéro>-<slug>`, par exemple `12-file-a-toi`.
- Un cadrage n'a pas d'issue : son worktree s'appelle `cadrage-<slug>`, par exemple `cadrage-s3`. C'est aussi le `<tâche>` de ses fichiers dans `docs/plans/`.
- Un jalon est découpé en petites issues au début du jalon, par un cadrage ([ADR 0011](../decisions/0011-pratiques-et-metriques-dora.md), petits lots).

## Cadrage et retours du mainteneur

Avant qu'une tâche entre dans le pipeline, le cadrage produit les specs, les ADR et les issues :

1. **Retour** : le coordinateur reformule la remarque du mainteneur, l'analyse, et la transmet dans le brief du rédacteur. Le rédacteur l'inscrit dans `RETOURS.md` (RET-NNN).
2. **Rédaction** : le [rédacteur](roles/redacteur.md) modifie les docs et écrit les brouillons d'issues (`docs/plans/<tâche>-issues.md`).
3. **Relecture** : un [relecteur](roles/relecteur.md) neuf relit la rédaction. Les tours s'enchaînent jusqu'à `RELECTURE : OK` (voir « Relecture » ci-dessous).
4. **Feu vert cadrage** : le mainteneur valide. Le rédacteur passe alors les ADR concernées de « proposée » à « acceptée », reporte les mentions qu'elles prévoient dans le statut des ADR qu'elles complètent ou précisent, et passe les retours concernés à « appliqué ». Le coordinateur committe, puis publie les issues et les milestones avec `gh`.

## Correspondance entre le pipeline cible et Orca

| Étape | Cible (jam E0) | Aujourd'hui, dans Orca |
|---|---|---|
| Tâche | Issue GitHub | Issue GitHub, rattachée au milestone de son jalon |
| Worktree | Créé par le cœur | `orca worktree create --name <numéro>-<slug> --no-parent` |
| Plan | Rôle planificateur | Terminal dans le worktree, agent en `dontAsk` + lecture seule, écrit uniquement `docs/plans/<tâche>.md` |
| **Feu vert 1** | File « À toi » | Statut du worktree `in-review`, commentaire « ⏸ feu vert plan ». Le mainteneur répond au coordinateur |
| Implémentation TDD | Rôle implémenteur, boucle jusqu'au vert | Nouveau terminal, agent en `dontAsk` + écriture dans le worktree + liste blanche shell. Ni commit ni push |
| Relecture | Rôle relecteur, contexte neuf, un par axe | Un terminal neuf par relecteur et par tour, lecture seule, un fichier de relecture chacun. Les corrections repartent vers l'implémenteur, jusqu'à OK de tous |
| Recette | Rôle recetteur, puis mainteneur | Contrôles automatisables par l'agent, puis test manuel du mainteneur |
| **Feu vert 2** | File « À toi » | Statut `in-review`, commentaire « ⏸ feu vert recette ». Le coordinateur committe une fois le feu vert donné |
| PR + CI | Le cœur via `gh` | `gh pr create` + CI |
| **Feu vert 3** | File « À toi » | Commentaire « ⏸ feu vert merge » |
| Merge | `gh pr merge` | `gh pr merge` |
| Nettoyage | Le cœur | `orca worktree rm` + suppression de la branche |

## Lancement d'un rôle (coordinateur)

```sh
# 1. Worktree de la tâche
orca worktree create --repo id:<repoId> --name <tâche> --no-parent --json
# 2. Terminal du rôle (profil de permissions dans roles/<rôle>.md)
orca terminal create --worktree id:<repoId>::<chemin> --title <rôle> --command '<commande du rôle>' --json
# 3. Attendre que l'agent soit prêt, puis envoyer le brief
orca terminal wait --terminal <handle> --for tui-idle --timeout-ms 60000 --json
orca terminal send --terminal <handle> --text "<brief>" --enter --json
# 4. Suivre
orca terminal wait --terminal <handle> --for tui-idle --timeout-ms 1800000 --json
orca terminal read --terminal <handle> --json
```

Le brief d'un rôle contient toujours : le chemin du profil de rôle à lire, la tâche (numéro d'issue, ou `cadrage-<slug>`), les livrables attendus et le critère de fin.

### Hook de démarrage du poste du mainteneur

Un hook personnel du poste, installé hors du repo, donne à chaque session d'agent son contexte dès le démarrage (RET-004) :
- le worktree, la branche et les autres worktrees actifs ;
- quand la session tourne dans Orca : la carte du worktree (statut, commentaire, issue et PR liées), le rôle de la session (`JAM_ROLE`, ou « session libre »), un avertissement par autre agent actif dans le même worktree, la CLI Orca et le chemin du process du repo.

C'est la préfiguration de FR-038 : dans jam, c'est le cœur qui injectera ce contexte.

### Hook RTK du poste du mainteneur

> Origine : friction constatée par le coordinateur en déroulant le pipeline (refus de permissions dus à la réécriture RTK, Q-022). Ce n'est pas un retour du mainteneur.

RTK est un outil installé sur le poste du mainteneur : il compacte la sortie des commandes shell pour économiser le contexte des agents. Un hook de Claude Code réécrit chaque commande que RTK sait traiter : `git status` devient `rtk git status`, `cat <fichier>` devient `rtk read <fichier>`.

Le hook ne fait que réécrire la commande : il ne décide rien. **La permission est contrôlée ensuite, sur la forme réécrite.** Deux conséquences :
- une règle sur la forme simple ne couvre pas la commande réécrite. Les listes blanches et les listes d'interdits doivent donc **couvrir les deux formes**, par exemple `"Bash(git status)" "Bash(rtk git status)"` ;
- une règle large sur une forme `rtk` autorise plus qu'il n'y paraît : `Bash(rtk read *)` autorise tout `cat`, `Bash(rtk ls *)` tout `ls`, `Bash(rtk gh *)` tout `gh`, écritures comprises. Une règle `rtk …` s'écrit donc aussi étroitement que la règle simple qu'elle double.

Une commande que RTK réécrit sous une forme absente de la liste est refusée. Le refus remonte comme tout refus de permission, et la liste est ajustée ([ADR 0009](../decisions/0009-permissions-par-role.md)).

## Relecture

- **Code applicatif** : au moins **deux relecteurs neufs en parallèle**, un par axe (RET-007) :
  - **A, justesse** : bugs, tests, cas limites ;
  - **B, conformité** : plan, ADR, lisibilité, sur-ingénierie, sécurité du repo public.

  Si le diff est gros, le coordinateur ajoute des relecteurs et leur partage le diff par zones, dans chaque axe.
- **Docs et petites corrections hors code applicatif** : un seul relecteur, qui couvre tout.
- **Boucle** (RET-006) : chaque tour relance **tous** les relecteurs, neufs, puisqu'une correction peut casser un axe déjà OK. La boucle s'arrête quand tous disent `RELECTURE : OK`.
- **Indépendance** : un relecteur ne lit pas les relectures des tours précédents, et le brief ne le lui demande pas. C'est le **coordinateur** qui compare les rapports d'un tour à l'autre pour repérer un constat qui revient (voir « Garde-fous »).
- **Rapport toujours dans un fichier** : `docs/plans/<tâche>-relecture-<axe>-<tour>.md` (`<axe>` vaut `justesse` ou `conformite`, sans accent ; par exemple `12-file-a-toi-relecture-justesse-2.md`), ou `docs/plans/<tâche>-relecture-<tour>.md` s'il n'y a qu'un relecteur. Jamais seulement dans le terminal : le terminal d'un agent ne garde que l'écran affiché, et un rapport rendu seulement là a déjà été perdu (friction constatée par le coordinateur, Q-023). On garde les tours précédents pour la comparaison.
- Les relecteurs sont des instances Claude neuves. La diversité de modèles est reportée à E2 (Q-034).

## Signalement d'attente (file « À toi » provisoire)

| Situation | Statut Orca | Commentaire de la carte |
|---|---|---|
| Un rôle travaille | `in-progress` | `▶ <rôle> en cours` |
| Feu vert attendu | `in-review` | `⏸ feu vert <cadrage / plan / recette / merge>` |
| Bloqué (garde-fou, refus de permission) | `in-review` | `⛔ bloqué : <raison>` |
| Terminé | `completed` | `✓ mergé` |

Le mainteneur n'a qu'une chose à regarder : les cartes en `in-review`.

## Garde-fous

- Implémentation : **8 itérations au plus** (cycles test-correction). Au-delà, la tâche passe en « bloqué ».
- Relecture : pas de nombre de tours fixé (RET-006). La boucle s'arrête et la décision revient au mainteneur dans deux cas : **absence de progrès**, c'est-à-dire qu'un seul constat bloquant ou à corriger revient, en substance, au tour suivant ; ou **budget de l'étape dépassé**. Dans Orca, rien ne mesure ce budget : seule l'absence de progrès s'applique, en plus de l'alerte de quota que voit le mainteneur.
- Aucun rôle du pipeline ni du cadrage (rédacteur, planificateur, implémenteur, relecteur, recetteur) ne committe, ne pousse, ne merge ni ne publie sur GitHub. Seul le coordinateur le fait, après le feu vert (ADR 0012).
- Le coordinateur ne produit aucun livrable, même « petit » : il le fait produire puis relire. Sa garde refuse ses écritures de fichiers hors des emplacements autorisés (mémoire, plan de la session, dossiers temporaires, installation d'un hook relu), à condition que la session soit lancée avec `JAM_ROLE=coordinateur` (ADR 0012).

## Ce qu'Orca ne permet pas (et que jam fera)

- Les permissions par rôle passent par les options de la CLI de l'agent et, pour le coordinateur, par un hook personnel du poste (`JAM_ROLE`). C'est du code, mais il reste local au poste et ne voit pas tout : un shell autorisé peut écrire des fichiers, la garde du coordinateur ne voit pas ses écritures par le shell, et elle ne protège pas une session lancée sans la variable.
- Les listes blanches réduisent le risque sans le supprimer : `Bash(node *)`, `Bash(npx *)` ou `Bash(pnpm *)` permettent d'exécuter n'importe quoi (`node -e …`, `pnpm exec git push`).
- Le relecteur peut écrire tout fichier `*-relecture*.md`, donc aussi réécrire les rapports des tours précédents sur lesquels le coordinateur compare les constats. Le brief lui donne le nom exact de son fichier.
- Le relecteur et le recetteur lancent le script de test du repo, que l'implémenteur a pu modifier : par ce script, n'importe quelle commande leur reste accessible, `git push` compris (Q-025).
- Un rôle qui écrit dans le worktree pourrait modifier ce que liront les rôles lancés après lui : les réglages de Claude Code du projet (`.claude/`), `AGENTS.md` ou les profils de rôle. Les profils qui écrivent interdisent donc `Edit(.claude/**)`, et l'implémenteur interdit aussi `AGENTS.md`, `docs/process/` et `docs/plans/`. Les voies `node -e` et script de test restent ouvertes : seul un sandbox système les fermera (risque R-03 de la roadmap).
- Le durcissement des profils ne vient pas d'un retour du mainteneur : les formes `rtk` répondent à une friction constatée par le coordinateur (Q-022) ; `Edit(.claude/**)` et `git -C` ont été ajoutés par précaution, à la relecture.
- La « file » se réduit aux cartes `in-review` : il n'y a pas de vue dédiée.
- Les boucles sont tenues par le coordinateur, donc par un agent : c'est lui qui relance les relecteurs et compare les constats d'un tour à l'autre.
- L'état d'avancement vit dans les commentaires de cartes et dans `docs/plans/`, pas dans une base.
