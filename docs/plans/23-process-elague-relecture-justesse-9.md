# Relecture justesse, tour 9 — #23 Process élagué (K1-2)

Relecteur A, axe justesse. Périmètre : tout le travail non commité de la branche (`git status`, `git diff -M`, fichiers non suivis), en priorité les changements depuis le tour 8 ; aucun autre rapport de relecture lu.

**Tests** : `python3 -m unittest` → `Ran 186 tests in 73.851s`, `OK`.

**Vérifié sans constat** :
- `hooks/guard_outbound.py` : l'extraction de `maintainer_words` est une refonte à comportement égal. Chaque `continue` de l'ancienne boucle devient `return None`, et la boucle continue sur `None` ; `test_guard_outbound` passe sans être modifié.
- `hooks/hooks.json` (`startup|clear|resume`), le test qui l'accompagne, et la ligne « Méthode » de `session_start_recap.py` : chemins trouvés depuis le fichier du hook. Un repo avec son propre `process/` n'est pas désigné ; sans fiche, la ligne n'apparaît pas ; une fiche qui est un dossier ne compte pas.
- `scripts/watch_cards.py` : réveil sur un agent bloqué, une fois par `paneKey` et par épisode ; la sortie de `▶` clôt l'épisode ; réveil sur une carte inactive (franchissement, ou première lecture inactive déjà au-delà de N ; seule la lecture de lancement compte comme vue) ; raison gardée quand le commentaire change au même relevé ; `nan`, `inf`, `0`, `-1` et une valeur non numérique refusés avec le code 2. Tests sensibles au temps : une régression les fait échouer de façon sûre, par le nombre de lectures ou la carte réveillée. Un runner trop lent échoue par le délai de 30 s du sous-processus, sans rester bloqué, et les commentaires des tests le disent.
- `scripts/maintainer_time.py` : seules les sessions dont le premier `cwd`, résolu par `realpath`, est `--main` sont lues ; un lien cassé ou un transcript sans `cwd` est ignoré ; les évènements `isSidechain` sont écartés ; un tour s'ouvre sur un message du mainteneur ou sur une notification ; `#23` ne prend pas `#230` ; `--issue #23` est accepté ; la fenêtre sans fuseau est lue en heure locale ; un écart de 10 min pile ouvre un nouveau moment ; aucun contenu de message n'est imprimé (test avec un mot témoin). Je ne trouve pas de code mort laissé par le retrait de la lecture côté tâche.
- Repo public : aucun chemin du poste, nom d'hôte, de personne ou d'un autre projet dans `process/`, `roles/`, `hooks/`, `scripts/`, `docs/methode.md`, l'ADR 0018, la fiche concept, le plan, le rapport de recette et la note de retours. Les `/Users/testhome` et `/Users/x/…` des tests sont des valeurs inventées.
- La phrase « Le mainteneur valide le chiffre » n'apparaît plus nulle part.

## Bloquant

Aucun.

## À corriger

### 1. La mesure ne compte pas la recette du mainteneur, et ses limites écrites ne le disent pas

- **Fichiers** :
  - `scripts/maintainer_time.py:30-32` (docstring, « Limits ») ;
  - `process/README.md:112` ;
  - `docs/concepts/veille-et-mesure.md:43` ;
  - `docs/decisions/0018-process-elague.md:42` ;
  - `docs/specs/RETOURS.md:251`.
- **Constat** : le script ne lit que les sessions démarrées dans le worktree principal. Or la recette du mainteneur se fait dans le worktree de la tâche. La fiche de jam (`docs/methode.md:13`) dit : « Il ouvre, dans un terminal Orca du worktree, une session `claude --plugin-dir <chemin du worktree>` […] par des demandes à cette session ». La check-list de #23 dit de même (`docs/plans/23-process-elague-recette.md:16` : « une session neuve `claude --plugin-dir <worktree>`, ouverte dans un terminal Orca du worktree `23-process-elague` »). Ces demandes sont bien les mots du mainteneur, mais aucune n'est lue. Les cinq endroits ci-dessus ne nomment qu'une limite plus étroite : « un feu vert tapé directement dans le worktree de la tâche n'est pas compté ».
- **Scénario d'échec** : sur une tâche de jam (niveau *léger*, où le mainteneur est seul à recetter), le mainteneur passe 25 min sur les cinq points de sa check-list, dans des sessions `--plugin-dir` du worktree de la tâche. Il y passe aussi 6 min en deux moments dans la session du coordinateur. Le corps de la PR annonce « 6 min », avec pour seule limite écrite « un feu vert tapé dans le worktree n'est pas compté ». Le lecteur de la PR, et plus tard la page publique (FR-056), croit la recette incluse. Le chiffre sous-estime donc d'un facteur 5 l'unique mesure de la méthode (FR-055), sans que rien ne le signale.
- **Correction attendue** : au minimum, écrire la limite exacte aux cinq endroits, par exemple : « la recette du mainteneur, faite dans une session du worktree de la tâche, n'est pas comptée, ni un feu vert tapé là ». Écrire aussi dans le rapport du script qu'il ne contient pas le temps de recette. Je ne recommande pas de relire les sessions de la tâche : la décision du mainteneur l'exclut pour une bonne raison, les relais d'agents. Si le mainteneur veut ce temps, c'est une décision pour lui, à remonter par le coordinateur (nouvelle question ouverte) : par exemple, noter dans la check-list l'heure de début et de fin de la recette. Ce n'est pas à trancher dans cette relecture.

### 2. Un agent bloqué peut être compté « au travail » : le second réveil, « depuis N min », ne vient jamais

- **Fichiers** :
  - `scripts/watch_cards.py:125-126` (`at_work`) ;
  - la docstring en `scripts/watch_cards.py:35-37` ;
  - `docs/concepts/veille-et-mesure.md:32`.
- **Constat** : `blocked_panes` tient pour bloqué un agent dont `state` **ou** `mainAgent.state` vaut `waiting`. `at_work` le tient pour au travail si l'un des deux vaut `working`. Un agent `{"state": "working", "mainAgent": {"state": "waiting"}}`, forme que `test_wakes_on_blocked_agent` (cas « mainAgent ») traite comme réelle, est donc à la fois bloqué et au travail. `idle_age_now` renvoie `None`, et le réveil « agent en attente d'une autorisation depuis N min » ne se déclenche jamais. La docstring affirme le contraire (« A blocked agent leaves no one at work either: still blocked N minutes into its wait, it wakes again »), et la fiche concept aussi.
- **Scénario d'échec** : sur une carte `▶`, l'orchestrateur reste sur une invite et Orca le rend sous cette forme. Premier réveil, puis la veille est relancée et le coordinateur prévient le mainteneur, qui est absent. 10, puis 30 min plus tard, toujours rien : le rappel promis par la docstring et la fiche concept ne vient pas. Avec `state` à `waiting` et `mainAgent.state` à `working`, même défaut.
- **Correction attendue** : dans `at_work`, un agent en attente n'est pas au travail :
  ```python
  def at_work(agent):
      if "waiting" in states(agent):
          return False
      return "working" in states(agent) or agent.get("workingMode") == "monitoring"
  ```
  Ajouter un sous-cas `mainAgent` à `test_agent_still_blocked_after_threshold_is_named_so`, avec `agent("working", main_state="waiting")`. Il doit réveiller avec `agent en attente d'une autorisation depuis 0.05 min`. L'âge reste juste : `started_at` prend le plus récent des deux `stateStartedAt`, donc le début de l'attente.

## Suggestions

1. `scripts/maintainer_time.py:247` : « N session(s) du coordinateur lue(s) » compte toute session démarrée dans le worktree principal, y compris une session libre ouverte par le mainteneur. Écrire « session(s) du worktree principal lue(s) », ou dire dans la docstring que toute session de `main` est tenue pour celle du coordinateur.
2. `scripts/maintainer_time.py:213` : si le nom du dossier de `--worktree` est vide (`--worktree /`) ou trop commun (le chemin du worktree principal passé par erreur, nom `jam`), la regex prend presque tout, et un chiffre gonflé sort avec le code 0. Refuser, avec le code 2, un `--worktree` dont le `realpath` égale celui de `--main` ou dont le nom est vide.
3. `scripts/watch_cards.py:246-249` : une valeur finie mais démesurée passe le contrôle. `--idle-minutes 1e308` donne `idle_seconds = inf`, et la carte ne réveille jamais. `--interval 1e308` lève `OverflowError` dans `time.sleep`, d'où une trace Python et le code 1. Borner les deux valeurs (par exemple 1440 min et 3600 s), ou attraper `OverflowError`.
4. `scripts/watch_cards.py:122` : un agent sans `paneKey` est noté `"None"`. Deux agents sans `paneKey` se confondent, et le second qui se bloque ne réveille pas. Sans conséquence tant qu'Orca donne toujours le champ ; au besoin, se rabattre sur la position de l'agent dans la liste.
5. Tests, cas limites non couverts :
   - `timestamp` (`maintainer_time.py:74`) : un horodatage de transcript sans fuseau, lu en UTC ;
   - `agents` (`watch_cards.py:110-112`) : un champ `agents` qui n'est pas une liste, ou des lignes qui ne sont pas des objets ;
   - `started_at` : des millisecondes en flottant.
   Chacun tient en quelques lignes.
6. `process/README.md:106` : « Les interdits protègent […] la fiche et `docs/plans/` ». Or l'implémenteur n'a plus pour interdit que le plan et les rapports de relecture (`roles/implementeur.md:9`, ADR 0018 ligne 59), pour pouvoir écrire la check-list au niveau *léger*. Écrire « la fiche, le plan et les rapports de relecture ».
7. `roles/recetteur.md:21` garde « cinq points au plus », alors que l'ADR 0018 (ligne 68) présente la nouvelle règle comme remplaçant « Une check-list de 5 étapes au plus ». Il faut soit retirer le plafond du profil, soit écrire dans l'ADR que la règle reformule la check-list en gardant son plafond.
8. `docs/specs/RETOURS.md:246` : « le coordinateur l'ajoute à la PR ». Au niveau *standard*, c'est l'orchestrateur de tâche qui ouvre la PR et y note le temps (`roles/orchestrateur-tache.md:21`). Écrire « la session qui ouvre la PR ».

RELECTURE : CORRECTIONS (2)
