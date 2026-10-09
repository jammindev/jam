# Relecture : cadrage-retours-essai, tour 3

Relecteur seul (docs, les deux axes). Objet : la rédaction non commitée du worktree (`git diff`, plus `docs/decisions/0015-remontee-carte-seule-coordinateur-flottant.md`), comparée au brief du rédacteur et à ses entrées (14 frictions de #7, commande du recetteur de #7, rapport de recette de #7).

## Vérifications faites

- **Message court supprimé** : il ne reste aucune mention d'un message de l'orchestrateur de tâche vers le coordinateur dans le process, les profils, le glossaire ni `AGENTS.md`. Les mentions restantes sont historiques ou voulues : ADR 0013 (acceptée, non retouchée), RET-009, et le contexte et la table de l'ADR 0015. Le handle du coordinateur a disparu du brief de l'orchestrateur de tâche (process et profil). `orca terminal send` ne sert plus qu'à lancer un rôle ou un orchestrateur, et au coordinateur pour écrire à un orchestrateur de tâche.
- **Carte seule et feux verts relayés** : c'est cohérent entre le process (« Remontée vers le coordinateur », « Format de tout feu vert relayé », « Signalement d'attente »), les deux profils, l'ADR 0015 et RET-013.
  - Un feu vert donné dans le worktree n'est cité sur la carte que s'il ouvre une action du coordinateur (merge, publication).
  - Un feu vert plan ou recette donné dans le worktree est consommé sur place par l'orchestrateur de tâche, et le coordinateur le voit au changement du segment d'état.
  - Le format (mots exacts, heure, session) et la règle « l'action que ce feu vert ouvre, et elle seule » sont repris sans changement, et la limite d'authentification est étendue aux commentaires de carte.
- **RET-012** : le terminal flottant et le `cd` vers le worktree principal, avec `--continue`, sont décrits de façon cohérente dans le process, le profil du coordinateur, l'ADR 0015, le glossaire et RET-012.
  - RET-008 tient bien : la session est lancée depuis le worktree principal.
  - Côté jam, la traduction passe par une précision de FR-016 et par le composant « Coordinateur » de `02-ARCHITECTURE.md`. L'exigence est vérifiable : la session tourne dans le worktree principal. Elle ne change pas l'étape (FR-040, E0.5), ce qui est cohérent avec Q-039 et l'ADR 0008. Le cas de plusieurs repos est renvoyé à Q-051.
- **Les 14 frictions** ont chacune un sort, justifié dans le rapport de rédaction, et je l'ai vérifié dans les docs :
  - 1 et 7 : commande du recetteur, Q-033 ;
  - 2 : process et profil du coordinateur ;
  - 3 : Q-036 ;
  - 4, 12 et 14 : ADR 0015 et RET-013 ;
  - 5 : profils de l'implémenteur et du planificateur ;
  - 6 : « Relecture » ;
  - 8 : « Lancement d'un rôle » ;
  - 9 : Q-050. L'affirmation est vérifiée dans le code : l'app passe `--db` au cœur, avec `app.getPath('userData')` dans `apps/desktop/src/main/index.ts:43`, donc `JAM_DATA_DIR` ne joue pas ;
  - 10 : clavier laissé au mainteneur, renvoi à Q-017, qui existe ;
  - 11 et 13 : profil de l'orchestrateur de tâche.
- **Commande du recetteur** :
  - elle a les formes `rtk` des commandes que RTK réécrit, interdit `Edit(.claude/**)`, commit, push et `gh`, et ne contient aucun chemin du poste ni nom de worktree en dur ;
  - `rm -rf` est en forme exacte ;
  - l'app s'arrête par l'arrêt de la tâche de fond, sans aucun `pkill`. `pgrep -fl <chemin du worktree>/` ne fait que vérifier, et le `/` final évite de viser un worktree dont le nom commence pareil. J'ai vérifié que le motif atteint bien les processus de l'app : le cœur est lancé avec un chemin absolu (`require.resolve`, dans `apps/desktop/src/main/core-process.ts:24`), et Electron vient du `node_modules` du worktree ;
  - elle permet de rejouer toutes les vérifications de `7-electron-install-neuve-recette.md` : 0 à 4 et 6 à 9, et la 5 notée « non reproduite », comme dans le rapport de #7.
- **Numérotation** : RET-012, RET-013, Q-050, Q-051 et ADR 0015. Aucune occurrence de RET-011, Q-040, Q-042 à Q-049 ni de l'ADR 0014 hors `docs/plans/`. Les ajouts sont en fin de table ou de section.
- **Statuts** : l'ADR 0015 est « proposée » (fichier et index). RET-012 et RET-013 sont « en application », un statut défini en tête de `RETOURS.md`. Le report de la précision dans le statut de l'ADR 0013 est prévu à l'acceptation.
- **Repo public** : aucun secret, aucune donnée personnelle hors citations du mainteneur, aucun chemin machine. Aucune mention d'auteur IA.

## Constats

### Bloquant

Aucun.

### À corriger

Aucun.

### Suggestions

- **S1, publication d'un cadrage après le nettoyage** : `docs/process/roles/coordinateur.md:30-31`.
  - Le point « Seul à merger » enchaîne merge, `git pull`, carte « ✓ mergé », fermeture de la session de l'orchestrateur de tâche et nettoyage du worktree. La publication des issues et des milestones vient au point suivant, « une fois la PR du cadrage mergée ».
  - Or le process (`docs/process/README.md:128-130`) prévoit qu'un `✓ feu vert de cadrage` reste sur la carte jusqu'à ce que le coordinateur ait agi et en ait accusé réception dans le terminal de l'orchestrateur de tâche. Suivi à la lettre, le merge efface ce segment, et ferme ce terminal, avant la publication qu'il autorise.
  - Pas de risque : sans citation, le coordinateur redemande l'accord au mainteneur. Mais l'ordre peut être fixé, par exemple : « pour un cadrage, il publie les issues et les milestones juste après le `git pull`, avant de passer la carte à « ✓ mergé » et de nettoyer le worktree ».
- **S2, ligne de table incomplète** : `docs/decisions/0015-remontee-carte-seule-coordinateur-flottant.md:38`.
  - La ligne « Feu vert donné dans le worktree, remonté par un message court → Cité dans le commentaire de la carte » ne reprend pas la restriction de la décision (ligne 24) : seul un feu vert qui ouvre une action du coordinateur est cité.
  - Lue seule, la table laisse croire qu'un feu vert plan ou recette donné dans le worktree est lui aussi cité, et l'ADR 0013 (ligne 38) disait « tout feu vert est transmis à l'autre niveau ».
  - Correction proposée : « Cité dans le commentaire de la carte s'il ouvre une action du coordinateur (merge, publication) ; sinon, l'orchestrateur de tâche agit et le segment d'état change ».
- **S3, sujet de phrase** : `docs/process/roles/implementeur.md:13`.
  - Dans « La liste ne contient ni `rm` ni arrêt de processus, et ne doit pas s'en servir par détour », le sujet grammatical de « ne doit pas s'en servir » est « la liste ».
  - Correction proposée : « …ni arrêt de processus, et l'implémenteur ne les obtient pas par détour (`node -e`) ».

RELECTURE : OK
