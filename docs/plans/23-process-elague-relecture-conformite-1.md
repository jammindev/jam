# Relecture #23, axe conformité, tour 1

Périmètre : tout le travail non commité de la branche (`git status`, fichiers non suivis compris, et `git diff`), comparé au plan validé `docs/plans/23-process-elague.md`, à l'issue (K1-2 dans `docs/plans/cadrage-kit-issues.md`, l. 91 à 140), aux ADR 0013, 0015, 0016, 0017 et 0018, et à `docs/process/` du worktree principal.

Tests : `python3 -m unittest` donne 172 tests OK. Le test de taille (`hooks/test_plugin.py`, `MethodTest`) passe, donc process et profils tiennent sous 4904 mots.

## Critère de fin, point par point

| Point | Verdict |
|---|---|
| `process/`, `roles/`, `process/fiche-projet.md` existent ; `docs/process/` ne contient plus que `README.md`, un renvoi | OK |
| Plafond de 4904 mots (NFR-015) | OK (test vert). Les nombres avant et après restent à mettre dans la PR |
| Ni `pnpm`, ni chemin du poste, ni nom d'hôte, de personne ou d'autre projet dans `process/` et `roles/` | OK (Grep : aucune occurrence ; les « jam » trouvés sont « jamais » ou la marque `[jam]`) |
| Chaque règle du point 3 dans le process et dans le profil du rôle qui l'applique, avec sa référence | **Incomplet** : C-1 (fenêtre d'autorisation du système, ADR 0017) et C-2 (références) |
| Planificateur : niveau motivé quand la tâche monte d'un niveau | OK (`roles/planificateur.md:16`) |
| Règle 6 d'`AGENTS.md` cohérente avec FR-052 et FR-053 | OK (`AGENTS.md:38`) |
| `docs/methode.md` au niveau *léger* | OK |
| Q-058 tranchée et cohérente avec le profil de l'orchestrateur de tâche | OK dans le process, le profil, le glossaire et Q-058. Mais l'ADR 0013 n'en porte pas la trace : voir C-3 |
| NFR-016 : chaque règle nouvelle dit ce qu'elle remplace ; « Origine : … » remplacé par un renvoi | OK : table de l'ADR 0018, l. 42 à 64. Les cinq « Origine » de `main` (process l. 82, 113, 147, 192 ; implémenteur l. 15) et le « Pourquoi » de la recette sont tous dans l'ADR 0018, l. 72 à 83. Aucun « Origine : » ne reste dans `process/` ni dans `roles/` |
| Règles propres à jam sorties des profils | OK : clone d'Orca, sections « Orca » et « Concepts », nom du worktree, milestones et `--plugin-dir` sont dans `docs/methode.md` |
| ADR existantes : seulement les liens et les mentions de statut prévues | OK pour les diffs de 0009, 0012 et 0013 (liens seuls). Une mention de statut manque au plan de l'ADR 0018 : voir C-3 |
| Liens vers l'ancien `docs/process/` | OK : hors `docs/plans/`, il ne reste que des mentions en texte (ADR 0016 l. 69, NFR-015, RETOURS l. 43, ADR 0018), justes en l'état. Les liens relatifs nouveaux (`process/`, `roles/`, `docs/methode.md`, `docs/process/README.md`, `docs/references/orca.md`, `docs/concepts/veille-et-mesure.md`, RETOURS) visent tous un fichier qui existe |

## Bloquant

Aucun.

## À corriger

### C-1 : la fenêtre d'autorisation du système n'est plus couverte (ADR 0017)

- **Fichiers** : `process/README.md:77` ; `roles/coordinateur.md:19` ; `docs/decisions/0018-process-elague.md:50`.
- **Constat** : l'ADR 0017 (l. 33, décision acceptée) dit : « Quand une carte reste `in-progress` sans changer, le coordinateur envisage ce cas comme une invite de permission, et prévient le mainteneur. » L'ADR 0018 (l. 50) retire cette vérification à la main et la remplace par la veille. Or la veille ne voit pas ce cas : le process (l. 77) écrit lui-même qu'une fenêtre du système « laisse l'agent `working` ». Le point 3 de l'issue demande pourtant d'écrire cette règle de l'ADR 0017 dans le process et dans le profil du coordinateur.
- **Scénario d'échec** : un rôle provoque une demande d'accès au trousseau. L'agent reste `working`, donc ni le réveil « bloqué » ni le réveil « inactif » ne partent. Le profil du coordinateur ne dit plus de vérifier une carte figée. La carte reste `▶` pendant des heures, et le mainteneur n'est jamais prévenu.
- **Correction attendue** : au choix du rédacteur et de l'implémenteur, l'une de ces deux options.
  - **Recommandée** : garder la règle pour ce seul cas, en une phrase. Dans le process, l. 77 : « Une carte `▶` dont le commentaire ne change plus alors que son agent travaille peut cacher une fenêtre du système : le coordinateur prévient le mainteneur (ADR 0017, Q-059). » Mettre la même phrase dans `roles/coordinateur.md:19`. Dans la ligne 50 de l'ADR 0018, écrire que cette règle remplace la vérification à la main, **sauf** pour ce cas.
  - Ou bien acter la perte : une ligne (−) dans les conséquences de l'ADR 0018, et une mention de statut « précisée (0018) » dans l'ADR 0017 qui le dise.

### C-2 : des règles du point 3 n'ont pas leur référence FR ou RET

- **Critère** : selon le brief de relecture, chaque règle du point 3 doit figurer dans le process **et** dans le profil du rôle qui l'applique, avec sa référence. Les lieux où elle manque :
  - `process/README.md:14-22` (« Niveaux ») : ni FR-049 ni FR-052. La section ne cite que Q-061 ;
  - `roles/coordinateur.md:18` (*léger*) : FR-052 ; `roles/coordinateur.md:21` (feux verts) : FR-053, qui manque à côté de RET-017 ;
  - `roles/planificateur.md:16` (niveau motivé) : FR-049 ;
  - `roles/relecteur.md:21` (seuil « assez bon ») : FR-050 ;
  - `roles/orchestrateur-tache.md:17` (feu vert remonté par `✓`) : FR-053 ; `roles/orchestrateur-tache.md:19` (seuil) : FR-050 ;
  - `roles/recetteur.md:17` (captures d'une interface) : FR-054.
- **Scénario d'échec** : un lecteur du profil ne sait pas d'où vient une règle, ni où la contester. C'est justement ce que l'élagage devait garder en remplaçant les « Origine : … » par des renvois.
- **Correction attendue** : ajouter la référence entre parenthèses à chacun de ces endroits. Cela coûte une vingtaine de mots, et le test de taille le vérifiera.

### C-3 : l'ADR 0018 ne prévoit pas de mention de statut dans l'ADR 0013, alors qu'elle en change deux règles

- **Fichiers** : `docs/decisions/0018-process-elague.md:5` et `:94` ; `docs/decisions/0013-orchestration-deux-niveaux.md:3` et `:51`.
- **Constat** : l'ADR 0013 dit (l. 51) que l'orchestrateur de tâche « a les mêmes interdits d'écriture que le coordinateur ». Q-058, tranchée par l'ADR 0018, lui fait pourtant écrire un fichier versionné (`docs/plans/<tâche>-retours.md`). De plus, la ligne 50 de l'ADR 0018 remplace la vérification à la main « (ADR 0013, ADR 0017) ». Malgré cela, l'ADR 0018 ne prévoit une mention « précisée (0018) » que pour les ADR 0016 et 0017 (l. 94), et son en-tête (l. 5) ne cite pas l'ADR 0013. Le profil du rédacteur (`roles/redacteur.md:16`) demande de reporter les mentions « dans le statut des ADR qu'elle touche ».
- **Scénario d'échec** : un relecteur ou un orchestrateur lit l'ADR 0013, qui est acceptée, et n'y trouve aucun renvoi à l'ADR 0018. Il juge alors que la note de suivi des retours viole l'ADR 0013 et la signale en « bloquant », ou bien l'orchestrateur renonce à l'écrire.
- **Correction attendue** : dans l'ADR 0018, l. 5, ajouter « et l'ADR 0013 (écriture de la note de suivi par l'orchestrateur de tâche, veille) ». À la l. 94, ajouter : « celui de l'ADR 0013 "précisée (0018) : l'orchestrateur de tâche écrit la note de suivi d'un retour ; la veille remplace la vérification à la main d'une carte" ».

## Suggestions

- **S-1, relais d'un merge hors production** (`process/fiche-projet.md:13`, `process/README.md:72`). Le gabarit dit : « En production, le feu vert merge se relaie sous sa forme complète. » Cela laisse croire qu'un merge hors production se relaie par un « ok ». Or FR-053 et le process (« et tout autre feu vert ») exigent la forme complète pour tout merge. Le risque reste faible, puisque le coordinateur fait de toute façon confirmer un merge dans son terminal (l. 74). Écrire dans le gabarit : « Le feu vert merge se relaie toujours sous sa forme complète (FR-053) ». La phrase « donc » de `docs/methode.md:14` devient alors inutile.
- **S-2, attendre la fin d'un rôle** (`process/README.md:53`). L'ancien process donnait `orca terminal wait --for tui-idle` pour attendre la fin d'un rôle. Le nouveau ne dit plus comment attendre avant `orca terminal read`. Une demi-phrase suffit : « attendre par `orca terminal wait --for tui-idle`, qui peut conclure trop tôt pendant une longue réflexion (Q-060) ».
- **S-3, carte du §0 d'Orca** (`docs/methode.md:18`, `docs/references/orca.md:19`). `orca.md` dit que sa carte sert au planificateur d'après la fiche, « Règles propres ». La fiche demande la section « Orca » du plan, mais elle ne dit pas de la remplir d'après cette carte. Ajouter « d'après la carte du §0 de `docs/references/orca.md` ».
- **S-4, liens vers les copies du worktree** (`docs/methode.md:3`, `docs/process/README.md:5-7`). Ces liens relatifs visent les copies du repo, celles que le texte voisin dit de ne pas lire. Ils servent à la lecture sur GitHub. Pour qu'un agent ne les suive pas, préciser : « (liens pour la lecture sur GitHub ; un agent suit la ligne « Méthode ») ».
- **S-5, implémenteur** (`roles/implementeur.md`). C'est le seul profil qui écrit sans ligne « Avant de commencer, lire ». Or la fiche de jam lui donne des règles propres (licence d'un morceau repris d'Orca). Ajouter : « Avant de commencer, lire : la fiche du projet, puis le plan (l'issue au niveau *léger*) ».
- **S-6, nom de section périmé** (`docs/decisions/0013-orchestration-deux-niveaux.md:37`). Le lien mis à jour renvoie à la « table « Signalement d'attente » », devenue « Carte, feux verts et veille ». Comme une ADR ne change que par ses liens, la mention de statut demandée en C-3 peut le signaler.

## Divers vérifiés, sans constat

- Hooks : la ligne « Méthode » désigne le process et les profils du plugin, en chemins absolus déduits du fichier du hook. Elle n'apparaît pas sans fiche, et une copie `process/` du repo n'est jamais désignée (tests l. 241 à 265). Le refus de la garde du coordinateur renvoie au process du plugin. `test_guard_outbound.py` n'a pas été modifié, comme le demande l'étape 4 du plan.
- Scripts : `watch_cards.py` et `maintainer_time.py` suivent l'annexe B du plan (états, épisodes sans fichier d'état, millisecondes entières, dossier des transcripts, sortie sans contenu de message). Leurs docstrings et commentaires expliquent le *pourquoi* ; c'est lisible pour un mainteneur qui ne code pas.
- Repo public : aucun chemin du poste, nom de personne, nom d'hôte ni nom d'un autre projet dans les fichiers nouveaux ou modifiés. Les fixtures utilisent `/work/…` et `/plugin/…` ; RET-017 et l'ADR 0018 parlent d'« un autre projet du poste » sans le nommer.
- Orca : rien n'est repris (plan, §3) ; aucune mention de licence n'est donc attendue.
- Sur-ingénierie : rien hors plan, à part quatre termes ajoutés au glossaire (« Veille des cartes », « Moment », « Note de suivi », « Session libre »). Le profil du rédacteur le veut pour un terme nouveau, donc aucune action n'est demandée.

RELECTURE : CORRECTIONS (3)
