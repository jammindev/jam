# Relecture : cadrage-retours-essai, tour 1

Relecteur seul (docs) : les deux axes. J'ai relu le diff non commité du worktree, la nouvelle ADR 0015 et le rapport du rédacteur, en les confrontant au brief du rédacteur, aux 14 frictions de #7, à la commande du recetteur de #7 et au rapport de recette de #7.

## Ce qui a été vérifié et tient

- **Message court supprimé** : aucune mention restante dans le process, les profils, le glossaire ni `AGENTS.md`. Les seules occurrences sont historiques (RET-009, ADR 0013, acceptée et non retouchée) ou décrivent l'abandon (ADR 0015, RET-013). Le brief de l'orchestrateur de tâche ne contient plus le handle du coordinateur (process:79, `orchestrateur-tache.md:18`), et la justification par le handle a disparu du lancement du coordinateur.
- **ADR 0015** : nouvelle ADR plutôt que retouche de l'ADR 0013, qui est acceptée. Statut « proposée », index `decisions/README.md` à « Proposée ». La table « Ce que l'ADR 0013 devient » couvre le lancement, la remontée, le feu vert relayé et la correspondance avec jam.
- **RET-012** : la remarque est citée, l'analyse vient du coordinateur, RET-008 tient (le `cd` vers le worktree principal, puis `--continue`). La traduction pour jam passe par une précision de FR-016, sans changer l'étape (Q-039), et reste cohérente avec l'ADR 0013, « Correspondance avec jam ».
- **Numérotation** : seuls RET-012, RET-013, Q-050 et ADR 0015 sont utilisés. Aucune référence à RET-011, Q-040, Q-042 à Q-049 ni ADR 0014. Les ajouts sont placés en fin de table ou de section.
- **Statuts** : RET-012 et RET-013 sont « en application », ce qui est le statut défini en tête de `RETOURS.md` pendant la rédaction. L'ADR 0015 est « proposée ».
- **Les 14 frictions** ont toutes un sort, justifié dans le rapport de rédaction et tracé dans les docs. J'ai contrôlé les faits suivants :
  - Q-050 : l'app passe bien `--db` au cœur (`apps/desktop/src/main/core-process.ts:25`, chemin construit dans `apps/desktop/src/main/index.ts:43`). `JAM_DATA_DIR` ne joue donc que sans `--db`.
  - Règle de rebase : la CI tourne bien sur `pull_request` (`.github/workflows/ci.yml:4`).
  - Les `node_modules` listés dans le `rm -rf` correspondent aux trois paquets présents (`apps/desktop`, `packages/core`, `packages/protocol`).
- **Commande du recetteur** :
  - formes `rtk` présentes là où RTK réécrit ; `Edit(.claude/**)` interdit ; ni commit, ni push, ni `gh` ;
  - aucun chemin propre au poste ni nom de worktree en dur ;
  - plus aucun `pkill`, et l'arrêt passe par la tâche de fond, ce qui épargne l'instance du mainteneur ;
  - elle couvre les dix vérifications du rapport de recette de #7, dont `pgrep`, qui était utilisé à #7 sans figurer dans la commande. Seul Cmd+K n'est pas couvert, et le profil le laisse explicitement au mainteneur.
- **Repo public** : aucun chemin machine dans les fichiers modifiés.

## Constats

### À corriger

**C1. Un retour reçu par l'orchestrateur de tâche n'a pas de forme sur la carte.**
- Fichiers : `docs/process/README.md:28`, `docs/process/roles/orchestrateur-tache.md:27`, table « Signalement d'attente » (`docs/process/README.md:159-165`).
- Constat : le message court garantissait que le coordinateur recevait le retour. Désormais, l'orchestrateur de tâche « le signale dans le commentaire de sa carte », mais aucune ligne de la table ne dit avec quel statut ni quel format. Le coordinateur ne prévient le mainteneur que lorsqu'une carte passe en `in-review` (process:126, `coordinateur.md:26`). Un retour signalé sur une carte `in-progress` est donc invisible, puis écrasé au prochain `▶ <rôle> en cours`. Enfin, la carte ne porte qu'une ligne, alors que la reformulation et l'analyse demandent un fichier, qu'il faut situer.
- Correction attendue : ajouter une ligne à la table, par exemple statut `in-review` et commentaire `💬 retour : <une ligne>, <fichier de l'analyse>`, conservée jusqu'à ce que le coordinateur l'ait pris en compte. Préciser où l'orchestrateur de tâche écrit la reformulation : il ne peut écrire que dans les dossiers temporaires de sa session. Autre option : faire surveiller au coordinateur tout changement de commentaire, et pas seulement le passage en `in-review`.

**C2. Les suggestions récurrentes n'ont pas de canal vers le mainteneur.**
- Fichier : `docs/process/README.md:142`.
- Constat : « Il cite celles qui sont revenues au mainteneur, avec le feu vert suivant ». Sous la règle de la carte seule (une ligne, qui désigne un fichier), l'orchestrateur de tâche n'a aucun support pour citer ces suggestions, sauf si le mainteneur vient dans son terminal. Le coordinateur, qui présente le feu vert, n'en saura rien.
- Correction attendue : dire comment elles remontent. Par exemple : le commentaire du feu vert désigne aussi le ou les fichiers de relecture où la suggestion revient (`… · suggestion récurrente : <chemin du worktree>/docs/plans/<tâche>-relecture-<axe>-<tour>.md`), et le coordinateur les présente au mainteneur avec le feu vert.

**C3. Deux citations de feu vert peuvent devoir coexister sur la carte d'un cadrage, et l'exemple n'en montre qu'une.**
- Fichiers : `docs/process/README.md:128-129` et :165, `orchestrateur-tache.md:25`.
- Constat : après la PR d'un cadrage, la carte porte `⏸ feu vert merge · cadrage : « ok cadrage », …`, et « le commentaire garde cette citation tant que le coordinateur n'a pas agi ». La publication n'a lieu qu'après le merge. Si le mainteneur donne ensuite le feu vert merge dans le worktree, l'exemple de format (`✓ feu vert merge : « ok merge », …`) remplace la ligne, et la citation du feu vert de cadrage, qui ouvre la publication, disparaît. Le coordinateur devrait alors demander confirmation, ou publier sur la foi d'une lecture antérieure de la carte. Les deux exemples utilisent en outre des préfixes différents (`⏸` et `✓`) pour un même type de ligne, sans que la table le précise.
- Correction attendue : écrire que les citations en attente d'une action du coordinateur se cumulent sur la ligne, avec un exemple pour le cas du cadrage, comme `✓ feu vert merge : « ok merge », 15:10 · cadrage : « ok cadrage », 14:32, session de l'orchestrateur de tâche`. Fixer le préfixe dans la ligne de la table (`:165`).

### Suggestions

**S1.** `docs/process/roles/recetteur.md:13`
- S'il reste des processus du worktree, le recetteur les signale sans les arrêter, mais rien ne dit qui les arrête : l'orchestrateur de tâche n'a pas d'arrêt de processus non plus. Préciser que c'est le mainteneur, ou le coordinateur avec son accord.
- La justification du rapport de rédaction (un `pkill` sur le chemin tuerait la session du recetteur, dont la ligne de commande contient ce chemin) n'est pas confirmée par #7 : `pgrep -fl 7-electron-install-neuve` n'y a trouvé aucun processus, alors que la commande du recetteur contenait ce nom. Le choix prudent tient quand même ; il vaut mieux ne pas l'appuyer sur cet argument.

**S2.** `docs/process/roles/recetteur.md:11` : « `<tâche>`, `<dossier de recette>` et `<chemin du worktree>` sont remplacés […] en chemins absolus ». `<tâche>` est un nom, pas un chemin. Proposition : « `<tâche>` par le nom de la tâche, les deux autres par des chemins absolus ».

**S3.** ADR 0015, deux retouches :
- `:40` : la phrase attribue à l'ADR 0013 une conséquence sur les commentaires de carte, alors que l'ADR 0013 (`:88`) ne parle que de `orca terminal send`. Proposition : « Cette conséquence s'étend aux commentaires de carte : … ».
- `:48` : la mention « À l'acceptation de cette ADR, le statut de l'ADR 0013… » est placée sous « Correspondance avec jam ». Elle serait mieux sous « Ce que l'ADR 0013 devient ».

**S4.** FR-016 (`01-REQUIREMENTS.md`), ADR 0015:44, `02-ARCHITECTURE.md` : « le worktree principal du repo ». L'app liste plusieurs repos (S1), même si le multi-repo est hors E0 (`04-ROADMAP.md:33`). Le champ global ouvre-t-il un coordinateur par repo, celui du repo affiché ? Le préciser, ou le noter dans une question ouverte, pour que l'exigence reste vérifiable quand plusieurs repos sont configurés.

**S5.** `docs/process/README.md:189` : le partage de `jam.db` entre instances n'est pas une limite d'Orca. La puce irait mieux dans la section « Recette », ou seulement dans le profil du recetteur et Q-050.

**S6.** `docs/process/README.md:165-167` : la ligne « Feu vert donné dans le worktree, pour une action du coordinateur » met la carte en `in-review`, mais c'est le coordinateur qui doit agir. Or la phrase qui suit dit que le mainteneur n'a qu'à regarder les cartes `in-review`. Préciser que ce cas attend le coordinateur, ou choisir un autre statut.

**S7.** `orchestrateur-tache.md:29` : la CI d'une PR tourne sur sa fusion avec `main` au moment du push, et ne se relance pas si `main` avance ensuite. On peut ajouter que le coordinateur vérifie que la PR est toujours mergeable sans conflit au moment du merge.

RELECTURE : CORRECTIONS (3)
