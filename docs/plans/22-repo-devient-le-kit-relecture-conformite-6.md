# Relecture — #22 Le repo devient le kit — axe B, conformité, tour 6

> Relecteur B (conformité), contexte neuf. Lu : profil du relecteur (section Kit comprise), `AGENTS.md`, ADR 0016, plan `22-repo-devient-le-kit.md` (ajustements validés compris), section K1-1 de `cadrage-kit-issues.md`. Relu : `hooks/` (code, tests, `hooks.json`), `scripts/` (code, tests, `fixtures/`), `.claude-plugin/`, `docs/concepts/plugin-et-hooks.md`, et le diff de `.github/workflows/ci.yml`, `.gitignore`, `README.md`, `AGENTS.md`, `docs/concepts/README.md`, des deux fiches historiques, de `02-ARCHITECTURE.md` et d'`OPEN-QUESTIONS.md`. Aucune relecture des tours précédents lue.

## Tests

`python3 -m unittest` depuis la racine : **137 tests, OK** (44,7 s).

## Conformité au plan, au critère de fin et aux ADR

- **Retrait de l'app** : `git status` montre exactement les suppressions prévues (`apps/`, `packages/`, `package.json`, `pnpm-lock.yaml`, `pnpm-workspace.yaml`, `tsconfig.base.json`, `vitest.config.ts`, `.node-version`) ; aucun fichier resté dans `apps/` ni `packages/`. `.gitignore` : blocs de l'app retirés, `__pycache__/` ajouté, `CLAUDE.md` et `.claude/settings.local.json` gardés. CI : job `ubuntu-latest` qui lance `python3 -m unittest`, `permissions: contents: read` et `timeout-minutes` gardés. Conforme.
- **Câblage** : `hooks/hooks.json` porte l'enveloppe `"hooks"`, les quatre événements et matchers du plan, la forme `python3 "${CLAUDE_PLUGIN_ROOT}/hooks/<fichier>"` ; `plugin.json` sans `author` ni `version` ; `marketplace.json` à source `"."`. `test_plugin.py` couvre ce que l'étape 6 demande.
- **Ajustements a et b** : `scripts/orca_cli.py` seul résout le binaire (`JAM_ORCA_BIN`, `PATH`, emplacement standard de l'app, constante remplacée dans les tests) ; `session_start_recap.py`, `watch_cards.py` et `launch_task.py` passent tous par lui. `NOT_FOUND` ne cite aucun chemin, et un test le vérifie.
- **Marque `[jam]`** : sur chaque sortie des hooks et des scripts, vérifiée par les tests (refus, récapitulatif, ligne d'état git, erreurs d'argparse des scripts).
- **Garde de sortie** (étape 5, annexe B) : liste de lectures exacte, refus par défaut, `-R`/`--repo`, `rtk`, chemin absolu ; le cas du feu vert remonté par la carte est testé (`test_green_light_relayed_by_a_card_is_not_an_approval`), avant et après compaction ; l'exemption `/tmp/claude-*` ne vaut pas pour `gh` (testé). La garde du coordinateur garde son comportement et son exception (Q-056 hors périmètre).
- **Scripts** (étapes 7 et 8) : chaque cas de test listé au plan est présent ; refus aux plafonds avant tout autre appel, terminal sans agent ou déconnecté non compté (fixture `terminal-list.json`, `test_global_cap`), worktree existant réutilisé sans `create`, brief envoyé à l'identique.
- **Schéma de la CLI Orca** : versionné seulement en exemples réduits (`scripts/fixtures/orca/*.json`), comme le plan le décide.
- **Fiche concept** : au format de `docs/concepts/README.md`, avec RET-005 et les trois pièges demandés à l'étape 9 ; la limite de la question 3 (texte de `orca terminal send` compté comme message du mainteneur) y est notée.
- **Docs du rédacteur** (étape 10) : section « L'app (en cours de retrait) » remplacée par « Installation » (marketplace locale, `--scope user`, `git pull`, `--plugin-dir`) ; ligne de la stack d'`AGENTS.md` mise à jour ; fiches de l'app marquées historiques ; tableau des concepts à jour ; Q-055 tranchée ; ligne « Distribution » de `02-ARCHITECTURE.md` à jour. La phrase d'installation pour tout le poste figure dans le README, comme l'issue le demande.
- **Orca** : aucune reprise de code, conforme à la section 3 du plan ; rien à ajouter à `THIRD_PARTY_NOTICES.md`.
- **Python 3.9** : ni `match`, ni annotations `X | Y`, ni f-string à guillemets imbriqués du même type.

## Écarts déclarés par l'implémenteur : jugement

| Écart | Jugement |
|---|---|
| `owner.name` « jammindev » dans `marketplace.json` | Accepté. Le champ `owner` est exigé par le format de la marketplace ; « jammindev » est l'organisation GitHub, déjà publique dans `repository` de `plugin.json`, pas un nom de personne. L'interdit d'`author` du plan vise `plugin.json`. |
| `launch_task.py` prend l'id dans la réponse de `orca worktree create`, sans relire `ps` | Accepté. La forme de cette réponse est celle que le plan exigeait de l'orchestrateur en prérequis (section 5) ; la relecture par `ps` n'ajoutait qu'un appel. Le cas d'une réponse sans id sort en 2 sans créer de terminal (testé). |
| Sûretés : `watch_cards` sort en 2 sans carte ou sur liste tronquée, intervalle 30 s ; `launch_task` refuse de créer sur liste `ps` tronquée, sort en 2 sur brief illisible ; codes 0/1/2 | Accepté. Chaque ajout évite une attente sans fin ou un worktree en double, est commenté sur son *pourquoi*, documenté dans la docstring et testé. Pas de sur-ingénierie notable. |
| `gh` seul, `gh --help`, `gh pr` passent comme lecture ; commande illisible contenant `gh` refusée | Accepté. Affichage d'aide seulement ; le refus de l'illisible suit le refus par défaut (question 2). |
| `gh api graphql` avec `--input` ou `-F @fichier` compté comme écriture | Accepté : une requête hors de vue ne se vérifie pas, refus par défaut. Écrit dans la docstring. |
| Écritures `gh` dans une substitution de commande ; lignes continuées par `\` réunies | Accepté. Formes courantes chez un agent (forme multiligne de la doc GitHub), testées, commentées. |
| Résumés de compaction ignorés comme messages du mainteneur | Accepté. Sert directement le cas nommé de l'issue (feu vert remonté par la carte) ; expliqué dans la fiche concept. |
| `JAM_ORCA_BIN` non exécutable = CLI introuvable, sans repli | Accepté : conforme à l'ajustement a (« `JAM_ORCA_BIN` s'il est posé »), testé. |
| Première ligne « [jam] Reprise de contexte » au lieu d'un titre `##` | Accepté : c'est la marque exigée en tête de chaque message. |
| `scripts/fixtures/fake_orca.py` et `scripts/fixtures/__init__.py` | Accepté. Le faux binaire reste écrit par le test dans un dossier temporaire, comme le plan le veut ; le module le partage entre trois fichiers de tests au lieu de le copier. |
| Délai de la CLI porté à 5 s dans les tests qui attendent une réponse, 1 s pour le test de lenteur | Accepté : le hook garde 1 s ; seuls les tests changent, avec la raison en commentaire. |

## Sécurité du repo public

Recherche dans `hooks/`, `scripts/`, `.claude-plugin/` et les docs modifiées : aucun nom de personne, aucun chemin du poste, aucun nom d'un autre projet. Les chemins des tests sont fictifs (`/Users/testhome`, `/Users/x/…`, `/work/…`) ; le seul chemin réel est l'emplacement standard de l'app Orca sur macOS, admis par le plan. Pas de secret.

## Constats

### Bloquant

Aucun.

### À corriger

Aucun.

### Suggestions

1. **`hooks/guard_outbound.py:23-26`** : la liste « NOT covered » peut citer `xargs`, `find -exec` et les options d'un enveloppeur (`sudo -u x gh …`, `env -i gh …`) : `echo 1 | xargs gh pr merge` passe, alors que `xargs git commit` est refusé (la regex git lit toute la ligne). Forme rare ; la citer dans la docstring suffit, sans code de plus.
2. **`hooks/test_guard_outbound.py:2`** : la docstring dit « the PreToolUse guard of commit and push » ; la garde couvre aussi les écritures `gh`. Écrire « commit, push and gh writes ».
3. **`hooks/test_session_start_recap.py:6-8` et `:21`** : la docstring dit que le faux binaire est branché par `JAM_ORCA_BIN` (il l'est aussi par le `PATH`, `test_cli_found_on_path`) et donne `Run: python3 test_session_start_recap.py`, quand les autres fichiers donnent `python3 -m unittest hooks.test_…`. Aligner les deux phrases.
4. **`.claude-plugin/marketplace.json:6`** : `description` est au premier niveau ; la référence des marketplaces la range sous `metadata`. À confirmer par le point 5 de la recette (`claude plugin validate .`) ; si un avertissement tombe, la déplacer sous `metadata`.
5. **Hors périmètre, pour K1-2** : `hooks/guard_coordinator.py:105` et `hooks/session_start_recap.py:21` désignent `docs/process/README.md`, chemin propre à jam ; le plan renvoie ce point à K1-2 (hook de reprise qui désigne le process du plugin). Rien à faire ici.

RELECTURE : OK
