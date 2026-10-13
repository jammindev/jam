# Relecture — #22 Le repo devient le kit — axe B, conformité, tour 1

> Relecteur B (conformité), contexte neuf. Référentiel : `AGENTS.md`, ADR 0016, plan `docs/plans/22-repo-devient-le-kit.md` (ajustements a, b, c compris), section K1-1 de `docs/plans/cadrage-kit-issues.md`. Le plan est hors relecture.

## Ce qui a été vérifié

- **Tests** : `python3 -m unittest` depuis la racine : 133 tests, `OK` (45 s).
- **Retrait de l'app** : `git status` montre la suppression de `apps/`, `packages/`, `package.json`, `pnpm-lock.yaml`, `pnpm-workspace.yaml`, `tsconfig.base.json`, `vitest.config.ts`, `.node-version`, et rien d'autre de supprimé. Aucun fichier ignoré resté sur disque dans `apps/`, `packages/` ou `node_modules/`. `.gitignore` : blocs de l'app retirés, `__pycache__/` ajouté, `CLAUDE.md` et `.claude/settings.local.json` gardés. CI : un seul job `ubuntu-latest`, `python3 -m unittest`, `permissions: contents: read` et `timeout-minutes: 10` gardés.
- **Hooks rapatriés** (comparés aux originaux du poste) : `guard_coordinator.py` ne change que par la marque (1 ligne) ; `test_guard_coordinator.py` par une assertion de marque (1 ligne) ; `guard_outbound.py` garde à l'identique la lecture de l'accord et le traitement de commit et push (prénom remplacé par « le mainteneur », renvoi à l'autre projet retiré de la docstring), et ajoute la partie `gh` de l'annexe B. Comportements de l'annexe A conservés.
- **Étapes 4 et 5** : marque `[jam]` testée sur les sorties des quatre hooks et des deux scripts ; faux `orca` trouvé par le `PATH` sans `JAM_ORCA_BIN` (`test_cli_found_on_path`) ; « CLI Orca introuvable » sans aucun `/` (`test_cli_missing_everywhere`, `test_not_found_message_has_no_path`) ; toutes les écritures de l'annexe B refusées sans accord et passées après accord ; lectures jamais refusées, même transcript illisible ; formes `rtk git push`, `rtk gh pr create`, `gh -R o/r issue create`, `gh api -X PATCH …`, `gh api … -f x=y` couvertes ; cas du feu vert remonté par une carte (refus, puis passage sur « ok merge ») ; ligne `[jam] [état git]` retirée du message lu ; exemption `/tmp/claude-*` limitée à commit et push.
- **Ajustements a et b** : `scripts/orca_cli.py` est le seul endroit qui résout le binaire (`JAM_ORCA_BIN`, `PATH`, `APP_BIN`) ; `session_start_recap.py`, `watch_cards.py` et `launch_task.py` passent tous par lui. `APP_BIN` est une constante remplacée par les tests. Aucun autre chemin en dur.
- **Étape 6** : `plugin.json` (`name`, `description`, `license`, `repository`, ni `author` ni `version`), `marketplace.json` (`"source": "."`), `hooks.json` (enveloppe `hooks`, quatre événements et matchers conformes, commandes `python3 "${CLAUDE_PLUGIN_ROOT}/hooks/<fichier>"`), vérifiés par `hooks/test_plugin.py`.
- **Étapes 7 et 8** : tous les cas de test exigés par le plan sont présents (`test_watch_cards.py`, `test_launch_task.py`) ; refus aux plafonds sans aucun appel après `terminal list` ; arguments exacts de chaque appel vérifiés ; `--role` limité à `[a-z-]+`.
- **Étape 9** : `docs/concepts/plugin-et-hooks.md` suit le format de `docs/concepts/README.md` (cinq rubriques) et couvre ce que le plan demande : plugin, raison d'un hook (RET-005), pièges (hooks en double, `CLAUDE_PLUGIN_ROOT` absent de Bash, accord lu sur le seul dernier message).
- **Étape 10** : `README.md` (section « Installation » conforme à Q-055, `--plugin-dir`, résolution de la CLI Orca), `AGENTS.md`, fiches historiques, tableau des fiches, Q-055 tranchée, ligne « Distribution » de `02-ARCHITECTURE.md` : conformes au plan et à l'ADR 0016.
- **Python 3.9** : ni `match`, ni annotation `X | Y`, ni API postérieure à 3.9 repérée.
- **Orca (règle 9)** : le plan ne prévoit aucune reprise ; aucune trace de code repris dans les fichiers relus.
- **Repo public** : recherche dans `hooks/`, `scripts/`, `.claude-plugin/` et les docs modifiées des prénoms, nom de famille, nom d'utilisateur du poste, chemins du poste, noms des autres projets, hôte et IP du serveur : rien. Seuls chemins absolus : `APP_BIN` (emplacement standard de l'app Orca, admis) et des chemins fictifs dans les tests (`/Users/testhome`, `/Users/x/…`, `/work/…`). Les occurrences de « Ben » dans `OPEN-QUESTIONS.md` préexistent et ne sont pas touchées par ce diff (la ligne Q-055 modifiée n'en ajoute pas).

## Écarts déclarés par l'implémenteur : jugement

| Écart | Jugement |
|---|---|
| `owner.name` « jammindev » dans `marketplace.json` | **Admis.** Champ exigé par le schéma des marketplaces ; c'est l'organisation GitHub, déjà publique dans l'URL `repository` de `plugin.json`. Pas un nom de personne ni un chemin du poste. |
| `launch_task.py` prend l'id du worktree dans la réponse de `orca worktree create`, sans relire `ps` | **Admis.** Plus simple que le plan, sans perte : la forme de la réponse est figée par `fixtures/orca/worktree-create.json` et l'absence d'id est refusée (code 2). Plan : prérequis du brief sur cette forme. |
| `watch_cards` sort en 2 sans carte ; intervalle 30 s par défaut | **Admis.** Un projet mal nommé attendrait sinon pour toujours sans rien dire ; le plan ne fixait pas de défaut. |
| `launch_task` refuse de créer si la liste `ps` est tronquée | **Admis.** Même logique que le refus sur `terminal list` tronquée, déjà au plan ; évite un worktree jumeau. |
| Codes de sortie 0/1/2 de `launch_task` | **Admis.** Documentés dans la docstring ; distinguent un refus voulu d'une panne. |
| `gh` seul ou `gh --help` passent comme lecture ; commande illisible contenant `gh` refusée | **Admis.** Le premier est de l'aide (`help` est déjà dans la liste de lecture) ; le second applique le refus par défaut (question 2). |
| `JAM_ORCA_BIN` non exécutable = CLI introuvable, sans repli | **Admis.** Un choix explicite qui échoue doit se voir ; documenté dans `orca_cli.py` et testé. |
| Première ligne « [jam] Reprise de contexte » au lieu d'un titre `##` | **Admis.** Imposé par la règle de marque (chaque message commence par `[jam]`). |
| `scripts/fixtures/fake_orca.py` et `scripts/fixtures/__init__.py` ajoutés | **Admis.** Le faux binaire écrit dans un dossier temporaire est celui que prévoit le plan (§2) ; le partager entre deux suites de tests évite une copie. `__init__.py` permet l'import `scripts.fixtures.fake_orca`. |
| Risque de tests instables dans `test_session_start_recap.py` (1 s laissée au faux `orca`) | Voir suggestion 1. |

Extension non déclarée mais conforme : `guard_outbound.py` reconnaît aussi `gh` derrière des affectations d'environnement, quelques mots-clés du shell et dans `bash -c`. Le plan n'en demande que `rtk`, chemin absolu et `-R`/`--repo` ; l'ajout reprend le mécanisme existant de `guard_coordinator.py` (mêmes `WRAPPERS`, même lecture de `-c`), ferme des contournements évidents à faible coût et figure dans la docstring. Pas de sur-ingénierie.

## Constats

### Bloquant

Aucun.

### À corriger

Aucun.

### Suggestions

1. **`hooks/test_session_start_recap.py`, l. 380-388 et cas qui attendent une réponse du faux `orca`** : le hook laisse 1 s à la CLI (`session_start_recap.py`, l. 42), et `test_cli_too_slow` exige moins de 1,8 s. Sur un runner chargé, le démarrage du faux `orca` (un interpréteur Python) peut dépasser ce délai et faire échouer la CI, alors que le critère de fin exige les tests au vert en CI. Pas de correction maintenant (tests rapatriés, délai voulu par le hook) : surveiller le premier passage de la CI sur la PR, et noter le risque dans `docs/specs/OPEN-QUESTIONS.md` s'il se confirme (règle 4 d'`AGENTS.md`).
2. **`hooks/test_guard_outbound.py`, l. 2** : la docstring dit « the PreToolUse guard of commit and push » ; la garde couvre aussi les écritures `gh`. Remplacer par « the single outbound guard (commit, push, gh writes) », pour un lecteur qui ne lit que l'en-tête.
3. **`hooks/test_session_start_recap.py`, l. 52** : l'identifiant fictif `…::/Users/x/orca/workspaces/jam/…` reproduit la disposition des dossiers d'Orca sur un poste. Il ne nomme ni personne ni le poste, mais les fixtures des scripts utilisent `/work/jam-worktrees/…` : aligner sur cette forme éviterait qu'une recherche de chemins du poste par le recetteur s'y arrête.
4. **`hooks/test_session_start_recap.py`, l. 21** : « Run: python3 test_session_start_recap.py », alors que les autres suites indiquent `python3 -m unittest hooks.<module>`. Uniformiser.

RELECTURE : OK
