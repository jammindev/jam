# Relecture #22 — axe B, conformité, tour 4

> Relecteur B (conformité), contexte neuf. Lus : profil du relecteur (section Kit), `AGENTS.md`, ADR 0016, plan `22-repo-devient-le-kit.md` (ajustements a à c compris), section K1-1 de `cadrage-kit-issues.md`. Relus en entier : `hooks/` (4 hooks, 5 fichiers de test, `hooks.json`), `scripts/` (`orca_cli.py`, `watch_cards.py`, `launch_task.py`, leurs tests, `fixtures/`), `.claude-plugin/`, `docs/concepts/plugin-et-hooks.md`, et le diff de `.github/workflows/ci.yml`, `.gitignore`, `README.md`, `AGENTS.md`, `docs/concepts/` et `docs/specs/`. Aucune relecture des tours précédents lue.

## Tests

`python3 -m unittest` depuis la racine : **135 tests, OK** (43 s).

## Conformité au plan, à l'issue et aux ADR

- **Étape 1** : `apps/`, `packages/` et les sept fichiers de la racine sont retirés (`git status`), rien d'autre. `.gitignore` : blocs de l'app retirés, `__pycache__/` ajouté, `CLAUDE.md` et `.claude/settings.local.json` gardés. `ci.yml` : un seul job `ubuntu-latest` qui lance `python3 -m unittest`, `permissions: contents: read` et `timeout-minutes` gardés. Conforme.
- **Étapes 2 à 4** : quatre hooks dans `hooks/`, `__init__.py` vides ; tests du comportement repris pour `guard_outbound` et `git_context` ; marque `[jam]` sur chaque sortie, vérifiée par les tests de chaque hook ; « le mainteneur » partout ; binaire Orca résolu par `scripts/orca_cli.py` seul (ajustements a et b) ; test du `PATH` sans `JAM_ORCA_BIN` (`test_cli_found_on_path`) et message « introuvable » sans `/` (`test_cli_missing_everywhere`, `test_not_found_message_has_no_path`). Code compatible Python 3.9 (ni `match`, ni annotations `X | Y`).
- **Étape 5** : toutes les écritures de l'annexe B refusées sans accord et passées après ; toutes les lectures jamais refusées, même transcript illisible ; formes `rtk`, `-R`/`--repo`, chemin absolu, `gh api -X PATCH`, `-f x=y` couvertes ; cas du feu vert remonté par la carte testé (refus, refus après compaction, passage après « ok merge ») ; ligne `[jam] [état git]` retirée du message lu. Exemption `/tmp/claude-*` limitée à commit et push, testée pour `gh`. La garde du coordinateur ne traite pas les sorties : inchangée hors marque.
- **Étape 6** : `plugin.json` (name, description, license, repository ; ni `author` ni `version`), `marketplace.json` (`name: jam`, un plugin `source: "."`), `hooks.json` avec l'enveloppe `hooks`, les quatre événements et matchers du plan ; `test_plugin.py` vérifie tout cela et l'existence des fichiers.
- **Étapes 7 et 8** : arguments, réveils, codes de sortie et refus « avant tout autre appel » conformes ; tous les tests listés au plan sont présents.
- **Étapes 9 et 10** : fiche concept au format de `docs/concepts/README.md`, avec les trois pièges demandés (hooks en double, `CLAUDE_PLUGIN_ROOT` absent de l'outil Bash, accord lu sur le seul dernier message) et la limite du relais par `orca terminal send` (question 3). README : section de l'app retirée, « Installation » conforme à Q-055 (marketplace locale, `--scope user`, `git pull`, `--plugin-dir`), installation pour tout le poste dite voulue (ADR 0016). `AGENTS.md`, fiches historiques, tableau des fiches, Q-055 et ligne « Distribution » à jour. Aucun fichier du process ni des profils touché (K1-2).
- **Orca, règle 9** : aucune reprise ; rien à vérifier dans `THIRD_PARTY_NOTICES.md`.

## Écarts déclarés par l'implémenteur

Tous admis :
- `owner.name` « jammindev » : champ exigé par le schéma des marketplaces ; c'est le nom de l'organisation GitHub, déjà dans `repository`, pas un nom de personne.
- Id du worktree lu dans la réponse de `orca worktree create` : le plan en faisait un prérequis du brief (forme JSON de cette sortie), la fixture `worktree-create.json` fixe le contrat, et `test_created_worktree_without_id` couvre une réponse sans id. Un appel `ps` de moins, sans perte.
- Ajouts de sûreté (aucune carte → sortie 2, intervalle 30 s, refus sur liste `ps` tronquée, codes 0/1/2) : petits, testés, dans l'esprit du refus de la liste tronquée déjà au plan. Pas de sur-ingénierie.
- `gh`, `gh --help`, `gh pr` en lecture ; commande illisible avec `gh` refusée ; `graphql` avec `--input` ou `-F @fichier` en écriture ; substitutions de commande reconnues ; résumés de compaction écartés : chacun ferme un trou réel de la garde ou évite un refus d'une simple aide, et la docstring de `guard_outbound.py` les décrit.
- `JAM_ORCA_BIN` non exécutable sans repli : choix explicite, documenté dans `orca_cli.py` et testé.
- Première ligne « [jam] Reprise de contexte » : ce que demande la marque.
- `scripts/fixtures/fake_orca.py` et `__init__.py` : servent le contrat des fixtures prévu au plan.
- Délai de 5 s dans les tests qui attendent une réponse, 1 s pour le test de lenteur : rend la CI moins fragile, le comportement réel reste testé.

## Sécurité du repo public

Recherche dans `hooks/`, `scripts/`, `.claude-plugin/` et les docs modifiées : aucun nom de personne, aucun chemin du poste, aucun nom d'un autre projet. Seuls chemins trouvés : fictifs dans les tests (`/Users/testhome/…`, `/Users/x/…`, `/work/…`, `repo-autre`), et l'emplacement standard d'installation de l'app Orca sur macOS dans `orca_cli.py`, admis. Aucun secret.

## Constats

### Bloquant

Aucun.

### À corriger

Aucun.

### Suggestions

1. `hooks/test_guard_outbound.py:2` : la docstring dit « the PreToolUse guard of commit and push » alors que le fichier teste aussi toutes les écritures `gh`. Écrire « the single outbound guard: commit, push and gh writes ».
2. `hooks/test_session_start_recap.py:21` : « Run: python3 test_session_start_recap.py », seul fichier de test sans la forme des autres. Écrire « Run: python3 -m unittest hooks.test_session_start_recap ».
3. `scripts/orca_cli.py:26` : quand `JAM_ORCA_BIN` est posé mais non exécutable, `NOT_FOUND` dit « ni orca dans le PATH, ni l'app » alors que ni le `PATH` ni l'app n'ont été regardés (pas de repli, voulu). Le message pourrait le dire, par exemple un second message « JAM_ORCA_BIN ne désigne pas un exécutable », toujours sans chemin. Cosmétique : le cas ne vient que d'un réglage explicite.

RELECTURE : OK
