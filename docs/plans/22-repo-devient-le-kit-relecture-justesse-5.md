# Relecture — #22 Le repo devient le kit — axe A, justesse, tour 5

Relecteur A (justesse), contexte neuf. Lus : profil du relecteur, `AGENTS.md`, plan validé avec ses ajustements, et tout le diff hors plan. Côté code : `hooks/` (quatre hooks, `hooks.json`, cinq fichiers de tests), `scripts/` (`orca_cli.py`, `watch_cards.py`, `launch_task.py`, leurs tests, `fixtures/fake_orca.py`, `fixtures/orca/*.json`), `.claude-plugin/`. Côté config : `ci.yml`, `.gitignore`. Côté docs : `README.md`, `AGENTS.md`, fiches concept, `02-ARCHITECTURE.md`, `OPEN-QUESTIONS.md`.

**Tests** : `python3 -m unittest` → `Ran 135 tests in 41.729s — OK`.

**Écarts déclarés par l'implémenteur** : jugés recevables. Le `owner.name` exigé dans `marketplace.json`, l'id pris dans la réponse de `orca worktree create`, les ajouts de sûreté, le traitement des formes `gh`, la jonction des lignes continuées, l'exclusion des résumés de compaction, `JAM_ORCA_BIN` sans repli, la première ligne `[jam] Reprise de contexte`, les fichiers `fake_orca.py` et `__init__.py` ajoutés, le délai de 5 s dans les tests : chacun est cohérent avec le code et couvert par un test. Un seul de ces ajouts appelle une remarque, le refus de `launch_task` sur une liste tronquée : `watch_cards` ne fait pas de même (constat 1).

## Bloquant

Aucun.

## À corriger

1. **`scripts/watch_cards.py:35-41` : une liste `orca worktree ps` tronquée est ignorée.** `project_cards` ne lit pas `result["truncated"]`, que le contrat versionné (`fixtures/orca/worktree-ps.json:50`) prévoit et que `launch_task.py:87` traite comme un refus. Scénario : la liste est tronquée et une carte du projet n'y figure pas. Son passage à `⏸` ne réveille jamais le coordinateur, qui attend sans fin. C'est la panne que `test_unknown_project` dit vouloir éviter (« A typo must not leave the coordinator waiting forever on nothing »). Si toutes les cartes du projet sont au-delà de la coupe, le message devient « aucune carte pour le projet », une cause fausse. Correction attendue : dans `project_cards`, lever `OrcaError` quand `truncated` est vrai (sortie en 2, message `[jam]` « liste des worktrees tronquée »), au lancement comme pendant la veille. Test : `ps()` avec `truncated: true`, au premier appel puis à un appel suivant → code 2, stderr qui commence par `[jam]`, stdout vide. Mentionner le cas dans la docstring (codes de sortie).

2. **`scripts/launch_task.py:130-135` : un brief qui n'est pas en UTF-8 sort en 1 avec une trace Python.** `fh.read()` lève alors `UnicodeDecodeError` (un `ValueError`, pas un `OSError`). L'erreur n'est pas rattrapée : traceback et code 1. Or la docstring réserve 1 au « refus voulu » (plafond, liste tronquée) et promet 2 pour un « brief illisible ». Un appelant qui lit le code croirait à un plafond atteint et attendrait qu'un agent finisse. Correction attendue : rattraper `(OSError, UnicodeDecodeError)` (ou `ValueError`) et sortir en 2 avec un message `[jam]` (attention : `strerror` n'existe pas sur `UnicodeDecodeError`). Test : un brief écrit en octets Latin-1 (`"é".encode("latin-1")`) → code 2, stderr `[jam]`, aucun appel au faux `orca`.

## Suggestions

3. **`hooks/guard_outbound.py:191-196` : `xargs` (et `find -exec`) devant `gh`.** `gh issue list --json number --jq '.[].number' | xargs -n1 gh issue close` passe : `xargs` n'est pas dans `WRAPPERS`, la commande n'est donc pas lue comme un `gh`. C'est une forme plausible pour une opération en lot, et `guard_coordinator` sait déjà la traiter. Même famille : `env -i gh …`, `sudo -u x gh …` (l'option du wrapper arrête `strip_wrappers`). Correction proposée : traiter `xargs` et `find … -exec` comme dans `guard_coordinator.py`, ou au moins citer ces formes dans le « NOT covered » de la docstring.

4. **`hooks/guard_outbound.py:231-234` : requête GraphQL hors de vue sans `--input` ni `@`.** `Q='mutation{…}'; gh api graphql -f query="$Q"` et `gh api graphql -f query="$(cat m.graphql)"` passent pour des lectures. La mutation est dans une autre commande ou dans un fichier, et le texte lu ne contient pas « mutation ». Correction proposée : compter comme cachée une valeur de champ GraphQL qui contient `$` ou un accent grave, ou citer le cas dans la docstring à côté de « query in sight ».

5. **`hooks/guard_outbound.py:42-43` : formes `git` non vues (comportement repris du poste).** `git -c core.hooksPath=/dev/null commit`, `git --no-pager push` et `git -C "dossier avec espace" push` échappent aux regex, qui n'admettent que `-C <mot>`. Hors périmètre du plan (« comportements inchangés »). À citer dans la docstring, ou à élargir plus tard (`(?:-[cC]\s+\S+\s+|--\S+\s+)*`, avec un `-C` entre guillemets).

6. **`hooks/guard_outbound.py:92-165` : la sortie d'une commande `!` du mainteneur compte comme son message (repris du poste).** Les événements `<bash-input>` et `<bash-stdout>` d'une commande lancée par le mainteneur avec `!` (et la sortie d'une commande locale `/…`) ne sont pas écartés. Une sortie qui contient « OK » (celle de `python3 -m unittest`, par exemple) vaut accord jusqu'au message suivant. C'est voisin de la limite déjà notée pour `orca terminal send` (question 3) : à ajouter à la liste des pièges de la fiche concept, ou à écarter comme les notifications.

7. **`hooks/git_context.py:68-71` : faux « (worktree secondaire) » quand le `cwd` passe par un lien symbolique (repris du poste).** `--absolute-git-dir` renvoie le chemin résolu, alors que `--git-common-dir` est relatif et joint au `cwd` non résolu (`/tmp/…` contre `/private/tmp/…`). Le test contourne le cas par `os.path.realpath` (`test_git_context.py:26-28`), sans le couvrir. Correction proposée : comparer des `os.path.realpath`, et ajouter un test avec le `cwd` non résolu.

8. **`hooks/test_session_start_recap.py:402` : seuil serré.** `assertLess(self.elapsed, 2 * REAL_TIMEOUT)` laisse environ 0,8 s pour le démarrage de Python, cinq appels `git` et l'arrêt du faux CLI. Sur un runner chargé, le test peut échouer au hasard. Le test vise à prouver le parallélisme, et `test_cli_calls_overlap` le prouve déjà sans dépendre de l'horloge : un seuil à `2 * REAL_TIMEOUT + 1` suffirait.

9. **`scripts/watch_cards.py:95` : `--interval nan` passe la garde `<= 0`** puis lève une trace dans `time.sleep`, et `--interval inf` ne se réveille jamais. Cosmétique : `math.isfinite(args.interval)` dans la même garde.

RELECTURE : CORRECTIONS (2)
