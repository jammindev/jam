# Relecture — cadrage-orchestration, tour 1

Relecteur seul (relecture d'un cadrage). Périmètre : toutes les modifications non commitées du worktree (`AGENTS.md`, `docs/decisions/README.md`, `docs/process/README.md`, profils `coordinateur`, `implementeur`, `redacteur`, `relecteur`, `04-ROADMAP.md`, `GLOSSARY.md`, `OPEN-QUESTIONS.md`, `RETOURS.md`) et les deux fichiers nouveaux `docs/decisions/0013-orchestration-deux-niveaux.md` et `docs/process/roles/orchestrateur-tache.md`. Référence : le brief du rédacteur (RET-008, RET-009 et les huit points à trancher).

## Fidélité au brief

- **RET-008** : remarque, décision et analyse fidèles (pas de worktree pour le coordinateur, 88 fichiers de retard, `git pull` après chaque merge, lancement `JAM_ROLE=coordinateur claude`).
- **RET-009** : les quatre points de la remarque et l'analyse sont fidèles. Les huit points sont présentés comme **propositions du coordinateur, à trancher au feu vert** (`RETOURS.md:106`) et l'ADR 0013 reste « proposée ». Les docs de process, les profils, `AGENTS.md` et le glossaire décrivent l'état cible comme des règles : c'est la convention du repo pour un cadrage non commité (déjà suivie pour l'ADR 0012), pas un constat.
- Choix d'une **nouvelle ADR** plutôt qu'un amendement de l'ADR 0012 : justifié dans son contexte (`0013-orchestration-deux-niveaux.md:17`). Recevable.
- Deux points où le rédacteur va au-delà du brief sans le dire comme proposition : la généralisation de la transition (constat 3) et le feu vert merge des cadrages (suggestion 4).

## Constats

### Bloquant

Aucun.

### À corriger

1. **Un feu vert transmis vaut-il « accord explicite du mainteneur » ? Les docs ne le disent pas, sur la règle la plus sensible (règle 6).**
   - Fichiers : `docs/decisions/0013-orchestration-deux-niveaux.md:34` et `:42` ; `docs/process/roles/orchestrateur-tache.md:7` et `:25` ; `docs/process/roles/coordinateur.md:9` et `:25` ; `docs/process/README.md:95`.
   - Problème : l'orchestrateur de tâche committe et pousse « avec l'accord explicite du mainteneur » (AGENTS.md, règle 6), et le coordinateur merge sous la même condition. Or un feu vert donné à un niveau est transmis à l'autre par `orca terminal send`. Le texte arrive dans la session comme s'il avait été tapé par le mainteneur : la session qui agit ne peut pas distinguer un message du mainteneur d'un message d'un autre agent. Telle qu'écrite, la règle laisse chaque agent décider seul si un message relayé suffit pour committer, pousser ou merger.
   - Correction attendue : trancher explicitement, comme proposition dans RET-009 et dans l'ADR 0013 (le mainteneur choisira), par exemple : (a) un feu vert relayé vaut accord, à condition que le message dise d'où il vient (« feu vert merge donné par le mainteneur au coordinateur, à HH:MM ») ; ou (b) l'accord explicite de la règle 6 se donne toujours dans la session qui agit, le relais ne servant qu'à informer. Ajouter la limite aux conséquences (−) de l'ADR 0013 : l'expéditeur d'un message relayé n'est pas authentifié.

2. **Le message court renvoie à un chemin que le coordinateur ne peut pas lire.**
   - Fichiers : `docs/process/README.md:94` (exemple `docs/plans/12-file-a-toi.md`) ; `docs/process/roles/orchestrateur-tache.md:24` ; `docs/decisions/0013-orchestration-deux-niveaux.md:33`.
   - Problème : le coordinateur vit sur le worktree principal (RET-008). Un chemin relatif au repo s'y résout dans le checkout de `main`, où le plan ou le rapport de la tâche n'existe pas encore (il est non commité dans le worktree de la tâche), ou existe dans une version périmée. Le coordinateur lirait le mauvais fichier, ou rien.
   - Correction attendue : préciser que le fichier est désigné dans le worktree de la tâche (chemin du worktree, tel que le donne `orca worktree ps`, suivi du chemin relatif), et corriger l'exemple en conséquence, sans chemin propre à une machine dans la doc (par exemple `<chemin du worktree>/docs/plans/12-file-a-toi.md`).

3. **La transition est généralisée au-delà du brief et contredit la règle « une tâche = un orchestrateur de tâche ».**
   - Fichiers : `docs/decisions/0013-orchestration-deux-niveaux.md:38` ; `docs/process/README.md:14` ; `docs/process/roles/coordinateur.md:28` (à comparer avec `:22` et `:9`) ; `docs/process/roles/redacteur.md:3`.
   - Problème : le brief (point 8) ne prévoit qu'une exception, ce cadrage-ci, lancé avant l'adoption du modèle. Les docs en font une règle permanente : « pour une tâche que le coordinateur conduit lui-même, il en tient le rôle, commit compris ». Le coordinateur peut donc toujours revenir au modèle d'avant, celui qui a saturé son contexte, ce qui contredit `coordinateur.md:22` (« une tâche = une issue = un worktree = un orchestrateur de tâche »). En plus, dans le même profil, les permissions (`coordinateur.md:9`) ne mentionnent plus ni commit ni push, alors que la règle de transition (`:28`) les lui donne. Enfin, la mention « C'est le cas du cadrage `cadrage-orchestration` » dans le process et dans le profil sera périmée dès le merge.
   - Correction attendue : limiter la transition au cadrage `cadrage-orchestration` (conduit jusqu'au merge par le coordinateur, commit et PR compris, depuis le worktree principal, par exemple avec `git -C <worktree>`), et la décrire dans l'ADR 0013 seulement, qui garde l'historique. Dans le process et dans les profils, supprimer la règle générale ou la garder explicitement comme proposition à trancher dans RET-009. Si elle est gardée, ajouter le commit et le push aux permissions de `coordinateur.md:9` pour ce cas.

4. **Deux références au coordinateur n'ont pas suivi le transfert du commit et des boucles.**
   - `docs/specs/RETOURS.md:5` : « avant le commit du coordinateur » → « avant le commit de l'orchestrateur de tâche ».
   - `docs/specs/OPEN-QUESTIONS.md:32` (Q-028) : « Dans Orca, c'est le coordinateur qui en juge » → « c'est l'orchestrateur de tâche qui en juge », en cohérence avec `docs/process/README.md:126` et `:160`.

5. **Le contenu du brief d'un orchestrateur de tâche diffère entre le process et le profil.**
   - Fichiers : `docs/process/README.md:74` et `docs/process/roles/orchestrateur-tache.md:18`.
   - Problème : le process y met « le nombre d'agents qu'il peut lancer à la fois », le profil non. Or la règle `orchestrateur-tache.md:26` en dépend (« ne lance pas plus d'agents que le coordinateur ne l'a fixé dans son brief »).
   - Correction attendue : ajouter ce nombre à la liste de `orchestrateur-tache.md:18`.

### Suggestions

1. **ADR 0008, « équipe d'agents permanents qui dialoguent »** (`docs/decisions/0008-boucle-exterieure-pipeline.md:22`, acceptée) : l'idée a été écartée pour son coût, sa dérive et son bruit. Deux sessions conversationnelles longues qui s'envoient des messages s'en rapprochent. Il n'y a pas de contradiction, puisque c'est propre à Orca et que jam le fera en code, mais l'ADR 0013 gagnerait à dire en une phrase pourquoi elle ne rouvre pas ce choix : hiérarchie stricte, messages d'une ligne, transitoire.
2. **« Agent actif »** (`docs/specs/GLOSSARY.md:19`, `docs/process/README.md:147`) : la définition ne dit pas si un orchestrateur bloqué dans `orca terminal wait` (30 minutes) est actif. Il ne consomme pas de quota, mais il est en plein tour. Le compte change selon la réponse : deux relecteurs, un orchestrateur et un coordinateur font 4 ou 2. Préciser, par exemple, « un agent qui attend la fin d'un autre agent ne compte pas ».
3. **Invites de permission de l'orchestrateur de tâche** (`docs/process/roles/orchestrateur-tache.md:14`) : elles s'affichent dans son terminal. Un mainteneur qui ne parle qu'au coordinateur ne les voit pas, et l'orchestrateur, bloqué sur l'invite, ne peut ni mettre à jour sa carte ni prévenir le coordinateur. Dans ce cas, la ligne « Bloqué (refus de permission) → message au coordinateur : oui » du signalement (`docs/process/README.md:138`) ne peut pas s'appliquer. À ajouter aux conséquences (−) de l'ADR 0013, ou à une question ouverte.
4. **Feu vert merge pour un cadrage** (`docs/process/README.md:31`) : jusqu'ici, un cadrage n'avait qu'un feu vert, celui de cadrage. Le texte ajoute un feu vert merge de la PR de cadrage. C'est un tranchage du rédacteur, cohérent avec « un seul acteur merge », mais absent du brief. Le présenter comme tel dans RET-009 (point 4 ou 8), pour que le mainteneur le valide sciemment.
5. **« comme le coordinateur »** (`docs/process/roles/orchestrateur-tache.md:8`) : l'orchestrateur de tâche n'a pas l'exception « installation d'un hook relu » (ADR 0013, table ; Q-036). Écrire « comme le coordinateur, sans l'exception d'installation d'un hook », pour que le profil ne paraisse pas plus large qu'il n'est.
6. **Retour donné directement à l'orchestrateur de tâche** : RET-009 permet au mainteneur de discuter d'une tâche dans son worktree, mais le process (`docs/process/README.md:28`) ne décrit que le chemin d'un retour via le coordinateur. Dire en une ligne qui reformule et consigne un retour reçu dans le worktree, et comment il remonte au coordinateur.
7. **Q-033** (`docs/specs/OPEN-QUESTIONS.md:37`) : le porteur « Coordinateur, puis rédacteur » devient « Orchestrateur de tâche, puis rédacteur », puisque c'est lui qui lancera l'implémenteur.
8. **R-03** (`docs/specs/04-ROADMAP.md:60`) : la mitigation cite la garde du coordinateur (ADR 0012). Ajouter que l'orchestrateur de tâche n'est pas encore gardé (Q-036).

## Autres vérifications, sans constat

- Glossaire : « Orchestrateur de tâche », « Agent actif », « Lead », « Coordinateur » et « Rôle » sont cohérents entre eux et avec ADR 0008 et FR-034. Le refus du terme « lead » est justifié.
- ADR 0009 (acceptée) : l'exception est déclarée sur le modèle de l'ADR 0012, et la mention à reporter à l'acceptation est prévue (`0013:52`).
- Correspondance avec jam : FR-024, FR-027, FR-029, FR-034 et FR-040 sont cités à bon escient. La tension entre agents et tâches est renvoyée à Q-038.
- Repo public : pas de secret, pas de chemin propre à une machine, pas de mention d'auteur IA.

RELECTURE : CORRECTIONS (5)
