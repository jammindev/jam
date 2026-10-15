# Relecture, axe justesse, tour 8 : process élagué (#23)

Relu : tout le travail non commité de la branche (`git status`, `git diff -M`, fichiers non suivis), d'abord les changements faits depuis la recette refusée. `python3 -m unittest` : 184 tests, OK (72 s).

## Bloquant

Aucun.

## À corriger

### C1. La règle « Messages au mainteneur » permet de retirer ce que la mesure lit

- **Fichiers** : `process/README.md:59` (« le numéro au plus entre parenthèses »), repris par `docs/specs/RETOURS.md:264` et `roles/coordinateur.md:21` ; face à `scripts/maintainer_time.py:212-217` et `process/README.md:110` (« Un message compte s'il nomme la tâche »).
- **Défaut** : le script ne rattache un message à la tâche que par `#<n>` ou par le nom du dossier du worktree (`23-process-elague`). La nouvelle règle demande au coordinateur de nommer la tâche **en mots**, avec le numéro **au plus** entre parenthèses, donc facultatif. Un coordinateur qui suit la règle à la lettre écrit des messages que la mesure ne voit plus. Le process ne dit nulle part que « nommer la tâche », pour la mesure, veut dire `#<n>` ou le nom du worktree.
- **Scénario d'échec** : le coordinateur, réveillé par la veille, écrit « Projet jam, tâche process élagué : la recette attend ton feu vert. » Le mainteneur répond « ok ». Ni le message ni le tour ne contiennent `#23` ou `23-process-elague` : le script compte le message dans « hors tâche ». Si tous les messages du coordinateur suivent la règle, le corps de la PR donne « 0 min en 0 moment(s) » avec « 1 session(s) du coordinateur lue(s) ». Aucun avertissement : le compteur de sessions, qui doit trahir un mauvais chemin, ne trahit pas ce cas. Cela fausse l'unique mesure de la méthode (FR-055, RET-018).
- **Correction attendue** (recommandée) : dans `process/README.md:59`, garder obligatoirement le numéro quand un message nomme une tâche, par exemple « … la tâche en mots, suivie de son numéro d'issue entre parenthèses, que lit la mesure du temps ». Préciser aussi dans « Mesure » (ligne 110) que « nommer la tâche » veut dire `#<n>` ou le nom du worktree. Aligner `roles/coordinateur.md:21` sur ce texte. Si le mainteneur tient au « au plus » de RET-019, écrire au moins la limite là où les autres sont écrites : docstring du script (l. 30-32), « Mesure » du process, `docs/concepts/veille-et-mesure.md:43` et RET-018.

## Suggestions

- **S1** `scripts/maintainer_time.py:134-137` et `:279` : le `cwd` du transcript est comparé à `abspath(--main)` sans résoudre les liens symboliques. Si `--main` est donné par un chemin qui passe par un lien, alors que Claude Code note le chemin physique, aucune session n'est lue. Le « 0 session(s) lue(s) » le montre, donc ce n'est pas silencieux. `os.path.realpath` des deux côtés éviterait l'erreur.
- **S2** `scripts/maintainer_time.py:117-119` : les évènements ne sont pas dédoublonnés. Si une reprise de session recopie l'historique dans un nouveau fichier (je n'ai pas vérifié le format), les messages sont comptés deux fois. Le temps ne change pas, car les horodatages sont identiques et tombent dans le même moment. Les comptes « message(s) retenu(s) » et « Écartés » doublent. Dédoublonner par `uuid` coûte une ligne.
- **S3** `scripts/maintainer_time.py:264-273` : `--until 2026-10-13` sans heure vaut minuit au début du 13, donc toute la journée du 13 est exclue. Une fenêtre inversée (`--since` après `--until`) passe aussi sans erreur et met tout en « hors fenêtre ». À refuser, ou à écrire dans l'aide de l'option.
- **S4** `scripts/maintainer_time.py:110-116` : seul `OSError` est rattrapé. Un bloc `{"type": "text", "text": null}` fait planter `"\n".join` (dans `maintainer_words` et `answer_text`) avec une trace Python. Improbable avec les transcripts réels.
- **S5** `scripts/watch_cards.py:241-244` : `nan` et `inf` passent le contrôle `<= 0`. Avec `--idle-minutes nan`, le réveil d'inactivité n'a jamais lieu (`age >= nan` est toujours faux). Avec `--interval nan`, `time.sleep` plante avec une trace. Utiliser `math.isfinite`.
- **S6** `scripts/watch_cards.py:117-123` : Orca a un quatrième état, `blocked` (`docs/references/orca.md:207`). Il ne compte ni comme travail ni comme attente d'autorisation, donc un agent `blocked` produit, après N minutes, un réveil « aucun agent au travail », et le coordinateur relance l'orchestrateur. Le sens de cet état n'est pas établi. À écrire dans la docstring comme un choix, ou à relever dans le prochain relevé réel.
- **S7** `docs/concepts/veille-et-mesure.md:40` : « un agent toujours bloqué ne réveille plus » contredit la ligne 32 et le script : un agent encore `waiting` réveille une seconde fois N minutes après le début de son attente. Reformulation proposée : « ne réveille plus comme nouvel agent bloqué, mais une fois encore si son attente atteint N minutes ».

## Vérifié sans constat

- **Veille** :
  - réveil sur un agent `waiting` (`state` ou `mainAgent.state`), par agent (`paneKey`) ;
  - réveil d'inactivité au franchissement de N, ou tout de suite à la première lecture inactive si l'âge dépasse déjà N, sauf à la lecture de lancement ;
  - carte sans agent ou sans date lisible (ISO, booléen, champ absent) datée par l'horloge du script ;
  - « agent en attente d'une autorisation depuis N min » quand l'agent est toujours bloqué ;
  - raison de l'agent gardée quand le commentaire change au même relevé ;
  - cartes `main`, `completed`, `⏸`, `⛔` et sans segment d'état exclues ;
  - un épisode recommence après la sortie de `▶` ;
  - `--idle-minutes` à 0, négatif ou non numérique refusé avec le préfixe `[jam]`.
- **Tests de la veille** :
  - le faux `orca` répète sa dernière réponse, et le `sleep` passe avant la sortie, donc l'heure lue par le script est postérieure ;
  - les cas à horloge de script (0,6 s) ne dépendent pas du démarrage des interpréteurs ;
  - les deux cas datés à 3 s (`test_wakes_on_idle_card`, `test_agent_still_blocked_after_threshold_is_named_so`) supposent que la première lecture arrive moins de 3 s après la construction du relevé. Sur un runner trop lent, le script ne se réveille pas et le test échoue par dépassement du délai de 30 s : il ne passe jamais à tort ;
  - les cas « pas de réveil » échouent bien si la règle régresse (vérifié en raisonnant sur les lectures 2 à 4).
- **Mesure** :
  - seules les sessions dont le premier `cwd` est le worktree principal sont lues ; un transcript étranger est écarté dès son premier `cwd` ;
  - un lien cassé, un transcript sans `cwd` ou une ligne illisible est ignoré sans plantage ;
  - les messages `isMeta`, `isCompactSummary`, `isSidechain`, les résultats d'outil, les commandes `!` et les notifications sont écartés ;
  - une notification ouvre un tour, tout le tour du coordinateur sert au rattachement, `#230` ne compte pas pour `#23`, et `--issue #23` est accepté ;
  - un écart d'exactement 10 min ouvre un nouveau moment ;
  - fenêtre sans fuseau en heure locale ;
  - dossier des transcripts par `--transcripts`, `CLAUDE_CONFIG_DIR` ou `HOME` ;
  - aucune sortie de contenu (témoin `ZORGLUB` absent de stdout et stderr) ;
  - aucun code mort laissé par le retrait de la lecture côté tâche : `--worktree` ne sert plus qu'au nom.
- **`hooks/guard_outbound.py`** : l'extraction de `maintainer_words` est fidèle ; les `continue` sont devenus des `return None` à l'identique, dans le même ordre de filtres.
- **Hook de reprise** : la ligne « Méthode » n'apparaît que si `docs/methode.md` est un fichier. Elle est cherchée à la racine du repo, et ses chemins sont ceux du plugin, jamais les copies `process/` ou `docs/process/` du repo.
- **`hooks/test_plugin.py`** :
  - plafond de 4904 mots sur les neuf pages, avec un test qui fait échouer la suite si une page n'est pas comptée ;
  - fichiers parasites ignorés ;
  - interdits sans affichage du fichier entier en cas d'échec.
- **Repo public** : aucun chemin du poste, nom de personne, d'hôte ou d'autre projet dans `process/`, `roles/`, `hooks/` ni `scripts/`.

RELECTURE : CORRECTIONS (1)
