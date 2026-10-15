# Relecture conformité, tour 9 — #23 Process élagué (K1-2)

Relecteur B, axe conformité. Relu : tout le travail non commité de la branche (`git status`, `git diff`, fichiers non suivis), contre le plan validé, AGENTS.md, `docs/specs/` et les ADR 0009, 0012, 0013, 0015, 0016, 0017 et 0018.

**Tests** : `python3 -m unittest`, 186 tests, OK (76,7 s).

## Vérifié sans constat

- Critère de fin : `process/README.md`, `process/fiche-projet.md` et les sept profils sont dans `roles/` ; `docs/process/` ne contient plus que le renvoi `README.md` ; le test de taille (≤ 4904 mots) et le test de généricité (`pnpm`, `/Users/`, `/home/`) passent ; aucun nom d'hôte, de personne ni d'autre projet dans `process/`, `roles/`, `scripts/maintainer_time.py`, ses tests (chemins `/work/…` inventés), `docs/methode.md`, l'ADR 0018 ni la fiche concept.
- Règles du point 3 présentes dans le process et dans le profil qui les applique, avec leur référence : FR-049 (coordinateur, planificateur), FR-050 (relecteur, orchestrateur, coordinateur), FR-051, FR-052, FR-053, FR-054 (recetteur), FR-055 et RET-018 (coordinateur, orchestrateur). Planificateur : niveau au-dessus « motivé (FR-049) ».
- Règle 6 d'`AGENTS.md` cohérente avec FR-052 et FR-053 ; `docs/methode.md` au niveau *léger* ; Q-058 tranchée, cohérente avec le profil de l'orchestrateur de tâche (l. 7), l'ADR 0018 et le glossaire (« Note de suivi »).
- NFR-016 : plus aucun « Origine : … » dans `process/` ni `roles/` ; la table de l'ADR 0018 couvre les nouvelles lignes (niveau *léger*, interdits de l'implémenteur, reprise de session, `--plugin-dir`, « Messages au mainteneur »), sauf l'exception notée au constat 3.
- ADR existantes : 0009, 0012 et 0013 ne changent que par leurs liens ; 0016 et 0017 intactes ; les mentions de statut sont reportées à l'acceptation (ADR 0018, dernière ligne). ADR 0018 « proposée », RET-017 à RET-019 « en application » : voulu.
- Liens : tous les liens vers `process/` et `roles/` hors `docs/plans/` résolvent ; plus aucun lien vers l'ancien `docs/process/roles/`.
- Mesure : le script ne lit que les sessions dont le premier `cwd` (résolu par `realpath`) est le worktree principal, ignore un transcript illisible ou sans `cwd`, accepte `--issue` avec un `#`, et sa limite (feu vert tapé dans le worktree de la tâche non compté) est écrite dans le script, le process, l'ADR 0018, RET-018, FR-055 et la fiche concept. « Le mainteneur valide le chiffre » n'apparaît plus nulle part. Écart à l'issue acté (RET-018, ADR 0018, FR-055).
- Friction 18 : même explication dans `process/README.md` l. 105, `roles/recetteur.md` l. 11, ADR 0018 l. 62 et `docs/methode.md` l. 13 ; Q-064 ouverte et rattachée à Q-055.
- « Messages au mainteneur » : deux phrases, fidèle au retour (note `23-process-elague-retours.md`, §1), citée par le coordinateur, l'orchestrateur, le planificateur et le recetteur.
- Hook de démarrage sur `startup|clear|resume`, testé ; veille : `stateStartedAt` accepté seulement en entier, donc ni `nan` ni `inf`.

## Bloquant

Aucun.

## À corriger

### 1. Le format du numéro d'issue n'est pas celui que lit la mesure

- **Fichiers** : `process/README.md` l. 61 ; `roles/coordinateur.md` l. 21 ; `docs/specs/RETOURS.md`, RET-019, « Règle » ; `docs/decisions/0018-process-elague.md` l. 70.
- **Constat** : la règle demande « la tâche suivie de son numéro d'issue entre parenthèses, que lit la mesure ». Or `maintainer_time.py` (l. 213 à 218) ne rattache un message qu'au nom du worktree ou à `#<n>`, dièse compris. Rien dans la règle n'impose le dièse.
- **Scénario d'échec** : le coordinateur, qui applique la règle et évite le jargon, écrit au mainteneur « jam, Process élagué (issue 23) : la recette est prête, check-list dans … ». Le mainteneur répond « ok ». Ni ce message ni le tour qui le précède ne contiennent `#23` ni `23-process-elague` : le message est compté « hors tâche ». Le temps noté dans la PR est donc sous-estimé, sans avertissement, alors que la règle disait justement servir à la mesure (RET-018, FR-055).
- **Correction attendue** : écrire le format exact là où la règle est écrite : « la tâche suivie de son numéro d'issue entre parenthèses, avec son dièse (`(#23)`), que lit la mesure ». À reporter dans le profil du coordinateur, RET-019 et la ligne de la table de l'ADR 0018.

### 2. Niveau *léger* : un retour reçu dans le worktree échoit au coordinateur, qui ne peut pas l'écrire

- **Fichiers** : `process/README.md` l. 37 ; à mettre en regard de `roles/coordinateur.md` l. 5 et l. 9, et de `hooks/guard_coordinator.py` (`ALLOWED`, l. 77 à 81).
- **Constat** : « Reçu dans un worktree, la session qui conduit la tâche l'analyse dans `docs/plans/<tâche>-retours.md` ». Au niveau *léger*, la session qui conduit la tâche est le coordinateur (process l. 20, FR-052). Or il « n'écrit rien dans le repo » : sa garde ne laisse écrire que la mémoire, le plan de session et les dossiers temporaires. L'ADR 0018 (Q-058) et le glossaire (« Note de suivi ») ne donnent cette écriture qu'à l'orchestrateur de tâche.
- **Scénario d'échec** : une tâche de jam, au niveau *léger*. Le mainteneur recette, comme le prévoit `docs/methode.md`, dans une session ouverte dans le worktree, et y fait une remarque ; c'est ce qui s'est passé pour #23. Le process dit au coordinateur d'écrire `docs/plans/<tâche>-retours.md` dans le worktree. Son `Write` est refusé par `[jam] BLOQUÉ : …`, ou bien, pour respecter sa garde, il garde l'analyse en mémoire ou dans un dossier temporaire, exactement ce que Q-058 voulait éviter (NFR-013).
- **Correction attendue** : dire ce qui se passe au niveau *léger*. Par exemple : « Au niveau *léger*, aucune session ne conduit la tâche dans le worktree : le retour remonte au coordinateur, qui le traite comme s'il l'avait reçu (brief d'un cadrage). » Ou bien confier la note à un rédacteur. Une demi-phrase dans le process suffit ; l'ADR 0018 (Q-058) précise alors le niveau *léger*.

### 3. Conflit avec `main` : celui qui fusionne ne peut pas résoudre, et la règle remplace une règle sans le dire

- **Fichiers** : `process/README.md` l. 33 ; `roles/orchestrateur-tache.md` l. 21 ; `docs/decisions/0018-process-elague.md` l. 60.
- **Constat** :
  - « la session qui conduit la tâche fusionne `main` dans la branche, sans rebase, relance les tests et pousse ». Si la fusion a de vrais conflits, il faut éditer les fichiers en conflit. Or cette session est l'orchestrateur de tâche, qui n'écrit que sa note de suivi (profil l. 7, « ne produit aucun livrable », RET-001), ou, au niveau *léger*, le coordinateur, dont la garde refuse toute écriture dans le repo.
  - La table de l'ADR 0018 classe cette règle « Rien : comblent un trou ». Mais le profil de l'orchestrateur sur `main` disait : « En cas de conflit, la tâche passe en « ⛔ bloqué : conflit avec `main` » et le coordinateur décide avec le mainteneur. » La règle remplace donc une règle existante sans le dire (NFR-016).
- **Scénario d'échec** : deux tâches de jam au niveau *léger* ajoutent chacune une question à la fin de `docs/specs/OPEN-QUESTIONS.md`. La première est mergée ; la seconde est en conflit. Le coordinateur fusionne `main` dans le worktree et obtient des marqueurs de conflit dans `OPEN-QUESTIONS.md`. Pour les retirer, il doit faire un `Edit` : refusé par `[jam] BLOQUÉ`. Au niveau *standard*, l'orchestrateur, lui, n'est arrêté par aucune garde : il édite le fichier, et produit ainsi un livrable que personne ne relit.
- **Correction attendue** :
  - Dans le process (et l. 21 du profil de l'orchestrateur) : « … fusionne `main` dans la branche, sans rebase ; les fichiers en conflit sont résolus par l'implémenteur (le rédacteur pour des docs), relancé avec le conflit dans son brief ; puis les tests sont relancés et la branche poussée sur un nouveau feu vert ». En passant, préciser quel feu vert (recette, ou merge ?).
  - Dans l'ADR 0018 l. 60, colonne « Remplace ou retire » : « En conflit, ⛔ et décision du coordinateur avec le mainteneur (profil de l'orchestrateur de tâche) ».

## Suggestions

1. **Carte et « Messages au mainteneur »** : `process/README.md` l. 61, la règle cite « la carte » parmi les messages qui nomment projet et tâche. Pourtant, les formats de segment de la table (l. 65 à 72), comme `▶ <rôle> en cours`, n'en nomment aucun, et le segment d'état doit rester en tête : `watch_cards.py` ne lit que le premier segment. Un agent qui ferait précéder ce segment du nom de la tâche (« jam, Process élagué (#23) · ⏸ … ») rendrait la carte invisible à la veille. Préciser : « sur la carte, le nom du worktree désigne la tâche ; le segment d'état reste en tête ».
2. **Relais du merge** : `process/README.md` l. 76, « merge d'un projet en production ou dont la fiche le demande, et tout feu vert autre que plan et recette ». Le merge est déjà un feu vert « autre que plan et recette » : la clause sur la fiche ne change rien. Pourtant, le gabarit (`process/fiche-projet.md` l. 13, « et si son feu vert se relaie sous sa forme complète, obligatoire en production ») laisse croire qu'un projet hors production peut s'en passer. Sans effet pratique, puisque le mainteneur confirme toujours dans le terminal du coordinateur. Mais les deux textes se contredisent : retirer la clause sur la fiche dans le process, et « et si son feu vert… » dans le gabarit, ou bien dire que la fiche peut alléger le merge et le reporter dans FR-053.
3. **Interdits** : `process/README.md` l. 106, « Les interdits protègent … la fiche et `docs/plans/` ». L'implémenteur ne protège plus que le plan de la tâche et les rapports de relecture (`roles/implementeur.md` l. 9, ADR 0018 l. 59). Écrire « le plan et les rapports de relecture » plutôt que tout `docs/plans/`.
4. **Fiche concept** : `docs/concepts/veille-et-mesure.md` l. 41, « Un agent bloqué entre la sortie de la veille et son relancement n'est jamais signalé ». Les l. 32 et 40 (et la docstring de `watch_cards.py`) disent qu'il réveille encore une fois quand son attente atteint N minutes, si la carte n'avait pas déjà dépassé N au relancement. Écrire « n'est signalé qu'au bout de N minutes d'attente ».

RELECTURE : CORRECTIONS (3)
