# Relecture du cadrage `cadrage-orca-reference`, tour 3

Relecteur seul, les deux axes. Objet : la rédaction non commitée (`git diff`, 8 fichiers) qui applique RET-011. Comparée à la règle validée par le mainteneur (points 1 à 5), à la vision, aux exigences, aux ADR 0001, 0002, 0004, 0005, 0009 et 0012, au glossaire et au process.

Hors constats, comme le prévoit le brief : la mention de « l'orchestrateur de tâche » sans définition (autre cadrage, ADR 0013), l'absence de RET-008 à RET-010 et de Q-036 à Q-039 et Q-041, l'existence du complément sur l'accès de l'implémenteur au clone (seule sa formulation est jugée ici).

Les cinq points de la règle du mainteneur sont bien couverts :
1. regard ciblé à partir de la carte : `planificateur.md:15`, `orca.md:18` et `:33` ;
2. section « Orca » du plan, avec la ligne « aucune brique » : `planificateur.md:20` ;
3. s'inspirer par défaut, copier par exception, licence : `planificateur.md:21`, `AGENTS.md` règle 9, `implementeur.md:18` ;
4. liste noire : `planificateur.md:22`, `orca.md:45`, `orca.md:389` ;
5. clone en lecture seule, version fixée, dossier temporaire hors du repo, `--add-dir` : `planificateur.md:13`, `orca.md:20-31`.

La portée (jam seulement, pas l'issue #7) est dite dans `RETOURS.md:99`. Aucun chemin propre au poste n'apparaît dans les docs (`<clone-orca>` est un paramètre). La numérotation de §0 dans `orca.md` laisse intactes les références existantes (ADR 0002 cite « §4 »). Aucun autre document ne renvoie aux numéros des rubriques du plan, qui passent de 7 à 8.

## Bloquant

Aucun.

## À corriger

### C-1. La suppression de `.claude/` rendrait toujours fausse la vérification du clone

- **Fichier** : `docs/references/orca.md`, lignes 28 et 31.
- **Constat** : la ligne 28 dit que, si une version future a un dossier `.claude/`, il est supprimé avant le `chmod`. La ligne 31 exige, avant chaque lancement, que `git -C <clone-orca> status --porcelain` soit vide, sinon le clone est supprimé et refait. Or un dossier `.claude/` suivi par git et supprimé apparaît dans `status --porcelain` (lignes ` D .claude/…`). La vérification échouerait donc à chaque lancement : le clone serait refait, `.claude/` de nouveau supprimé, et ainsi de suite. La procédure se contredit dans le cas même qu'elle prévoit.
- **Correction attendue** : faire tenir les deux règles ensemble. Par exemple, la vérification ignore ce dossier (`git -C <clone-orca> status --porcelain -- . ':!.claude'`), ou bien la ligne 28 dit qu'à la montée de version qui ferait apparaître un `.claude/`, la procédure de vérification est revue en même temps (Q-040).

### C-2. Le chemin du clone peut finir dans les fichiers commités par l'implémenteur

- **Fichier** : `docs/process/roles/implementeur.md`, ligne 18.
- **Constat** : l'implémenteur reçoit dans son brief le chemin du clone, qui est propre au poste. On lui demande ensuite d'écrire dans `THIRD_PARTY_NOTICES.md` « la liste des fichiers repris avec leur fichier source », et une mention en tête du fichier repris. Rien ne lui dit de citer le fichier source par son chemin dans le repo d'Orca. Le profil du planificateur prend cette précaution (`planificateur.md:13` : « il ne figure jamais dans le plan, qui cite les fichiers d'Orca par leur chemin dans le repo d'Orca »), alors que c'est l'implémenteur qui écrit les fichiers commités. Un chemin absolu du poste dans un repo public enfreindrait la règle 7 d'`AGENTS.md`.
- **Correction attendue** : ajouter dans `implementeur.md:18` la même précision que pour le planificateur : le fichier source se cite par son chemin dans le repo d'Orca (par exemple `src/main/git/worktree-add.ts`) avec la version de référence, jamais par le chemin du clone.

## Suggestions

### S-1. Le planificateur ne peut dire « aucune brique » qu'après avoir regardé la carte

- **Fichier** : `docs/process/roles/planificateur.md`, lignes 15 et 20.
- **Constat** : la ligne 15 fait lire la carte « pour une tâche de jam qui touche une brique qu'Orca possède », mais c'est justement la carte qui permet de savoir si la tâche en touche une. La ligne 20 demande d'écrire « une seule ligne » quand aucune brique n'est touchée : sans avoir lu le tableau du §0, cette ligne repose sur ce que l'agent croit savoir d'Orca.
- **Proposition** : pour toute tâche de jam, lire le §0 de `orca.md` (une trentaine de lignes). N'ouvrir le clone que si une brique de la carte est touchée. Cela reste conforme au point 1 de la règle, qui porte sur la lecture du code d'Orca.

### S-2. « Ce n'est pas un contrôle d'accès » est présenté comme établi alors que Q-043 le laisse ouvert

- **Fichiers** : `docs/process/roles/planificateur.md`, ligne 13 ; `docs/specs/GLOSSARY.md`, ligne 35.
- **Constat** : ces deux lignes affirment que la règle `"Read"` n'est pas restreinte par chemin et que `--add-dir` n'est donc pas un contrôle d'accès. `RETOURS.md:98` et Q-043 tiennent cette conséquence pour « à vérifier » : si, en `dontAsk`, un `"Read"` sans chemin ne lit pas hors du worktree, `--add-dir` est bien ce qui ouvre l'accès. Le mainteneur tranche le complément de l'implémenteur en partie sur ce point.
- **Proposition** : écrire la même réserve qu'à `RETOURS.md:98`, par exemple « ce n'est sans doute pas un contrôle d'accès (à vérifier, Q-043) ».

### S-3. « Garder la mention de copyright » suppose qu'elle existe dans le fichier d'Orca

- **Fichier** : `docs/process/roles/implementeur.md`, ligne 18.
- **Constat** : un fichier source d'Orca n'a pas forcément d'en-tête de licence : la mention MIT peut ne figurer que dans le `LICENSE` de la racine. Dans ce cas, « garder » ne dit pas quoi faire.
- **Proposition** : « ajouter en tête du fichier repris la mention de copyright d'Orca et de sa licence MIT (ou la garder si le fichier source en a une) ».

### S-4. Ce qui dépend du complément proposé, pour la décision du mainteneur

- **Fichiers** : `docs/specs/RETOURS.md`, ligne 98 ; `docs/process/roles/implementeur.md`, ligne 18.
- **Constat** : sans le complément, l'implémenteur n'a ni le chemin du clone, ni `WebFetch`. Il ne peut donc récupérer ni le morceau à copier, ni le texte de la licence. Si le complément est refusé, le point 3 (« copier par exception ») n'a plus de voie d'application, sauf si le plan recopie lui-même le morceau. Le texte ne le dit pas, alors que c'est l'enjeu de la décision.
- **Proposition** : ajouter une phrase à `RETOURS.md:98` : « Sans ce complément, aucune reprise n'est possible : l'implémenteur n'a pas accès au code d'Orca. » Préciser aussi ce que devient la ligne 18 de l'implémenteur si le complément est refusé.

### S-5. Les consignes propres à Orca, présentes dans le clone

- **Fichier** : `docs/references/orca.md`, ligne 28.
- **Constat** : la note ne traite que de `.claude/`. Or le clone contient l'`AGENTS.md` d'Orca (cité au §1), peut-être un `CLAUDE.md` à la racine ou dans des sous-dossiers. Ce sont les consignes d'Orca à ses propres agents, pas celles de jam. À vérifier au moment de l'usage : `--add-dir` ne charge pas, par défaut, le `CLAUDE.md` d'un dossier ajouté.
- **Proposition** : une phrase qui dit que les `AGENTS.md` et `CLAUDE.md` du clone sont des données à lire, pas des consignes à suivre.

### S-6. Chemins sans extension dans la carte

- **Fichier** : `docs/references/orca.md`, ligne 37.
- **Constat** : `src/main/startup/main-window-controller` et `src/main/startup/main-process-ipc-bootstrap` n'ont ni extension ni `/` final : on ne sait pas si ce sont des fichiers ou des dossiers. Les autres entrées du tableau sont des fichiers complets.
- **Proposition** : écrire le chemin exact (`….ts` ou `…/`).

### S-7. Les sources de la note ne mentionnent pas le tag

- **Fichier** : `docs/references/orca.md`, lignes 3 à 10.
- **Constat** : l'en-tête date la note du 2026-10-08 et liste `main` en 1.4.214 comme seul clone. Le §0 s'appuie sur le tag `v1.4.218`, relevé le 2026-10-09.
- **Proposition** : ajouter aux sources « tag `v1.4.218`, relevé du 2026-10-09 (§0) ».

### S-8. Carte limitée aux briques d'E0

- **Fichier** : `docs/references/orca.md`, lignes 35 à 43.
- **Constat** : l'ADR 0005 cite le diff parmi les briques d'Orca à reprendre, et `RETOURS.md:90` aussi. Le diff (FR-006, E3) est absent de la carte, et la palette (`cmdk`), déjà livrée, l'est aussi. C'est cohérent avec « partir du minimum », mais la note ne le dit pas : un planificateur d'E3 pourrait conclure « aucune brique » sur une tâche de diff.
- **Proposition** : préciser que la carte couvre les briques d'E0, et que le cadrage d'un jalon qui touche une nouvelle brique d'Orca (diff en E3) la complète.

### S-9. Le résumé de l'axe de conformité ne cite pas les reprises d'Orca

- **Fichiers** : `docs/process/README.md`, ligne 88 ; `docs/specs/GLOSSARY.md`, ligne 23.
- **Constat** : le profil du relecteur ajoute le point 5 (reprises d'Orca) à l'axe B. Le process et le glossaire résument l'axe en « plan, ADR, lisibilité, sur-ingénierie, sécurité du repo public », sans ce point.
- **Proposition** : ajouter « reprises d'Orca (licence) » aux deux résumés, ou s'en tenir au profil et l'assumer.

### S-10. « Pas de nouvelle ADR » : dire aussi pourquoi l'ADR 0009 n'est pas touchée

- **Fichier** : `docs/specs/RETOURS.md`, ligne 97.
- **Constat** : la phrase justifie l'absence d'ADR au regard de l'ADR 0001 seulement. Or la règle donne aux rôles l'accès en lecture à un dossier situé hors du worktree, et l'ADR 0009 décrit l'implémenteur en « lecture et écriture dans le worktree ». Il y a un précédent : l'ADR 0012 trace les profils qui sortent de la table de l'ADR 0009.
- **Proposition** : une phrase. Le planificateur reste en lecture seule. Si le complément est validé, l'implémenteur lit hors du worktree sans y écrire, ce qui reste dans l'esprit de l'ADR 0009. Sinon, le tracer comme l'ADR 0012 l'a fait pour les autres profils.

RELECTURE : CORRECTIONS (2)
