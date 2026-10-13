# Relecture A, justesse, tour 1 : #22 Le repo devient le kit

> Relecteur A (axe justesse), contexte neuf. Périmètre : tout le diff non commité (suppressions de l'app, `hooks/`, `scripts/`, `.claude-plugin/`, CI, `.gitignore`, docs), le plan exclu. Référence : plan validé, ajustements a à c compris, et section K1-1 de `cadrage-kit-issues.md`.

## Tests lancés

`python3 -m unittest` depuis la racine : **133 tests, OK** (45,6 s). `git status` : suppressions de l'app, fichiers modifiés attendus, nouveaux fichiers non suivis attendus ; rien d'autre dans `apps/` ni `packages/`.

## Constats

### Bloquant

Aucun.

### À corriger

1. **`rtk proxy gh …` passe la garde de sortie sans accord.** `hooks/guard_outbound.py:76` et `:182-185`. `strip_wrappers` retire `rtk`, puis `proxy` devient le nom de la commande : `rtk proxy gh pr merge 12` n'est pas reconnu comme `gh` et passe, même après un « non ». Or `rtk proxy <cmd>` est justement la forme documentée pour lancer une commande brute derrière le hook RTK, et le plan (annexe B) demande que les écritures `gh` soient reconnues « derrière `rtk` ». Pour `git commit` et `git push`, rien ne change : leur regex porte sur le texte brut. **Correction attendue** : après `rtk`, retirer aussi un `proxy` qui suit (dans `strip_wrappers` de la garde de sortie seulement), et ajouter `rtk proxy gh pr merge 1` à `GH_WRITES` et `rtk proxy gh pr list` à `GH_READS` dans `hooks/test_guard_outbound.py`.

2. **Deux comportements déclarés de la garde de sortie sans test.** `hooks/guard_outbound.py:232-241`, `hooks/test_guard_outbound.py:240-254`. L'écart déclaré « `gh` seul ou `gh --help` passent comme lecture », et le cas voisin `gh pr` seul (aide, ligne 241), ne sont prouvés par aucun test : une régression qui ferait de `gh pr` sans sous-commande une écriture, ou l'inverse, ne serait pas vue. **Correction attendue** : ajouter `"gh"`, `"gh --help"` et `"gh pr"` à `GH_READS`.

3. **Les deux refus ajoutés au lanceur n'ont pas de test.** `scripts/launch_task.py:87-95`, `scripts/test_launch_task.py`. L'ajout de sûreté « refus de créer si la liste `ps` est tronquée » (sortie 1, sans `worktree create`) et la réponse de `worktree create` sans id (sortie 2) ne sont couverts par aucun cas. Le premier est précisément ce qui empêche de créer un worktree jumeau ; il doit être prouvé. **Correction attendue** : un test où `worktree ps` répond `"truncated": true` sans la carte cherchée → code 1, message `[jam]`, appels limités à `terminal list` puis `worktree ps` ; un test où `worktree create` répond `{"worktree": {}}` → code 2, message `[jam]`, aucun `terminal create`.

4. **Tests du récapitulatif instables sous charge, alors qu'ils doivent passer en CI.** `hooks/session_start_recap.py:42` (délai d'une seconde par appel Orca), `hooks/test_session_start_recap.py:380-401` et tous les cas qui attendent une réponse du faux `orca`. Le faux binaire est un script Python : son démarrage plus la réponse doivent tenir en 1 s, et `test_cli_too_slow` exige moins de 1,8 s pour tout le hook (démarrage, trois appels git, délai). L'implémenteur a vu des échecs sur machine chargée ; ces tests n'ont jamais tourné sur un runner partagé, et le critère de fin exige qu'ils passent en CI. **Correction attendue** : sortir le délai dans une constante du module (`ORCA_TIMEOUT = 1`) et, dans les tests qui attendent une réponse, lancer le hook par le même procédé `runpy` que `WITH_APP_BIN` en portant ce délai à quelques secondes ; garder 1 s pour `test_cli_too_slow` et `test_cli_calls_overlap`, en desserrant la borne de `test_cli_too_slow` (par exemple sous 2 délais, en comparant au délai effectif plutôt qu'à 1,8 s fixe). À défaut, au moins vérifier la CI de la PR sur plusieurs passes avant le feu vert merge.

### Suggestions

5. **Docstring de la garde de sortie incomplète sur ce qu'elle ne couvre pas.** `hooks/guard_outbound.py:14-22`. Passent aussi sans être vus : `timeout 30 gh pr merge 1`, `nice gh …`, `env -i gh …` / `env -u X gh …` (le premier mot après `env` est une option), `xargs gh …`, `find … -exec gh …`, les backticks (`` `gh pr merge 1` ``), et `gh api graphql` dont la mutation vient d'un fichier (`-F query=@q.graphql`, `--input`). C'est cohérent avec « un garde-fou, pas un bac à sable », mais la liste « NOT covered » ne cite qu'`eval`, variable, alias et script : la compléter, ou reconnaître `timeout`/`nice` comme `WRAPPERS` (avec leur argument) si c'est jugé courant.

6. **`"source": "."` dans `marketplace.json` à confirmer.** `.claude-plugin/marketplace.json:10`, `hooks/test_plugin.py:54`. La doc des marketplaces montre des chemins relatifs en `./…` ; si le validateur exige ce préfixe, l'installation échouerait alors que le test passe. Le point 5 de la recette (`claude plugin validate .`) le dira ; si refus, passer à `"./"` et mettre à jour l'assertion.

7. **Lecture des réponses Orca dans le lanceur.** `scripts/launch_task.py:93, 102, 107, 111`. `(created.get("worktree") or {}).get(...)` lève un `AttributeError` (trace Python, code 1 confondu avec « refusé ») si `worktree`, `terminal`, `wait` ou `send` est une chaîne ou une liste. Vérifier `isinstance(..., dict)` comme le fait déjà `orca_cli.call`, pour garder la promesse des codes 0/1/2.

8. **Message « CLI Orca introuvable » quand `JAM_ORCA_BIN` est posé mais invalide.** `scripts/orca_cli.py:44-45`. Le choix de ne pas se replier est juste, mais le message dit « ni JAM_ORCA_BIN » alors que la variable est posée : un message distinct (« JAM_ORCA_BIN ne désigne pas un exécutable ») orienterait mieux, toujours sans citer de chemin.

9. **`--interval` négatif ou nul** (`scripts/watch_cards.py:95-96`) : refusé avec le code 2, sans test. Un cas suffit.

## Écarts au plan déclarés par l'implémenteur

- **`owner.name` « jammindev » dans `marketplace.json`** : exigé par le schéma des marketplaces ; c'est le nom de l'organisation, déjà dans l'URL `repository` de `plugin.json`. Juste ; sa conformité au critère « aucun nom de personne » revient à l'axe B.
- **Id du worktree lu dans la réponse de `worktree create`, sans relire `ps`** : acceptable. Un id mal formé ferait échouer `terminal create` avec un message `[jam]` et le code 2, sans effet silencieux ; une relecture par `ps` aurait au contraire pu manquer un worktree tout juste créé. Le format vient de la fixture tirée de la doc de la CLI ; `launch_task` n'est pas exercé en recette, à garder en tête.
- **Ajouts de sûreté** (`watch_cards` en code 2 sans carte, 30 s par défaut ; refus sur liste `ps` tronquée ; codes 0/1/2) : justes et utiles ; le refus sur `ps` tronquée manque de test (constat 3).
- **`gh` seul ou `gh --help` en lecture** : juste (affiche l'aide), non testé (constat 2). **Commande illisible contenant `gh` refusée** : cohérent avec le refus par défaut, testé ; faux positif possible sur un heredoc dont le texte contient une apostrophe et le mot `gh`, sans gravité (un accord suffit).
- **`JAM_ORCA_BIN` non exécutable = CLI introuvable** : juste et testé (voir suggestion 8 pour le message).
- **Première ligne « [jam] Reprise de contexte »** : juste, marque en tête, testée.
- **`scripts/fixtures/fake_orca.py` et `__init__.py`** : nécessaires à l'import des tests depuis la racine ; justes.
- **Tests instables** : confirmé par lecture du code, voir constat 4.

## Points vérifiés sans constat

- Garde de sortie : accord lu sur le seul dernier message, résultats d'outil, `isMeta`, notifications et interruptions écartés ; ligne `[jam] [état git]` retirée (testé) ; cas du feu vert remonté par une carte refusé puis passé après « ok merge » (testé) ; exemption `/tmp/claude-*` limitée à commit et push (testé) ; formes `-R`, `--repo=`, chemin absolu, `rtk gh`, `bash -c`, `&&`, `;`, `gh api -X/--method/-XPATCH`, champs `-f/-F/--field/--raw-field/--input`, `graphql` avec `mutation` (testés).
- `orca_cli` : ordre de recherche, lien cassé ignoré, `APP_BIN` remplaçable, message sans chemin, échec, JSON illisible, formes inattendues, délai dépassé (testés).
- `watch_cards` : réveils `⏸`/`⛔` en tête, `✓`/`💬` dans un segment, pas de réveil `▶`→`▶`, carte déjà en attente au lancement, autre projet, carte `completed`, id du repo, échecs de la CLI (testés).
- `launch_task` : plafonds global et du projet avant tout autre appel, terminal sans agent ou déconnecté non compté, worktree existant réutilisé, même nom dans un autre repo non réutilisé, rôle restreint, brief absent, brief envoyé à l'identique, agent pas prêt (pas d'envoi), brief refusé (testés).
- `hooks.json` : enveloppe `hooks`, quatre événements et matchers du plan, commandes `python3 "${CLAUDE_PLUGIN_ROOT}/hooks/…"` vers des fichiers existants (testé).
- CI : un seul job `python3 -m unittest`, `permissions: contents: read` et `timeout-minutes` gardés ; tests portables (aucun chemin propre à macOS hors de chaînes fictives).
- Aucun nom de personne, chemin du poste ni nom d'un autre projet dans `hooks/`, `scripts/` et `.claude-plugin/` (chemins de test fictifs : `/Users/testhome`, `/Users/x`, `/work/…`).
- Docs : fiche concept fidèle au code (ordre de recherche du binaire, codes de sortie, pièges) ; README, `02-ARCHITECTURE.md`, `OPEN-QUESTIONS.md` (Q-055) et fiches historiques cohérents avec le plan.

RELECTURE : CORRECTIONS (4)
