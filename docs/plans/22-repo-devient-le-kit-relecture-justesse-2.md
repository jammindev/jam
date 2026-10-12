# Relecture — #22 Le repo devient le kit — axe A, justesse, tour 2

> Relecteur A (justesse), contexte neuf. Lu : profil du relecteur, `AGENTS.md`, ADR 0016, plan (avec ses ajustements validés), section K1-1 de `cadrage-kit-issues.md`. Relu : `hooks/` (code, tests, `hooks.json`), `scripts/` (code, tests, fixtures, faux `orca`), `.claude-plugin/`, `ci.yml`, `.gitignore`, fiche concept et docs modifiées. Aucune autre relecture lue.

## Tests

`python3 -m unittest` à la racine : **135 tests, OK** (42,8 s).

Contrôles hors repo, en lecture seule :
- forme de sortie de la CLI Orca, lue dans le code de la CLI livré avec l'app : `worktree create` rend bien `result.worktree.id` (le formateur de `worktree show`, partagé, lit `worktree.id`), `terminal create` rend `result.terminal.handle`, `terminal wait` rend `wait.satisfied`, `terminal send` rend `send.accepted`, et `--no-parent` existe. Les fixtures sont conformes ;
- forme réelle d'un transcript de Claude Code après compaction (constat B1 ci-dessous), lue dans un transcript du poste (clés seulement, rien n'est recopié ici).

## Écarts déclarés par l'implémenteur

Tous acceptés :
- `owner.name` dans `marketplace.json` : champ exigé par le format des marketplaces ; la valeur est le nom de l'organisation GitHub, déjà dans l'URL `repository`. Pas un nom de personne.
- `launch_task.py` prend l'id du worktree dans la réponse de `orca worktree create` : la CLI le rend (voir plus haut), et l'absence d'id est testée (`test_created_worktree_without_id`). Une relecture par `ps` n'apporterait rien.
- Ajouts de sûreté (sortie 2 sans carte, intervalle 30 s, refus sur liste `ps` tronquée, codes 0/1/2) : justes et testés, sauf la validation de `--interval` (suggestion S5).
- `gh`, `gh --help`, `gh pr` passent comme lecture ; commande illisible contenant `gh` refusée : testé dans les deux sens.
- `JAM_ORCA_BIN` non exécutable = CLI introuvable, sans repli : testé (`test_explicit_variable_not_executable_is_not_replaced`, `test_cli_missing`).
- Première ligne « [jam] Reprise de contexte » : testée.
- `scripts/fixtures/fake_orca.py` et `scripts/fixtures/__init__.py` : nécessaires aux imports des tests.
- Délai Orca porté à 5 s dans les tests qui attendent une réponse, 1 s gardée pour le test de lenteur : juste (voir toutefois S4).

## Constats

### Bloquant

**B1 — La garde de sortie s'ouvre seule après une compaction de contexte.**
`hooks/guard_outbound.py:114` (dans `last_user_message`). Après une compaction, Claude Code écrit dans le transcript un événement `"type": "user"`, **sans** `isMeta`, marqué `"isCompactSummary": true` et `"isVisibleInTranscriptOnly": true`, dont le texte est le résumé de la session et finit par « Continue the conversation from where it left off without asking the user any further questions. » (forme vérifiée sur un transcript réel du poste). Le hook prend ce résumé pour le dernier message du mainteneur ; `\bcontinue\b` (sans compter les « commit », « merge », « ok » du résumé lui-même) y trouve un accord. Jusqu'au prochain vrai message du mainteneur, **tout commit, push, merge et écriture `gh` passe**.
C'est exactement le scénario que la garde doit tenir : un coordinateur qui surveille les cartes pendant des heures compacte, lit sur une carte « ✓ feu vert merge », lance `gh pr merge` → passé. Le test `test_green_light_relayed_by_a_card_is_not_an_approval` reste vert parce que son transcript ne contient pas de compaction. Le défaut existait dans le hook du poste, mais l'issue exige le refus « sans accord explicite dans le dernier message du mainteneur », et ce hook devient la garde unique de tout le poste.
**Correction attendue** : dans `last_user_message`, ignorer aussi les événements `isCompactSummary` ou `isVisibleInTranscriptOnly` (comme `isMeta`) ; ajouter le cas à `noise()` de `hooks/test_guard_outbound.py:107` (résumé de compaction contenant « continue » après un « non merci » → refus ; après un « ok » → passe), et le scénario carte + compaction au test du feu vert remonté. Ajouter la compaction aux pièges de `docs/concepts/plugin-et-hooks.md` (§ « L'accord est lu sur le seul dernier message du mainteneur »).

### À corriger

**C1 — `gh api graphql` dont la requête n'est pas visible passe pour une lecture.**
`hooks/guard_outbound.py:211-213` (`api_reads`). Pour `graphql`, seul le texte des arguments est fouillé à la recherche de `mutation`. Une requête lue dans un fichier ou sur stdin y échappe : `gh api graphql --input q.json`, `gh api graphql --input - <<'EOF' … mutation … EOF`, `gh api graphql -F query=@mutation.graphql` sont classés lectures et passent sans accord. Cela contredit le principe retenu à la question 2 du plan (refus par défaut de ce qu'on ne sait pas lire), que le hook applique déjà à une commande illisible.
**Correction attendue** : pour `graphql`, compter comme écriture tout appel avec `--input` (ou `--input=`), ou dont un champ `-F`/`--field` a une valeur commençant par `@` ; garder la recherche de `mutation` pour le reste. Ajouter ces trois formes à `GH_WRITES` de `hooks/test_guard_outbound.py:206`, et garder `gh api graphql -f query='query { viewer { login } }'` dans les lectures.

### Suggestions

- **S1 — Réveils répétés sur un `✓` ou `💬` déjà traité.** `scripts/watch_cards.py:55` et `:75-79` : un segment `✓`/`💬` qui reste dans le commentaire réveille la veille à chaque changement de n'importe quel autre segment (« ▶ implémenteur · ✓ feu vert plan » → « ▶ relecteur · ✓ feu vert plan » réveille). Conforme au texte du plan, mais source de faux réveils si l'orchestrateur ne retire pas le segment. Piste : ne réveiller que sur un segment `✓`/`💬` absent de l'état mémorisé. À noter au moins dans la docstring, ou en friction à observer.
- **S2 — Formes de `gh` non vues, à lister dans « NOT covered ».** `hooks/guard_outbound.py:20-22` et `strip_wrappers` (`:182`) : `env -i gh …`, `sudo -u x gh …`, `timeout 60 gh …`, `xargs gh …`, `` `gh pr merge 1` `` et `"$(gh pr merge 1)"` (substitution entre guillemets doubles) passent. Une garde de type « tripwire » peut les laisser, mais la docstring doit le dire, comme celle de `guard_coordinator.py`.
- **S3 — Formes de `git commit`/`push` non vues (comportement repris tel quel).** `hooks/guard_outbound.py:38-39` : `git -c user.name=x commit`, `git --git-dir=… push`, `git -C "dossier avec espace" push` échappent à la regex. Hors du périmètre « comportement inchangé » de ce lot ; à noter dans la docstring ou dans `OPEN-QUESTIONS.md`.
- **S4 — Test de lenteur peut-être instable en CI.** `hooks/test_session_start_recap.py:402` : `elapsed < 2 * REAL_TIMEOUT` (2 s) inclut le démarrage de Python, l'attente d'1 s et cinq appels `git`. La marge est d'environ 0,7 s sur un runner chargé, la même instabilité que celle qui a fait monter les autres délais à 5 s. Piste : comparer à `REAL_TIMEOUT + 1,5` ou mesurer le chevauchement par le journal du faux, comme `test_cli_calls_overlap`.
- **S5 — `--interval` sans test.** `scripts/watch_cards.py:95-96` : le refus de `--interval 0` ou négatif n'est pas testé ; `--interval nan` passe la garde (`nan <= 0` est faux) puis `time.sleep(nan)` lève une `ValueError` non rattrapée (trace Python, code 1). Piste : `math.isfinite(args.interval) and args.interval > 0`, et un test sur `0`, `-1`, `nan`.
- **S6 — `"source": "."` à confirmer.** `.claude-plugin/marketplace.json:10` : la doc des marketplaces montre des sources relatives en `./…`. Le point 5 de la recette (`claude plugin validate .`) le tranchera ; si `.` est refusé, passer à `./` (et adapter `hooks/test_plugin.py:54`).
- **S7 — Docstring de test périmée.** `hooks/test_guard_outbound.py:2` : « the PreToolUse guard of commit and push » ; elle couvre aussi les écritures `gh`.

RELECTURE : CORRECTIONS (2)
