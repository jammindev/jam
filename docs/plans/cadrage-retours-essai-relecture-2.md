# Relecture : cadrage-retours-essai, tour 2

Relecteur seul (docs) : les deux axes. J'ai relu le diff non commité du worktree, la nouvelle ADR 0015 et le rapport du rédacteur. Je les ai confrontés au brief du rédacteur, aux 14 frictions de #7, à la commande du recetteur de #7, au rapport de recette de #7 et à l'ADR 0013.

**Écart à l'indépendance** : j'ai ouvert `cadrage-retours-essai-relecture-1.md` au début de la session, avant d'avoir relu la règle de mon profil qui l'interdit. Les constats ci-dessous viennent de ma propre lecture du diff. L'orchestrateur de tâche peut en tenir compte quand il compare les tours.

## Ce qui a été vérifié et tient

- **Carte seule** : le message court n'apparaît plus comme canal en vigueur dans le process, les profils, le glossaire ni `AGENTS.md`. Il ne reste que des mentions historiques (RET-009, ADR 0013, acceptée et non retouchée) ou des mentions qui décrivent l'abandon (ADR 0015, RET-013, Q-037). Le brief de l'orchestrateur de tâche ne contient plus le handle du coordinateur (process:79, `orchestrateur-tache.md:18`). Les seuls `orca terminal send` qui restent vont du coordinateur vers un orchestrateur de tâche, ou d'un orchestrateur de tâche vers ses rôles.
- **Feu vert relayé** : « Format de tout feu vert relayé » (process:133) couvre les deux supports : le terminal de l'orchestrateur de tâche dans un sens, un segment `✓` de la carte dans l'autre. Les trois éléments exigés et la règle « l'action que ce feu vert ouvre, et elle seule » sont inchangés. La limite d'authentification est étendue aux commentaires de carte. Le profil du coordinateur (:27) et celui de l'orchestrateur de tâche (:25-26) disent la même chose. Le cas du cadrage, où le feu vert de cadrage (publication) et le feu vert merge sont en attente ensemble, est couvert par deux exemples (process:129-130).
- **RET-012** : la remarque est citée, l'analyse est attribuée au coordinateur, et RET-008 tient (`cd` vers le worktree principal, puis `--continue`). La traduction pour jam est une précision de FR-016, sans changement d'étape (Q-039). Elle est cohérente avec la « Correspondance avec jam » de l'ADR 0013 (niveau projet = cockpit + session de `main`). Le cas de plusieurs repos est renvoyé à Q-051.
- **ADR 0015** : c'est une nouvelle ADR, et non une retouche de l'ADR 0013, qui est acceptée. Son statut est « proposée », et l'index (`decisions/README.md`) dit « Proposée ». La mention à reporter dans le statut de l'ADR 0013 est prévue (:43) ; le process (étape 4 du cadrage) dit qui la reporte.
- **Les 14 frictions** ont toutes un sort, tracé dans les docs :
  - 1 : Q-033, porteur corrigé ;
  - 2 : process:81 et `coordinateur.md:29` ;
  - 3 : Q-036 ;
  - 4, 12 et 14 : ADR 0015 et RET-013 ;
  - 5 : `implementeur.md:13` et `planificateur.md:18` ;
  - 6 : process:146 ;
  - 7, 9 et 10 : profil du recetteur, et Q-050 pour la friction 9 ;
  - 8 : process:98 ;
  - 11 : `orchestrateur-tache.md:28` et process:49 ;
  - 13 : `orchestrateur-tache.md:29` et `coordinateur.md:30`.

  J'ai vérifié le fait sur lequel repose Q-050 : l'app passe `--db` au cœur (`apps/desktop/src/main/core-process.ts:25`, `index.ts:43`), et `JAM_DATA_DIR` ne sert que sans `--db` (`packages/core/src/paths.ts:10`).
- **Commande du recetteur** (`recetteur.md:9`) :
  - les formes `rtk` sont présentes pour les commandes que RTK réécrit ;
  - interdits : `Edit(.claude/**)`, commit, push et `gh`, sous les deux formes ;
  - aucun chemin propre au poste ni nom de worktree en dur : tout passe par `<tâche>`, `<dossier de recette>` et `<chemin du worktree>`, et la règle de remplacement est donnée, syntaxe `//` de `Edit` comprise ;
  - plus aucun `pkill`. L'arrêt passe par la tâche de fond, et `pgrep -fl <chemin du worktree>/` vise ce worktree seul : le `/` final évite un worktree au nom voisin, et le chemin de `main` n'en est pas un préfixe. Le cœur est lancé avec un chemin absolu (`require.resolve`, `core-process.ts:24`) : `pgrep` le trouve donc aussi ;
  - elle couvre toute la recette de #7 : `rm -rf` exact, `pnpm install`, `ls`, `pnpm dev` puis `pnpm dev --remoteDebuggingPort 9333`, `curl`, `screencapture`, `pgrep`, `pnpm check` et `pnpm core:ping`. Elle couvre aussi l'écriture des journaux dans le dossier de recette. Seul Cmd+K n'est pas couvert, et le profil le laisse au mainteneur (:15).
- **Numérotation** : seuls RET-012, RET-013, Q-050, Q-051 et l'ADR 0015 sont utilisés. Aucune référence à RET-011, Q-040, Q-042 à Q-049 ni à l'ADR 0014. Les ajouts sont en fin de table ou de section.
- **Statuts** : RET-012 et RET-013 sont « en application », et non « appliqué ». L'ADR 0015 est « proposée ».
- **Vocabulaire** : nouveau terme « Terminal flottant » au glossaire, utilisé tel quel. « Orchestrateur de tâche », « carte », « feu vert » et « cadrage » sont conformes.
- **Repo public** : aucun chemin machine ni donnée personnelle dans les fichiers modifiés.

## Constats

### À corriger

**C1. L'ordre des segments cumulés et le statut de la carte ne sont pas fixés, alors que le tri repose sur le premier caractère.**
- Fichiers : `docs/process/README.md:170`, `:172` et `:174` ; `docs/process/roles/orchestrateur-tache.md:27` ; `docs/process/roles/coordinateur.md:26` ; ADR 0015:22.
- Constat :
  - :172 classe une carte selon le **début** de son commentaire : `⏸`/`⛔` pour le mainteneur, `✓`/`💬` pour le coordinateur.
  - :174 garde un segment `✓` ou `💬` « même quand l'état de la tâche change ». Un `💬` peut donc coexister avec `▶ <rôle> en cours` ou avec `⏸ feu vert plan : …`.
  - Rien ne dit dans quel ordre écrire les segments. Rien ne dit non plus quel statut porte la carte : la ligne `💬` de la table impose `in-review`, alors que la ligne `▶` impose `in-progress`.
- Exemples concrets :
  - un retour arrive pendant l'implémentation. La carte devient `in-review` avec `💬 retour : … · ▶ implémenteur en cours`. Elle est alors classée « attend le coordinateur », alors qu'un rôle travaille. Ou bien elle reste `in-progress` contre la table ;
  - plus tard, la carte porte `💬 retour : … · ⏸ feu vert plan : …`. Elle commence par `💬`, donc le mainteneur, qui ne regarde que les cartes `⏸` et `⛔` (:172, :192), ne voit pas le feu vert plan qui l'attend.
- Correction attendue :
  - fixer l'ordre : le segment d'état (`▶`, `⏸` ou `⛔`) toujours en tête, puis les segments `✓` et `💬` ;
  - le statut suit le segment d'état. Une carte ne passe en `in-review` pour un `✓` ou un `💬` que si elle n'a pas de segment d'état, comme dans l'exemple :130 ;
  - le coordinateur cherche les segments `✓` et `💬` sur toutes les cartes, quel que soit leur statut ;
  - adapter la colonne « Statut » des lignes `✓` et `💬` de la table (par exemple : « celui de l'état en cours, `in-review` s'il n'y en a pas »), et la phrase de :172.

### Suggestions

**S1. ADR 0015:41, « Le reste de l'ADR 0013 tient ».** Trois conséquences de l'ADR 0013 ne tiennent plus telles quelles :
- :81 : « il ne voit des tâches que les cartes et les messages courts » ;
- :87 : le risque Q-037, qui s'est réalisé, et que la carte seule supprime ;
- :89 : « ni prévenir le coordinateur ».

Proposition : ajouter une ligne « Conséquences (+) contexte léger, (−) Q-037, (−) invite de permission » au tableau « Ce que l'ADR 0013 devient », ou exclure ces conséquences de la phrase :41.

**S2. `recetteur.md:9`, `"Bash(curl -s http://localhost:9333/json*)"`.** Le joker couvre aussi `/json/close/<id>` et `/json/activate/<id>`, qui agissent sur la fenêtre au lieu de la lire. Proposition : les formes exactes `curl -s http://localhost:9333/json` et `curl -s http://localhost:9333/json/list`, avec leurs formes `rtk`. C'est sans effet sur la recette de #7, qui n'a lu que `/json`.

**S3. `coordinateur.md:28`, analyse d'un retour `💬`.** Le fichier est dans un dossier temporaire de la session de l'orchestrateur de tâche, qui disparaît au nettoyage du worktree. On peut préciser que le coordinateur reprend ce contenu dans le brief du cadrage auquel il confie le retour, au lieu d'y renvoyer par le chemin.

RELECTURE : CORRECTIONS (1)
