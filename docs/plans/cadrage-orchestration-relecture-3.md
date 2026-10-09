# Relecture — cadrage-orchestration, tour 3

Relecteur seul, relecture d'un cadrage. Périmètre : toutes les modifications non commitées du worktree (`AGENTS.md`, `docs/decisions/README.md`, `docs/process/README.md`, profils `coordinateur`, `implementeur`, `redacteur`, `relecteur`, `04-ROADMAP.md`, `GLOSSARY.md`, `OPEN-QUESTIONS.md`, `RETOURS.md`) et les nouveaux fichiers `docs/decisions/0013-orchestration-deux-niveaux.md` et `docs/process/roles/orchestrateur-tache.md`.

Références : brief du rédacteur, puis son complément 1 (qui prime), plus la décision ajoutée depuis (le format du feu vert relayé vaut pour tout feu vert relayé). Lus aussi : vision, exigences (FR-021, FR-024, FR-027, FR-029, FR-034, FR-038, FR-040), ADR 0008, 0009 et 0012, glossaire, process et tous les profils de rôle.

Conformément au profil, les rapports `cadrage-orchestration-relecture-1.md` et `-2.md`, non commités, n'ont pas été lus. Ils ne sont donc pas couverts par cette relecture, repo public compris.

## Fidélité aux retours et décisions du mainteneur

Rendus fidèlement :
- RET-008 (coordinateur sur `main`, `git pull` après chaque merge, lancement `JAM_ROLE=coordinateur claude`) ;
- les huit propositions de RET-009, notées comme validées (« ça me semble OK ») ; les formulations « à trancher » ont disparu du process, des profils et d'`AGENTS.md` ; l'ADR 0013 reste « proposée » et les retours restent « en application » ;
- la mise en place immédiate dans Orca ;
- « dans jam, c'est le code qui orchestre » : la correspondance (cockpit + coordinateur au niveau projet, lead au niveau tâche, remontée structurelle par l'état du cœur) figure dans l'ADR 0013, dans la table de correspondance du process et dans le glossaire (« Lead », « Orchestrateur de tâche ») ;
- Q-039, notée comme ouverte et non tranchée ;
- le feu vert relayé (mots exacts, heure, session), étendu à tout feu vert relayé ; la limite « expéditeur non authentifié » et sa forme dans jam figurent dans les conséquences (−) de l'ADR 0013 ;
- l'exception de ce cadrage, décrite dans l'ADR 0013 seulement, sans règle générale dans le process ni dans les profils ;
- le feu vert merge d'un cadrage, présenté comme une proposition à valider au feu vert de cadrage.

Cohérence avec les ADR acceptées : l'ADR 0008 tient (le pipeline reste codé dans le cœur, le lead garde sa place, le coordinateur conversationnel reste après E0). L'écart avec l'ADR 0009 est tracé comme deux exceptions, sur le modèle de l'ADR 0012. Aucune exigence n'est modifiée, ce qui est cohérent avec FR-021, FR-027 et FR-034. La tension avec FR-029 est notée dans Q-038.

## Constats

### Bloquant

Aucun.

### À corriger

1. **Le feu vert relayé « vaut accord » pour plus que l'action qu'il ouvre.** Depuis que le format s'applique à tout feu vert (cadrage, plan, recette, merge), la phrase qui suit le rend trompeur. Prise à la lettre, elle dit qu'un feu vert **plan** relayé vaut accord explicite pour le commit, le push, la PR et le merge, et qu'un feu vert **recette** remonté au coordinateur vaut accord pour le merge. Le reste du process (la table de correspondance, la règle « seul à merger, après le feu vert merge ») empêche l'erreur, mais la règle telle qu'elle est écrite dit autre chose.
   - `docs/process/README.md:119` : « Il vaut alors feu vert, et accord explicite au sens de la règle 6 d'`AGENTS.md` pour le commit, le push, la PR et le merge. »
   - `docs/process/roles/orchestrateur-tache.md:26` : « il vaut alors aussi accord explicite pour le commit, le push et la PR. »
   - `docs/process/roles/coordinateur.md:25` : « il vaut alors aussi accord explicite pour le merge ou la publication. »
   - `docs/decisions/0013-orchestration-deux-niveaux.md:39`, même phrase que dans le process.
   - `docs/specs/RETOURS.md:118`, même phrase, dans les compléments de RET-009.

   **Correction attendue** : limiter l'accord à l'action que ce feu vert ouvre. Par exemple : « Il vaut alors feu vert, et accord explicite au sens de la règle 6 pour l'action que ce feu vert ouvre : commit, push et PR après le feu vert recette ou le feu vert de cadrage ; merge après le feu vert merge ; publication des issues et des milestones après le feu vert de cadrage. Un feu vert plan n'ouvre aucune de ces actions. » Il faut aligner les cinq endroits ; dans les profils, on peut renvoyer à la phrase du process.

### Suggestions

1. **Le coordinateur doit tourner dans un terminal Orca.** Le brief d'un orchestrateur de tâche contient « le handle du terminal du coordinateur » (`docs/process/README.md:75`, `orchestrateur-tache.md:18`), et les messages courts passent par `orca terminal send`. Or le lancement du coordinateur dit seulement « depuis le worktree principal » (`docs/process/README.md:57`, `coordinateur.md:12`). S'il est lancé dans un terminal ordinaire, il n'a pas de handle et ne peut pas recevoir de messages. Préciser « dans un terminal Orca du worktree principal ».

2. **Ce que le feu vert merge d'un cadrage changerait, s'il est accepté.** Le process (`README.md:31`) prévoit de retirer la réserve dans le process seulement. Il faudrait la retirer aussi dans `0013-orchestration-deux-niveaux.md:42` et dans `RETOURS.md:120`, et mettre à jour le glossaire :
   - « Cadrage » (`GLOSSARY.md:20`) : « rédacteur → relecteur → feu vert de cadrage » deviendrait « … → feu vert de cadrage → feu vert merge » ;
   - « Feu vert » (`GLOSSARY.md:26`) ne cite que le feu vert de cadrage pour un cadrage.

   La consigne de retrait (`README.md:31`) pourrait lister ces fichiers.

3. **« Les échanges se limitent à des messages d'une ligne »** (`0013-orchestration-deux-niveaux.md:21`). Le brief de lancement d'un orchestrateur de tâche n'est pas une ligne : il contient, pour un cadrage, les retours et leur analyse. Écrire « hors le brief de lancement » rendrait l'argument exact face à l'ADR 0008.

4. **« Chacun après son feu vert »** pour le commit, le push et la PR (`0013-orchestration-deux-niveaux.md:33`, `RETOURS.md:110`). Cette formule laisse croire à trois feux verts distincts. La table de correspondance (`README.md:47-48`) place les trois actions après le seul feu vert recette, et le process (`README.md:31`) les place après le feu vert de cadrage pour un cadrage. Dans l'ADR, « après le feu vert recette (ou de cadrage) » serait plus juste. Dans RETOURS, la formule rapporte la proposition du coordinateur et peut rester telle quelle.

5. **Traçabilité de RET-009, point 8** (`RETOURS.md:114`). Le point est rangé sous « validées par le mainteneur (« ça me semble OK ») », mais deux précisions viennent de l'arbitrage qui a suivi le tour 1 : « jusqu'au merge » et « décrite dans l'ADR 0013 seulement ». Une mention « (précisé à l'arbitrage du tour 1) » distinguerait ce que le mainteneur a validé d'abord de ce qui a été arbitré ensuite.

RELECTURE : CORRECTIONS (1)
