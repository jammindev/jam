# Relecture B (conformité), tour 2 — #22 Le repo devient le kit

> Relecteur B, axe conformité, contexte neuf. Référence : plan `22-repo-devient-le-kit.md`, y compris ses « Ajustements validés après le feu vert plan », section K1-1 de `cadrage-kit-issues.md`, ADR 0016, `AGENTS.md`. Aucune relecture précédente lue.

## Ce qui a été relu

- Suppressions de l'app (`git status`) : `apps/`, `packages/`, `package.json`, `pnpm-lock.yaml`, `pnpm-workspace.yaml`, `tsconfig.base.json`, `vitest.config.ts`, `.node-version`. Rien d'autre de supprimé, aucun fichier ignoré resté dans `apps/` ou `packages/`.
- Modifiés : `.github/workflows/ci.yml`, `.gitignore`, `AGENTS.md`, `README.md`, `docs/concepts/README.md`, `docs/concepts/processus-electron.md`, `docs/concepts/coeur-separe-protocole.md`, `docs/specs/02-ARCHITECTURE.md`, `docs/specs/OPEN-QUESTIONS.md`.
- Non suivis, lus en entier : `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `hooks/` (quatre hooks, `hooks.json`, cinq fichiers de tests, `__init__.py`), `scripts/` (`orca_cli.py`, `watch_cards.py`, `launch_task.py`, leurs tests, `fixtures/fake_orca.py`, `fixtures/__init__.py`, `fixtures/orca/*.json`), `docs/concepts/plugin-et-hooks.md`.
- Tests : `python3 -m unittest` à la racine → **135 tests, OK** (41,8 s).

## 1. Conformité au plan, au critère de fin et aux ADR

| Exigence | Constat |
|---|---|
| Étape 1 : retrait de l'app, `.gitignore`, CI | Conforme. `.gitignore` garde `CLAUDE.md` et `.claude/settings.local.json`, retire `node_modules`, `out`, `*.db`, ajoute `__pycache__/`. CI : un job `ubuntu-latest`, `timeout-minutes` gardé, `python3 -m unittest`, commentaire sur le *pourquoi* (zéro test = échec sous 3.12+). |
| Étapes 2-3 : rapatriement, tests du comportement actuel | Conforme. `guard_outbound` et `git_context` ont leurs tests (annexe A : accord, refus, bruit ignoré, rappel système, transcript absent, `--dry-run`, `git -C`, `/tmp/claude-*`, autre outil ; hors repo, repo neuf, fichiers comptés, worktree secondaire, HEAD détachée). Tests de `git_context` isolés (HOME, identité git posée) : passeront sur le runner. |
| Étape 4 : hooks génériques | Conforme. Marque `[jam]` sur chaque sortie, assertée dans chaque fichier de tests ; « le mainteneur » partout ; binaire Orca résolu par `scripts/orca_cli.py` seul (ajustements a et b) ; test du `PATH` sans `JAM_ORCA_BIN` (`test_cli_found_on_path`) ; message « introuvable » sans `/` (`test_cli_missing_everywhere`, `test_not_found_message_has_no_path`), avec `APP_BIN` remplacé pour tenir sur un poste où Orca est installé. |
| Étape 5 : garde de sortie unique | Conforme à l'annexe B : liste de lecture exacte, refus par défaut (question 2), `gh api` en lecture sans champ, `graphql` sans `mutation`, `rtk`, chemin absolu, `-R`/`--repo`. Toutes les formes nommées au plan sont testées, ainsi que le cas du feu vert remonté par la carte (refus puis passage après « ok merge ») et le retrait de la ligne `[jam] [état git]`. Exemption `/tmp/claude-*` limitée à commit et push, testée. |
| Étape 6 : câblage | Conforme. `plugin.json` sans `author` ni `version` (asserté) ; `hooks.json` avec l'enveloppe `"hooks"`, les quatre événements et matchers du plan ; `test_plugin.py` vérifie forme des commandes et existence des fichiers. |
| Étape 7 : veille des cartes | Conforme : `⏸`/`⛔` en premier segment, `✓`/`💬` dans n'importe quel segment, carte `completed` ignorée, état au lancement mémorisé, autre projet ignoré, sortie 2 sur CLI en échec ou JSON illisible. |
| Étape 8 : lancement d'une tâche | Conforme : refus aux plafonds global et projet avant tout autre appel (asserté sur la liste exacte des appels), terminal sans agent ou déconnecté non compté, liste tronquée refusée, worktree existant réutilisé, `--role` limité à `[a-z-]+`, brief envoyé à l'identique. |
| Étape 9 : fiche concept | Conforme au format de `docs/concepts/README.md` ; RET-005 ; les trois pièges du plan, plus la limite de `orca terminal send` (question 3). |
| Étape 10 : docs du rédacteur | Conforme : section « L'app » remplacée par « Installation » (marketplace, `--scope user`, `git pull`, `--plugin-dir`) ; ligne d'`AGENTS.md` ; fiches de l'app marquées historiques ; tableau des fiches ; Q-055 tranchée ; ligne « Distribution » de `02-ARCHITECTURE.md`. L'installation pour tout le poste et son effet sur les autres projets sont écrits, avec renvoi à l'ADR 0016. |
| Section Orca | Aucune reprise ; rien à vérifier dans `THIRD_PARTY_NOTICES.md`. |
| ADR | Aucune contradiction. La garde du coordinateur garde l'exception « installation d'un hook relu » (Q-056 hors périmètre) ; la garde de sortie lit la seule session qui agit (ADR 0016, relais allégé). |
| Python 3.9 | Ni `match` ni annotation `X | Y` dans `hooks/` ni `scripts/`. |

Points du critère de fin hors de portée d'une relecture : CI verte sur la PR, câblage réel par `--plugin-dir` (recette), temps du mainteneur dans le corps de la PR.

## Écarts déclarés par l'implémenteur

Tous acceptés.

- **`owner.name` « jammindev » dans `marketplace.json`** : champ exigé par le format des marketplaces ; c'est le nom de l'organisation GitHub, déjà public dans l'URL `repository`, pas un nom de personne. Le test n'exige qu'un nom non vide.
- **Id du worktree créé lu dans la réponse de `orca worktree create`, sans relire `ps`** : un appel de moins, même garantie (l'id vient de la CLI), échec explicite si l'id manque (testé). Simplifie le plan sans rien perdre.
- **Ajouts de sûreté** (projet sans carte → sortie 2, intervalle 30 s par défaut, liste `ps` tronquée → refus de créer, codes 0/1/2) : petits, testés, dans l'esprit du plan (refus quand on ne peut pas compter ; une faute de frappe ne laisse pas le coordinateur attendre à vide). Pas de la sur-ingénierie.
- **`gh` seul, `gh --help`, `gh pr` comme lecture ; commande illisible contenant `gh` refusée** : ce sont des aides (lecture) ; le refus de l'illisible applique le refus par défaut de la question 2.
- **`JAM_ORCA_BIN` non exécutable = CLI introuvable, sans repli** : conforme à l'ajustement a (« `JAM_ORCA_BIN` s'il est posé ») ; un choix explicite qui échoue est signalé plutôt que remplacé en silence. Testé.
- **Première ligne « [jam] Reprise de contexte (hook SessionStart) » au lieu d'un titre `##`** : la marque est en tête, comme le veut le plan.
- **`scripts/fixtures/fake_orca.py` et `scripts/fixtures/__init__.py`** : outillage de test partagé par les trois fichiers de tests des scripts ; sert les fixtures du plan.
- **Délai de 5 s dans les tests qui attendent une réponse, 1 s gardée pour le test de lenteur** : le comportement du hook (1 s) reste testé tel quel ; le changement ne vise que la stabilité sous charge, et il est commenté.

## 2. Lisibilité

Bonne. Chaque module ouvre sur une docstring qui dit son rôle, ses codes de sortie et ce qu'il ne couvre pas ; les commentaires portent le *pourquoi* (transcript lu par la fin, exemption `/tmp/claude-*` limitée à commit et push, appels Orca en parallèle, id jamais aplati). Deux docstrings de tests ont vieilli (suggestions 1 et 2).

## 3. Sur-ingénierie

Rien à retirer. La garde de sortie lit aussi `bash -c`, `rtk proxy`, les affectations de variables et les mots-clés du shell en plus des formes de l'annexe B : quelques lignes, reprises du découpage de la garde du coordinateur, sans lesquelles `GH_TOKEN=x gh pr merge 1` passerait. C'est la garde demandée, pas une extension.

## 4. Secrets, données personnelles, chemins du poste

- `hooks/`, `scripts/`, `.claude-plugin/` : aucun nom de personne, aucun nom d'un autre projet, aucun chemin du poste. Seuls chemins : l'emplacement standard de l'app Orca sur macOS (admis), et des chemins fictifs dans les tests (`/Users/testhome/…`, `/Users/x/…`, `/work/…`). « jammindev » n'apparaît que comme organisation GitHub (URL du repo, `owner` de la marketplace).
- Docs modifiées : rien d'ajouté par ce diff. Voir la suggestion 3 pour l'existant.

## 5. Code repris d'Orca

Aucune reprise déclarée ni constatée.

## Constats

### Bloquant

Aucun.

### À corriger

Aucun.

### Suggestions

1. **`hooks/test_guard_outbound.py:2`** : la docstring dit « the PreToolUse guard of commit and push », alors que la garde couvre aussi les écritures `gh` et que la moitié du fichier les teste. Correction : « the single outbound guard (commit, push, gh writes) ».
2. **`hooks/test_session_start_recap.py:21`** : « Run: python3 test_session_start_recap.py », forme héritée du poste, qui ne tourne que depuis `hooks/`. Les autres fichiers de tests disent `python3 -m unittest hooks.test_…`. Correction : « Run: python3 -m unittest hooks.test_session_start_recap ».
3. **`docs/specs/OPEN-QUESTIONS.md`** (existant, hors du diff) : la colonne « Qui » porte le prénom du mainteneur sur une cinquantaine de lignes. Ce diff n'en ajoute aucun (la ligne Q-055 modifiée n'en porte pas) ; le remplacer par « le mainteneur » sortirait du périmètre de #22. À noter pour une tâche de docs si le mainteneur veut appliquer à `docs/` la règle des hooks.

RELECTURE : OK
