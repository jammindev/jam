# ADR 0013 : orchestration à deux niveaux, coordinateur sur `main` et orchestrateur de tâche par worktree

- **Statut** : acceptée. Précisée par l'[ADR 0015](0015-remontee-carte-seule-coordinateur-flottant.md) : l'orchestrateur de tâche ne remonte plus que par sa carte Orca, sans message court au coordinateur, et le coordinateur tourne dans le terminal flottant d'Orca, lancé depuis le worktree principal.
- **Date** : 2026-10-09
- **Tranche** : RET-008, RET-009. Précise l'[ADR 0012](0012-coordinateur-role-garde-fous-hook.md), complète l'[ADR 0009](0009-permissions-par-role.md)

## Contexte

En attendant que jam déroule son pipeline, un seul coordinateur conduit tout dans Orca : il lance chaque rôle de chaque tâche, lit chaque sortie, tient chaque boucle de relecture, committe et merge (ADR 0012). Trois limites sont apparues :

- **contexte saturé** : dans la nuit du 8 au 9 octobre, le contexte du coordinateur a saturé. Il porte le détail de toutes les tâches ;
- **référence périmée** : son worktree était sur une vieille branche, 88 fichiers en retard sur `main`. Au démarrage, il chargeait un `AGENTS.md` et un process périmés (RET-008). Or il n'écrit aucun fichier du repo (RET-001) : un worktree ne lui sert à rien ;
- **un seul fil de discussion** : pour parler d'une tâche en détail, le mainteneur doit passer par le coordinateur, qui mélange alors toutes les tâches.

Le mainteneur propose deux niveaux (RET-009) : un orchestrateur sur `main`, son seul interlocuteur s'il le souhaite, et un orchestrateur dans chaque worktree, à qui il peut parler d'une tâche en détail.

Le mainteneur veut ce modèle appliqué dès maintenant dans Orca, et qu'il devienne le cœur de jam. Il a validé les huit propositions du coordinateur le 2026-10-09 (RET-009).

Cette décision est distincte de celle de l'ADR 0012, qui fait du coordinateur un rôle protégé par une garde. Elle fait l'objet d'une ADR à part pour pouvoir être acceptée ou refusée sans rouvrir la garde, déjà relue et installée.

Elle ne rouvre pas le choix de l'ADR 0008, qui écarte une « équipe » d'agents permanents qui dialoguent entre eux : la hiérarchie est stricte (le coordinateur lance, l'orchestrateur de tâche rend compte), hors le brief de lancement, les échanges se limitent à des messages d'une ligne, et le dispositif est transitoire, propre à Orca. Dans jam, c'est le code qui orchestre.

## Décision

### Deux niveaux

| | Coordinateur | Orchestrateur de tâche |
|---|---|---|
| Où | Worktree principal, sur `main` | Le worktree de sa tâche (`<numéro>-<slug>` ou `cadrage-<slug>`) |
| Combien | Un | Un par tâche en cours |
| Lancement | `JAM_ROLE=coordinateur claude`, par le mainteneur, dans un terminal Orca du worktree principal | Par le coordinateur, dans un terminal Orca du worktree, avec `JAM_ROLE=orchestrateur-tache` et un brief |
| Orchestre | Les tâches : création des worktrees, lancement des orchestrateurs de tâche, plafond d'agents actifs | Les rôles de sa tâche : lancement, boucles, garde-fous, comparaison des rapports de relecture |
| Git et GitHub | Merge, après le feu vert merge. Publication des issues et des milestones. `git pull` sur `main` après chaque merge | Commit, push de sa branche et ouverture de la PR, après le feu vert recette (ou de cadrage) |
| Livrables | Aucun (RET-001) | Aucun (RET-001) |

- **Le coordinateur vit sur `main`** et ne change pas de branche. Comme il n'y écrit rien, `git pull` après chaque merge suffit à le garder sur la référence.
- **Remontée d'information** : l'orchestrateur de tâche tient l'état de sa tâche dans le statut et le commentaire de sa carte Orca (table « Signalement d'attente » du [process](../process/README.md)). Le coordinateur lit ces cartes. Pour un événement qui attend le mainteneur (feu vert, blocage), l'orchestrateur de tâche prévient aussi le coordinateur par un message court : la tâche, l'événement et le fichier à lire (plan, rapport, recette). Le fichier est désigné dans le worktree de la tâche (chemin du worktree, puis chemin relatif) : sur `main`, il n'existe pas encore ou il est périmé. Pas de long texte, pour que le contexte du coordinateur reste léger.
- **Feux verts** : le mainteneur les donne au coordinateur ou à l'orchestrateur de tâche. Un feu vert donné à un niveau est transmis à l'autre : remonté au coordinateur s'il est donné dans le worktree, transmis à l'orchestrateur de tâche s'il est donné au coordinateur.
- **Feu vert relayé** (tranché par le mainteneur, 2026-10-09) : tout feu vert relayé d'un niveau à l'autre (cadrage, plan, recette, merge) cite les mots exacts du mainteneur, l'heure et la session où il l'a donné. Il vaut alors feu vert, et accord explicite au sens de la règle 6 d'`AGENTS.md` pour l'action que ce feu vert ouvre, et elle seule : commit, push et PR après le feu vert recette ou le feu vert de cadrage ; merge après le feu vert merge ; publication des issues et des milestones après le feu vert de cadrage. Un feu vert plan n'ouvre aucune de ces actions. Sinon, il ne vaut qu'information, et la session qui doit agir demande la confirmation au mainteneur.
- **Un seul acteur merge** : le coordinateur. Les merges sont donc sérialisés et `main` est mis à jour au même endroit. Il publie aussi les issues et les milestones, qui touchent tout le projet.
- **Plafond d'agents actifs** : le coordinateur décide combien d'orchestrateurs de tâche tournent en même temps, pour environ **3 agents actifs** au total, tous niveaux confondus. Un agent actif est un agent en train de travailler ; un agent qui attend une réponse, un feu vert ou la fin d'un autre agent ne compte pas. Origine : la limite d'usage a été atteinte avec 5 agents actifs dans la nuit du 8 au 9 octobre.
- **Cadrages** : même schéma, avec un orchestrateur de tâche dans `cadrage-<slug>` (le terme couvre donc aussi un cadrage). La PR d'un cadrage passe par un feu vert merge, comme toute PR (décision du mainteneur, RET-009). Le coordinateur publie les issues et les milestones du cadrage une fois sa PR mergée.
- **Exception unique, ce cadrage** : `cadrage-orchestration` a été lancé avant l'adoption du modèle. Il est conduit par le coordinateur jusqu'au merge, commit et PR compris, depuis le worktree principal (par exemple avec `git -C <worktree>`). Cette exception ne vaut pour aucune autre tâche : après lui, chaque tâche et chaque cadrage a son orchestrateur de tâche.

### Exceptions et profils

- **Deux exceptions à l'ADR 0009**, sur le modèle de celles du coordinateur (ADR 0012) :
  - l'orchestrateur de tâche committe, pousse sa branche et ouvre la PR, après le feu vert correspondant et avec l'accord explicite du mainteneur (AGENTS.md, règle 6). Il ne merge pas et ne publie ni issue ni milestone ;
  - il tourne en **session interactive**, et non en refus sans invite : le mainteneur peut lui parler de la tâche, ce qu'une session `dontAsk` ne permet pas. Toute commande hors des réglages du poste lui demande donc son accord. La justification de l'ADR 0012 (« le mainteneur est présent ») ne vaut qu'en partie : le mainteneur n'est en général pas devant ce terminal, et une invite peut y rester sans réponse (voir la conséquence (−) sur les invites de permission).
- **Précision de l'ADR 0012** : le coordinateur garde le merge et la publication sur GitHub. Le commit, le push et l'ouverture de la PR d'une tâche passent à son orchestrateur de tâche.
- L'orchestrateur de tâche est **un rôle**, avec son profil dans [`roles/orchestrateur-tache.md`](../process/roles/orchestrateur-tache.md). Il a les mêmes interdits d'écriture que le coordinateur : il ne produit aucun livrable.
- **Profil hors de la table de l'ADR 0009**, tracé ici :

| Rôle | Fichiers | Shell | Réseau / Git distant |
|---|---|---|---|
| Orchestrateur de tâche | Lecture ; écriture limitée à sa mémoire, au plan de la session et aux dossiers temporaires | `orca`, `git`, `gh`. Accord du mainteneur pour le commit, le push et l'ouverture de la PR, et pour toute commande hors des réglages du poste | Lecture : oui. Push et PR : après feu vert. Ni merge, ni publication d'issue ou de milestone |

- **Garde** : la garde du poste ne reconnaît aujourd'hui que `JAM_ROLE=coordinateur`. Son extension à `orchestrateur-tache` est un travail hors repo, suivi dans [Q-036](../specs/OPEN-QUESTIONS.md). D'ici là, les interdits de l'orchestrateur de tâche ne tiennent qu'à son profil et à son brief.
- À l'acceptation de cette ADR, le statut de l'ADR 0012 mentionne cette précision, et celui de l'ADR 0009 ce complément.

### Correspondance avec jam

Choix explicite du mainteneur : **dans jam, c'est le code qui orchestre**. L'[ADR 0008](0008-boucle-exterieure-pipeline.md) tient : le pipeline d'une tâche est codé dans le cœur, qui enchaîne les étapes et tient l'état. Les deux niveaux existent dans jam comme **deux niveaux d'interlocuteurs**, pas comme deux agents qui orchestrent :

- **niveau projet** : le cockpit (tableau des tâches, file « À toi ») et la session conversationnelle de `main`, le coordinateur. L'ADR 0008 place ce coordinateur après E0 ; l'avancer dans E0 est une question ouverte ([Q-039](../specs/OPEN-QUESTIONS.md)) ;
- **niveau tâche** : le lead du worktree (FR-034), à qui le mainteneur parle de sa tâche.

La remontée d'information devient structurelle : les deux niveaux lisent le même état du cœur (FR-027). Dans Orca, faute de cœur, l'orchestrateur de tâche est un agent qui tient ce rôle à la main.

| Dans Orca | Dans jam |
|---|---|
| Coordinateur, sur `main` | Niveau projet : le cockpit, et la session conversationnelle de `main` (FR-040) |
| Orchestrateur de tâche : enchaînement des étapes | Le pipeline, codé dans le cœur (ADR 0008, FR-021) |
| Orchestrateur de tâche : discussion de la tâche | Niveau tâche : le lead du worktree (FR-034) |
| Carte Orca et message court au coordinateur | État de la tâche persisté par le cœur (FR-027), lu par les deux niveaux |
| Feu vert relayé par message | Feu vert donné dans le cockpit, enregistré par le cœur |
| Plafond d'environ 3 agents actifs | Plafond configurable de tâches en parallèle (FR-029) et budget par étape (FR-024) |

## Conséquences

- (+) Le contexte du coordinateur reste léger : il ne voit des tâches que les cartes et les messages courts.
- (+) Le coordinateur lit toujours la référence, sans risque de branche périmée.
- (+) Le mainteneur choisit son niveau de détail : un seul interlocuteur, ou la discussion d'une tâche dans son worktree.
- (+) On éprouve dans Orca les deux niveaux d'interlocuteurs que jam reprendra : la vue d'ensemble d'un côté, la discussion d'une tâche de l'autre.
- (−) Un agent de plus par tâche, qui consomme du quota. Le plafond d'agents actifs le compense, au prix d'un parallélisme réduit (Q-038).
- (−) Deux endroits où donner un feu vert : un oubli de transmission bloque la tâche ou laisse le coordinateur dans l'ignorance. La carte Orca reste la référence.
- (−) Le message de l'orchestrateur de tâche arrive dans la session du coordinateur, où le mainteneur peut être en train d'écrire (Q-037).
- (−) L'expéditeur d'un message relayé n'est pas authentifié : un texte envoyé par `orca terminal send` arrive dans la session comme s'il avait été tapé par le mainteneur. Les trois éléments exigés d'un feu vert relayé (mots exacts, heure, session) le rendent vérifiable par le mainteneur, pas infalsifiable. Dans jam, le feu vert sera une action du cockpit, enregistrée par le cœur.
- (−) Une invite de permission de l'orchestrateur de tâche s'affiche dans son terminal. Bloqué sur elle, il ne peut ni mettre à jour sa carte ni prévenir le coordinateur : seul l'état de l'agent dans Orca le montre.
- (−) Tant que la garde n'est pas étendue (Q-036), une session d'orchestrateur de tâche n'est pas protégée en code.
- (−) Le commit n'est plus tenu par un seul acteur, comme dans l'ADR 0012 : plusieurs orchestrateurs de tâche committent. Seul le merge reste à un acteur unique.
