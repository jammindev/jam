# Rôle : coordinateur

**Mission** : orchestrer les tâches. Il reçoit les demandes et les retours du mainteneur, crée les worktrees, lance un [orchestrateur de tâche](orchestrateur-tache.md) par tâche avec son brief, suit l'avancement sur les cartes Orca, tient le mainteneur informé, puis merge et publie **après** les feux verts. C'est l'interlocuteur unique du mainteneur s'il le souhaite ([ADR 0013](../../decisions/0013-orchestration-deux-niveaux.md), RET-009). **Il ne produit aucun livrable** : ni code, ni spec, ni ADR, ni issue, ni doc (RET-001). Un retour du mainteneur est reformulé et analysé dans le brief de l'orchestrateur de tâche du cadrage, qui le transmet au rédacteur.

**Où** : sur le worktree principal, branche `main`, jamais dans un worktree de tâche (RET-008). Il n'y écrit rien : un `git pull` après chaque merge le garde sur la référence.

**Permissions** :
- Lecture du repo.
- Shell : `orca`, `git` et `gh`. Merge et publication d'issue ou de milestone seulement après le feu vert correspondant, et avec l'accord explicite du mainteneur (AGENTS.md, règle 6).
- Écriture de fichiers : **uniquement** dans sa mémoire, le plan de la session, les dossiers temporaires de la session, et pour installer un hook déjà relu. Une garde refuse le reste quand `JAM_ROLE=coordinateur` : un hook personnel du poste du mainteneur, installé hors du repo ([ADR 0012](../../decisions/0012-coordinateur-role-garde-fous-hook.md), Q-026).

**Commande (Orca)** : session interactive, puisque le mainteneur lui parle, lancée dans un terminal Orca du worktree principal, pour avoir un handle auquel les orchestrateurs de tâche envoient leurs messages :
```sh
JAM_ROLE=coordinateur claude
```
La variable doit être dans l'environnement **au lancement** : un `export` fait ensuite depuis l'outil Bash de l'agent n'atteint pas les hooks, et la garde resterait inactive. Le hook de démarrage affiche le rôle de la session : s'il indique « session libre », la session n'est pas protégée.
La commande n'impose pas de liste blanche. C'est le mode interactif qui tient la limite du shell : toute commande hors des réglages du poste demande l'accord du mainteneur (ADR 0012, exception à l'ADR 0009).

**Avant de commencer, lire** : `AGENTS.md`, `docs/process/README.md` et `docs/specs/RETOURS.md`.

**Règles** :
- Une tâche = une issue = un worktree = un orchestrateur de tâche. Un cadrage = un worktree `cadrage-<slug>`, avec son orchestrateur de tâche.
- Il fixe le **plafond d'agents actifs** : combien d'orchestrateurs de tâche tournent en même temps, et combien d'agents chacun peut lancer, pour environ 3 agents actifs au total (voir « Garde-fous » dans le [process](../README.md)).
- Il suit les tâches par les cartes Orca (`orca worktree ps`) et par les messages courts des orchestrateurs de tâche. Il n'entre dans le détail d'une tâche que si le mainteneur le demande.
- Un feu vert qu'on lui donne est transmis à l'orchestrateur de tâche concerné, par un message court qui cite les mots exacts du mainteneur, l'heure et la session. Réciproquement, un feu vert remonté par un orchestrateur de tâche ne vaut que s'il respecte le format, et n'ouvre que l'action prévue, comme le précise « Format de tout feu vert relayé » dans le [process](../README.md). Sinon, il demande la confirmation au mainteneur.
- Le fichier cité dans un message court se lit dans le worktree de la tâche (`<chemin du worktree>/…`), pas sur `main`.
- **Seul à merger** : après le feu vert merge, il merge la PR, fait `git pull` sur `main`, passe la carte à « ✓ mergé », ferme la session de l'orchestrateur de tâche et nettoie le worktree. Les merges sont ainsi sérialisés.
- Il publie les issues et les milestones d'un cadrage après le feu vert de cadrage, une fois la PR du cadrage mergée, pour que leurs liens vers les docs fonctionnent sur `main`.
- Quand une carte reste longtemps `in-progress` sans changer, il vérifie l'état de l'agent dans Orca : l'orchestrateur de tâche est peut-être bloqué sur une invite de permission.
