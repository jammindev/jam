# Relecture — cadrage-orchestration, tour 4

Relecteur seul (relecture d'un cadrage). Contexte neuf : les rapports des tours précédents n'ont pas été lus.

**Périmètre relu** : toutes les modifications non commitées du worktree (`AGENTS.md`, `docs/decisions/README.md`, `docs/process/README.md`, profils `coordinateur`, `implementeur`, `redacteur`, `relecteur`, `docs/specs/04-ROADMAP.md`, `GLOSSARY.md`, `OPEN-QUESTIONS.md`, `RETOURS.md`) et les fichiers nouveaux `docs/decisions/0013-orchestration-deux-niveaux.md` et `docs/process/roles/orchestrateur-tache.md`.

**Références** : le brief du rédacteur, son complément 1 (qui prime), les deux décisions ajoutées depuis (le format du feu vert relayé vaut pour tout feu vert relayé ; un feu vert relayé ne vaut accord que pour l'action qu'il ouvre), `00-VISION.md`, `01-REQUIREMENTS.md` (FR-021 à FR-029, FR-034, FR-038, FR-040), `02-ARCHITECTURE.md`, `04-ROADMAP.md`, les ADR 0008, 0009 (acceptées) et 0012 (proposée), le glossaire et les autres profils de rôle.

## Fidélité aux retours et aux décisions

- **RET-008** (coordinateur sur `main`) : bien rendu dans RETOURS, le process (« Acteurs », « Lancement du coordinateur »), le profil du coordinateur (« Où »), AGENTS.md et l'ADR 0013. Les éléments de l'analyse (88 fichiers de retard, `git pull` après chaque merge, lancement `JAM_ROLE=coordinateur claude`) sont présents.
- **RET-009, huit propositions** : toutes rendues et notées comme validées (« ça me semble OK », 2026-10-09). L'ADR 0013 reste « proposée » et les retours « en application », comme demandé. Je n'ai pas trouvé de reste de formulation « à trancher » dans le process, les profils ou AGENTS.md.
- **Complément 1, point 3 (dans jam, c'est le code qui orchestre)** : correspondance rendue dans l'ADR 0013 (« Correspondance avec jam »), dans la table du process (lignes « Interlocuteur », « Orchestration d'une tâche », « État d'une tâche », « Feu vert relayé ») et dans le glossaire (« Lead », « Orchestrateur de tâche »). Cohérent avec l'ADR 0008 (pipeline codé dans le cœur, lead par worktree, coordinateur conversationnel après E0), avec FR-021, FR-027 et FR-034. Les exigences ne sont pas modifiées.
- **Complément 1, point 4 (avancer le coordinateur dans E0)** : Q-039, non tranchée, avec le rappel qu'une nouvelle ADR serait nécessaire. Conforme.
- **Feu vert relayé, option (a)** et limite d'authentification : présents dans les conséquences (−) de l'ADR 0013, dans le process et dans RET-009.
- **Décision « tout feu vert relayé »** : le format couvre cadrage, plan, recette et merge dans le process (« Format de tout feu vert relayé »), l'ADR 0013, RET-009 et les deux profils qui orchestrent.
- **Décision « accord pour l'action qu'il ouvre, et elle seule »** : rendue dans le process, l'ADR 0013, RET-009 et, par renvoi, dans les profils du coordinateur et de l'orchestrateur de tâche. Elle n'apparaît pas dans la règle 6 d'AGENTS.md (voir la suggestion 1).
- **Exception de ce cadrage** : décrite seulement dans l'ADR 0013 (et rappelée dans RET-009, qui consigne l'arbitrage), sans règle générale dans le process ni dans les profils. Conforme à l'arbitrage du constat 3.
- **Feu vert merge d'un cadrage** : présenté comme proposition du rédacteur dans RET-009, avec ses réserves dans le process et l'ADR 0013. Conforme à l'arbitrage de la suggestion 4.

## Cohérence avec les ADR, les exigences et le glossaire

- **ADR 0009 (acceptée)** : l'ADR 0013 trace deux exceptions (commit, push et PR par l'orchestrateur de tâche ; session interactive), sur le modèle de l'ADR 0012, et prévoit la mention dans le statut de l'ADR 0009 à l'acceptation. Pas de contournement.
- **ADR 0008 (acceptée)** : l'ADR 0013 répond explicitement au rejet d'une « équipe » d'agents qui dialoguent (hiérarchie stricte, messages d'une ligne, dispositif transitoire propre à Orca). Pas de contradiction.
- **ADR 0012 (proposée)** : « Précision de l'ADR 0012 » explicite le transfert du commit, du push et de la PR. La conséquence (−) « le commit n'est plus tenu par un seul acteur » est honnête.
- **FR-029 / critère d'E0** : la tension avec le plafond d'environ 3 agents actifs est relevée dans Q-038. Correct.
- **Glossaire** : « Orchestrateur de tâche » et « Agent actif » ajoutés, « Lead », « Coordinateur » et « Rôle » mis à jour. Vocabulaire employé de façon cohérente dans tous les fichiers relus.
- **Profils** : implémenteur, rédacteur et relecteur renvoient désormais à l'orchestrateur de tâche là où il prend le relais. Planificateur et recetteur ne mentionnent pas le coordinateur : rien à mettre à jour.
- **Repo public** : pas de secret, de donnée personnelle ni de chemin propre à une machine (les chemins sont des gabarits `<chemin du worktree>`).

## Constats

### Bloquant

Aucun.

### À corriger

Aucun.

### Suggestions

1. **`AGENTS.md:40`, règle 6** : « Après un feu vert, l'orchestrateur de tâche committe… » est générique, alors que la décision limite l'accord d'un feu vert relayé à l'action qu'il ouvre (un feu vert plan n'ouvre ni commit ni PR). La règle 6 est la règle de l'accord explicite, que tout agent lit en premier. Correction proposée : « Après le feu vert correspondant (recette, ou cadrage), l'orchestrateur de tâche committe… » et, à la fin de la phrase sur le feu vert relayé, « … et seulement pour l'action que ce feu vert ouvre (voir `docs/process/README.md`, « Format de tout feu vert relayé ») ».

2. **`docs/specs/RETOURS.md:118`, RET-009, « Compléments du mainteneur », feu vert relayé** : la parenthèse « format étendu à tout feu vert au tour 2 de relecture, portée de l'accord précisée au tour 3 » attribue ces décisions à des tours de relecture, sous un intitulé « Compléments du mainteneur ». Un relecteur ne décide pas : il signale. Correction proposée, sur le modèle du point 8 (« Précisé à l'arbitrage qui a suivi le tour 1 ») : « format étendu à tout feu vert à l'arbitrage qui a suivi le tour 2, portée de l'accord précisée à l'arbitrage qui a suivi le tour 3 », en nommant qui a arbitré (mainteneur ou coordinateur).

3. **`docs/process/README.md:28` (« Retour ») et « Remontée vers le coordinateur »** : le process ne dit comment le coordinateur transmet un retour ou un arbitrage qu'au lancement (« dans le brief de l'orchestrateur de tâche »). Ce cadrage a montré le cas d'un complément en cours de route. L'ADR 0013 limite les échanges, hors brief de lancement, à des messages d'une ligne. Correction proposée : une phrase dans « Remontée vers le coordinateur » (ou une section symétrique) : un complément de brief est écrit dans un fichier des dossiers temporaires du coordinateur, et transmis par un message d'une ligne qui donne son chemin.

4. **`docs/process/README.md:31`, liste des endroits à mettre à jour au feu vert de cadrage** : si la proposition « feu vert merge d'un cadrage » est refusée, la « Fin » du profil de l'orchestrateur de tâche (`docs/process/roles/orchestrateur-tache.md:30`, « la carte indique « ⏸ feu vert merge » ») ne vaudrait plus pour un cadrage, et elle n'est pas dans la liste. « Si la proposition est refusée, il retire la phrase » est aussi ambigu (une seule phrase, alors que la réserve figure à trois endroits). Correction proposée : ajouter le profil de l'orchestrateur de tâche (« Fin ») à la liste, et écrire « il retire la proposition aux mêmes endroits ».

5. **`docs/process/roles/orchestrateur-tache.md:30`, « Fin »** : la session ne s'arrête pas à « ⏸ feu vert merge » : si le mainteneur donne le feu vert merge dans le worktree, l'orchestrateur de tâche doit encore le remonter au coordinateur. Correction proposée : « … et le coordinateur est prévenu. Il reste ouvert pour remonter un feu vert merge donné dans le worktree ; après le merge, le coordinateur ferme la session et nettoie le worktree. »

RELECTURE : OK
