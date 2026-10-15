# Relecture #23, axe justesse, tour 5

Périmètre : tout le travail non commité de la branche (`git status`, `git diff -M`), dont les fichiers non suivis. `python3 -m unittest` : 184 tests, OK (71 s en local).

Vérifié sans constat :
- la refonte de `hooks/guard_outbound.py` ne change pas le comportement. `maintainer_words` renvoie `None` là où l'ancienne boucle faisait `continue`, et `""` pour un `/` sans argument comme avant. `hooks/test_guard_outbound.py` n'a pas changé et reste vert ;
- le hook de reprise désigne le process et les profils depuis son propre fichier. Les cas « copie `process/` dans le repo », « pas de fiche » et « fiche qui est un dossier » sont testés ;
- dans `watch_cards.py`, les tests de temps ne dépendent pas de la vitesse du runner, sauf `test_wakes_on_idle_card` et `test_agent_still_blocked_after_threshold_is_named_so`. Ces deux-là ont 3 s de marge pour la première lecture. Si la marge est dépassée, le test échoue par `TimeoutExpired` au bout de 30 s : il ne passe pas à tort ;
- `test_plugin.py` : le plafond est vérifié, la liste des fichiers comptés est fermée et les interdits sont testés.

## Bloquant

Aucun.

## À corriger

1. **`scripts/maintainer_time.py:205-226` (`coordinator_turns`)** : le « tour » qui sert au rattachement n'est remis à zéro que sur un message du mainteneur. Il accumule donc tous les textes du coordinateur, y compris ceux des tours ouverts par une notification de tâche de fond, comme le réveil de la veille (un évènement `user` avec `<task-notification>`, pour lequel `maintainer_words` renvoie `None`). Le plan (annexe B) rattache un message si « la dernière réponse du coordinateur avant lui » nomme la tâche. Or une notification ouvre un nouveau tour de l'agent.
   **Scénario d'échec** (session du coordinateur) :
   - 09:00, le mainteneur : « lance #24 » ;
   - 10:00, la veille réveille le coordinateur (notification), qui répond « 24-x attend ton feu vert plan. » ; le mainteneur ne répond pas, la veille est relancée ;
   - 11:00, nouvelle notification ; le coordinateur répond « 23-y attend ton feu vert recette. » ;
   - 11:02, le mainteneur : « ok ».

   `maintainer_time.py --worktree …/24-x --issue 24` compte ce « ok » pour #24 : un moment de 3 min en trop, alors que la dernière réponse ne nomme que #23. Ce n'est pas la limite écrite (« un ok qui suit un résumé de plusieurs tâches ») : ici, aucune réponse ne résume plusieurs tâches. Avec un coordinateur qui tourne des heures sur des réveils, cela arrive à presque chaque « ok ».
   **Correction attendue** : remettre `turn` à zéro sur tout évènement `user` qui ouvre un tour sans être un message du mainteneur. Au minimum : une notification de tâche de fond, c'est-à-dire un contenu avec `<task-notification` ou `SYSTEM NOTIFICATION`. Les `tool_result`, qui sont dans le tour, ne remettent pas à zéro. Ajouter le test du scénario ci-dessus : le « ok » est retenu pour #23 et compté « hors tâche » pour #24.

## Suggestions

1. **`scripts/maintainer_time.py:175-191` (`relayed`)** : un relais du coordinateur vers une **autre** tâche peut prendre un message identique du mainteneur dans la tâche mesurée. Par exemple, « ok » est relayé à 10:00 vers l'orchestrateur de #24, puis à 10:05 le mainteneur tape « ok » dans le terminal de #23 : ce « ok » est écarté comme relais pour #23. Le plan (annexe B, point 4) est encore plus large, la règle suit donc le plan validé. Écrire cette limite dans la docstring (« Limits ») et dans la PR.
2. **`scripts/maintainer_time.py:164-171` (`relay_sends`)** :
   - pour chaque `terminal send`, `rest` va jusqu'à la fin de la ligne : `orca terminal send --text a && orca terminal send --text b` relève `b` deux fois, et un second message `b` du mainteneur peut être écarté. Couper `rest` au prochain `terminal`, ou au prochain `&&`, `;`, `|` ;
   - la forme `--text=…` n'a pas de test (un cas limite par fonction exposée).
3. **`scripts/maintainer_time.py:75-85` (`window_bound`)** : `--until 2026-10-12` se lit comme minuit au début de ce jour, et la journée nommée est exclue sans avertissement. Documenter dans l'aide qu'une date sans heure vaut 00:00, ou lire une date seule en `--until` comme la fin du jour.
4. **`scripts/maintainer_time.py:254-256`** : `--issue "#23"` donne le motif `##23`, qui ne trouve rien, et tous les messages du coordinateur passent « hors tâche » sans erreur. Retirer un `#` initial.
5. **`scripts/maintainer_time.py:108`** : un transcript illisible (`PermissionError`) fait planter le script avec une trace Python, sans préfixe `[jam]`. Sauter le fichier, ou finir en code 2 avec un message `[jam]`.
6. **`scripts/watch_cards.py:176-178`** : la règle « quitter ▶ clôt les deux épisodes » n'a pas de test. Cas à ajouter : un agent bloqué au lancement, la carte passe en ⏸ (réveil), puis la veille est relancée, la carte revient en ▶ avec le même agent bloqué, et elle réveille.
7. **`scripts/watch_cards.py:117`** : `str(agent.get("paneKey"))` réunit sous `"None"` deux agents sans `paneKey`, et le second blocage ne réveille pas. Si Orca garantit le champ, rien à faire ; sinon, prendre une clé de repli (`displayName`, ou l'indice).
8. **`process/README.md:77`** : « Un seul réveil par épisode ». Or un agent bloqué réveille deux fois : à l'entrée en `waiting`, puis N min plus tard, avec la mention « depuis N min », comme le dit la docstring de `watch_cards.py`. Préciser la phrase, pour que le coordinateur ne prenne pas le second réveil pour une anomalie.

RELECTURE : CORRECTIONS (1)
