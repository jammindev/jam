# Relecture conformité — #23 Process élagué (K1-2), tour 8

Relecteur B, axe conformité. Relu : tout le travail non commité de la branche (`git status`, `git diff -M`, fichiers non suivis), comparé au worktree principal pour `docs/process/` d'avant. `python3 -m unittest` : **184 tests, OK** (dont le plafond de mots et l'absence de `pnpm`, `/Users/`, `/home/` dans `process/` et `roles/`, `hooks/test_plugin.py`).

## Critère de fin de l'issue, point par point

| Point | Verdict |
|---|---|
| `process/`, `roles/`, `process/fiche-projet.md` existent ; `docs/process/` ne contient que le renvoi | OK (`docs/process/README.md` seul, liens justes) |
| Plafond de 4904 mots pour `process/` et `roles/`, fiche comprise | OK (test `test_under_word_cap` vert ; `test_no_file_left_uncounted` empêche un fichier hors compte). Les nombres avant et après restent à mettre dans le corps de la PR |
| Ni `pnpm`, ni chemin, ni nom d'hôte ou d'autre projet dans `process/` et `roles/` | OK (test, plus recherche manuelle : aucune occurrence) |
| Chaque règle du point 3 dans le process **et** dans le profil qui l'applique, avec sa référence | OK : niveaux (process l. 16, coordinateur l. 17, planificateur l. 16, FR-049) ; *léger* (process l. 20, coordinateur l. 19, FR-052) ; seuil (process l. 84, relecteur l. 21, orchestrateur l. 20, FR-050) ; plafonds (process l. 96, coordinateur l. 18, orchestrateur l. 14, FR-051) ; relais (process l. 72-77, coordinateur l. 23, orchestrateur l. 17-18, FR-053) ; interface (process l. 91, recetteur l. 17, FR-054) ; mesure (process l. 110, coordinateur l. 19, orchestrateur l. 21, FR-055, RET-018) ; ADR 0017 et Q-058 (process l. 35, 39, 79, orchestrateur l. 7, coordinateur l. 20) |
| Planificateur : niveau motivé quand une tâche monte | OK (`roles/planificateur.md:16`) |
| Règle 6 d'`AGENTS.md` cohérente avec FR-052 et FR-053 | OK |
| `docs/methode.md` au niveau *léger* ; Q-058 tranchée et cohérente | OK (fiche l. 5 ; Q-058, ADR 0018, glossaire « Note de suivi », profil de l'orchestrateur ; statut de l'ADR 0013 prévu à l'acceptation) |

Autres points demandés, conformes : « Origine : … » absent de `process/` et `roles/`, origines reportées dans l'ADR 0018 ; règles propres à jam dans la fiche ; niveau *léger* cohérent dans le process, le profil du coordinateur, le glossaire et `AGENTS.md` ; ADR existantes touchées seulement aux liens (0009, 0012, 0013) ; aucun lien cassé vers l'ancien `docs/process/` hors `docs/plans/` ; règle « Messages au mainteneur » en deux phrases, fidèle à RET-019, citée par l'ADR 0018 et reprise dans les profils du coordinateur, de l'orchestrateur, du planificateur et du recetteur ; explication de la friction 18 cohérente entre `process/README.md:103`, `roles/recetteur.md:11`, l'ADR 0018 l. 60 et `docs/methode.md:13`, avec Q-064 ; écart à l'issue sur la mesure acté (ADR 0018 l. 42, RET-018) et cohérent avec FR-055, FR-046, FR-056, `00-VISION.md`, `02-ARCHITECTURE.md`, `04-ROADMAP.md`, le glossaire et la fiche concept ; « le mainteneur valide le chiffre » ne reste nulle part comme règle ; lecture côté tâche retirée du script, transcript sans `cwd` écarté, `--issue` accepté avec `#`, veille relancée avant le traitement du réveil et sa limite écrite (process l. 79, coordinateur l. 20, concept l. 41). Aucun secret, chemin du poste, nom de personne ou d'hôte dans le diff (les chemins des tests sont fictifs).

## Bloquant

Aucun.

## À corriger

1. **Règles de permission changées dans les profils sans trace dans l'ADR 0018 (NFR-016).**
   - **Où** : `docs/decisions/0018-process-elague.md`, table « Ce que chaque règle nouvelle remplace ou retire » (l. 46-70) ; règles concernées dans `roles/*.md`, ligne de commande (l. 9), notamment `roles/relecteur.md:9`.
   - **Constat** : trois changements de profil n'y ont pas de ligne :
     - toutes les règles `Edit` sont désormais ancrées par `/` ;
     - le relecteur n'écrit plus que son rapport exact (`Edit(/docs/plans/<rapport>)`, au lieu de `Edit(docs/plans/*-relecture*.md)`) ;
     - le relecteur perd son interdit `Edit(.claude/**)`. Le planificateur perd aussi le sien, mais celui-là est tracé par Q-027.

     La seule mention de l'ancrage, l. 60, dit que « l'ancrage par `/` n'y change rien ». Or NFR-016 demande que chaque règle nouvelle dise ce qu'elle remplace ou retire, et le process (l. 3) renvoie à l'ADR 0018 pour le savoir.
   - **Scénario d'échec** : un mainteneur adapte un profil, ou le rédacteur d'une tâche future en retouche un. Il cherche dans l'ADR 0018 pourquoi les règles sont ancrées par `/`. Il n'y trouve que « l'ancrage par `/` n'y change rien », retire le `/`, et la règle se résout de nouveau depuis le dossier courant de la session (ce que le plan de #23 voulait éviter, §2). Même chose pour le rapport exact du relecteur : rien ne dit qu'il ferme la limite « le relecteur peut réécrire les rapports des tours précédents », que l'ancien process listait.
   - **Correction attendue** : une ligne de plus dans la table, par exemple : « Règles `Edit` des profils ancrées par `/` (résolues depuis le dossier de lancement, pas depuis le dossier courant) ; relecteur limité au rapport que nomme son brief, donc sans interdit `.claude/` | Règles relatives sans ancrage ; `Edit(docs/plans/*-relecture*.md)`, qui laissait réécrire les rapports des tours précédents | Plan de #23, §2 et annexe A ». Il faut aussi réécrire la fin de la l. 60 : l'ancrage ne règle pas la friction 18, mais il reste la forme des profils pour une autre raison.

2. **L'issue de la page publique (K1-3) contredit FR-056 réécrit, et rien ne le signale.**
   - **Où** : `docs/specs/RETOURS.md:253` (Impact de RET-018). Le texte publié de l'issue K1-3 est repris de `docs/plans/cadrage-kit-issues.md:150` et `:156`.
   - **Constat** : l'issue K1-3 demande « chiffres mesurés à l'appui » et « seulement ceux qui ont été mesurés ». Après RET-018, FR-056, `00-VISION.md` et `04-ROADMAP.md` parlent de chiffres **estimés par script**, présentés comme des estimations. L'Impact de RET-018 ne cite pas l'issue K1-3, et aucune question ouverte ne note qu'elle est à aligner.
   - **Scénario d'échec** : à la tâche K1-3, l'implémenteur ou le rédacteur suit l'issue (« seulement ceux qui ont été mesurés »). Les seuls chiffres disponibles sont des estimations : soit la page sort sans chiffres, soit elle les présente comme des mesures. Les deux s'écartent de FR-056, et le relecteur ne voit la contradiction qu'en recoupant l'issue avec les specs.
   - **Correction attendue** : ajouter à l'Impact de RET-018 l'issue K1-3, dont le passage « Chiffres » est à aligner sur FR-056 (corps de l'issue modifié par le coordinateur après le merge, sur feu vert), ou une ligne équivalente dans les questions ouvertes.

## Suggestions

1. `docs/specs/RETOURS.md:259` : « suit plusieurs projets **en plus de son travail** » donne un détail de la vie du mainteneur, inutile au retour (`AGENTS.md`, règle 7 ; l'issue K1-3 exclut aussi ce genre de détail). « Suit plusieurs projets » suffit.
2. `process/README.md:103` : « Une règle `Edit` est relative, ancrée par `/` (…) ou absolue » se lit mal pour un mainteneur qui ne code pas, car on ne voit pas qu'il s'agit de deux formes. Proposition : « Une règle `Edit` s'écrit ancrée par `/` (`Edit(/docs/plans/x.md)`, résolue depuis le dossier de lancement de la session) ou absolue (`//` suivi du chemin sans son `/` initial). »
3. `scripts/watch_cards.py`, docstring (vers la l. 30) : dans « the coordinator relaunches it at once », « it » peut désigner l'agent bloqué, alors qu'il s'agit du script. Écrire « relaunches the watch at once ».
4. `hooks/test_plugin.py:2` : la docstring ne parle que du câblage (`.claude-plugin/`, `hooks.json`), alors que le fichier teste aussi la méthode (plafond NFR-015, généricité NFR-014). Il faut l'ajouter en une ligne.
5. Niveau *léger*, trois trous mineurs :
   - `process/README.md:85` dit « c'est l'orchestrateur de tâche qui compare », alors qu'en *léger* c'est le coordinateur. Écrire « la session qui conduit la tâche ».
   - `process/README.md:35` ne dit pas qui analyse un retour reçu dans un worktree sans orchestrateur.
   - La règle `gh pr create --milestone` n'est que dans le profil de l'orchestrateur, alors qu'en *léger* c'est le coordinateur qui ouvre la PR.
6. Corps de la PR : le critère de fin demande les nombres de mots avant (9808) et après. Ils ne sont écrits nulle part dans la branche, et c'est à l'orchestrateur de tâche de les reporter (le test ne donne le total qu'en cas d'échec).

RELECTURE : CORRECTIONS (2)
