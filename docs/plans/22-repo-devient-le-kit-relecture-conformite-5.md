# Relecture — #22, axe B (conformité), tour 5

Relecteur B, contexte neuf. Lu : profil du relecteur (section Kit comprise), `AGENTS.md`, ADR 0016, plan validé `docs/plans/22-repo-devient-le-kit.md` (ajustements a, b, c compris), section K1-1 de `docs/plans/cadrage-kit-issues.md`. Relu en entier : `hooks/` (quatre hooks, `hooks.json`, cinq fichiers de tests, `__init__.py`), `scripts/` (`orca_cli.py`, `watch_cards.py`, `launch_task.py`, leurs tests, `fixtures/fake_orca.py`, `fixtures/__init__.py`, `fixtures/orca/*.json`), `.claude-plugin/plugin.json` et `marketplace.json`, `docs/concepts/plugin-et-hooks.md`, et le diff de `.github/workflows/ci.yml`, `.gitignore`, `README.md`, `AGENTS.md`, `docs/concepts/README.md`, des deux fiches historiques, de `02-ARCHITECTURE.md` et d'`OPEN-QUESTIONS.md`.

Tests : `python3 -m unittest` depuis la racine → **135 tests, OK** (44 s).

## Conformité au plan, au critère de fin et aux ADR

- **Retrait de l'app** : `apps/`, `packages/` et les fichiers racine de l'étape 1 sont supprimés (indexés), il ne reste aucun dossier `apps/` ni `packages/`, et aucun fichier non suivi n'y traîne. `.gitignore` : les deux blocs de l'app sont retirés, `__pycache__/` est ajouté, `CLAUDE.md` et `.claude/settings.local.json` sont gardés. CI : un seul job `ubuntu-latest` qui lance `python3 -m unittest`, `permissions: contents: read` et `timeout-minutes` gardés. Conforme.
- **Câblage** : `hooks.json` a l'enveloppe `hooks`, les quatre événements, les matchers et la forme de commande `python3 "${CLAUDE_PLUGIN_ROOT}/hooks/<fichier>"` du plan. `plugin.json` n'a ni `author` ni `version`. `marketplace.json` déclare un seul plugin, source `"."`. `test_plugin.py` vérifie tout cela. Conforme.
- **Garde de sortie unique** (annexe B, question 2) : refus par défaut de tout `gh` absent de la liste de lecture. La liste de lecture est exactement celle de l'annexe, l'exemption `/tmp/claude-*` ne vaut que pour commit et push, et `rtk`, `rtk proxy`, un chemin absolu et `-R`/`--repo` sont reconnus. Le cas du feu vert remonté par la carte est testé (refus, puis passage après « ok merge »), avec en plus la variante après compaction. La ligne `[jam] [état git]` est retirée du message lu. La garde du coordinateur ne garde pas les sorties : rien ne lui est retiré (ADR 0012, ADR 0016). Conforme.
- **Hooks génériques** : la marque `[jam]` ouvre chaque sortie (refus des deux gardes, ligne d'état git, récapitulatif, messages des scripts ; `orca_cli.NOT_FOUND` n'est jamais affiché seul, il est toujours inclus dans un message `[jam]`). Le binaire Orca est résolu dans le seul module `scripts/orca_cli.py`, dans l'ordre de l'ajustement a. `APP_BIN` est une constante que les tests remplacent. Le message « introuvable » ne cite aucun chemin, et un test le vérifie. Conforme aux ajustements a et b.
- **Scripts** : `watch_cards.py` et `launch_task.py` font ce que décrivent les étapes 7 et 8 du plan, et leurs tests couvrent la liste de cas du plan : réveil sur `⏸`, `⛔`, `✓` ou `💬` ; aucun réveil sur un `▶` ; carte déjà en attente au lancement, ou d'un autre projet, ignorée ; sortie 2 si la CLI échoue ; refus au plafond global et au plafond du projet après le seul `terminal list` ; terminaux sans agent ou déconnectés non comptés ; worktree existant réutilisé ; brief envoyé à l'identique ; `--role` limité à `[a-z-]+`.
- **Schéma de la CLI Orca** : versionné en exemples de sorties réduits aux champs lus (`scripts/fixtures/orca/*.json`), comme le prévoit le plan pour répondre à l'ADR 0017.
- **Docs du rédacteur** : section « L'app » retirée, « Installation » ajoutée (marketplace locale, `--scope user`, mise à jour par `git pull`, `--plugin-dir`, et l'effet « vaut pour tous les projets du poste », voulu par l'ADR 0016) ; ligne d'`AGENTS.md` mise à jour ; fiches de l'app marquées historiques sans être supprimées ; tableau des concepts ; Q-055 tranchée ; ligne « Distribution » de `02-ARCHITECTURE.md`. Conforme à l'étape 10.
- **Fiche concept** : au format de `docs/concepts/README.md` (cinq rubriques). Elle traite ce qu'est un plugin, pourquoi un hook tient ce qu'une consigne ne tient pas (RET-005), et les trois pièges que demande le plan (hooks en double, `CLAUDE_PLUGIN_ROOT` absent de l'outil Bash, accord lu sur le dernier message), plus la limite connue d'`orca terminal send` (question 3). Conforme.
- **Orca** : aucune reprise. Le plan dit « aucune brique reprise ni inspirée », et rien dans le diff ne ressemble à du code repris.

### Écarts déclarés par l'implémenteur : jugement

| Écart | Jugement |
|---|---|
| `owner.name` « jammindev » dans `marketplace.json` | **Admis.** Le schéma des marketplaces exige `owner` ; « jammindev » est le nom de l'organisation GitHub, déjà présent dans `repository` de `plugin.json`, que le plan exige. Aucune information nouvelle, et ce n'est pas un nom de personne. |
| `launch_task.py` prend l'id du worktree dans la réponse de `worktree create`, sans relire `ps` | **Admis.** Le plan faisait de la forme JSON de `create` un prérequis du brief, et la fixture `worktree-create.json` en est le contrat ; un appel de moins et pas de course entre la création et la relecture. Un id absent sort en 2 avant tout `terminal create`, et c'est testé. La recette sur Orca réel (non reproduite par le recetteur) confirmera le champ. |
| Ajouts de sûreté : carte absente → 2, intervalle de 30 s par défaut, refus sur liste `ps` tronquée, codes 0/1/2 | **Admis.** De petits ajouts qui servent le but (pas de veille infinie sur une faute de frappe, pas de worktree jumeau). Ils sont documentés dans les docstrings et testés. Pas de sur-ingénierie. |
| `gh`, `gh --help` et `gh pr` seuls lus comme lectures ; commande illisible contenant `gh` refusée | **Admis.** L'aide ne sort rien ; le refus d'une commande illisible suit le refus par défaut (question 2). |
| `api graphql` avec `--input` ou `-F …=@fichier` → écriture | **Admis.** Une requête que la garde ne peut pas lire n'est pas prouvée sans `mutation` : refus par défaut. |
| Écritures `gh` dans une substitution de commande, lignes continuées réunies | **Admis.** Ce sont des formes courantes (la forme multiligne de la doc REST de GitHub, `PR="$(gh pr create)"`), toutes citées dans la docstring et testées. |
| Résumés de compaction ignorés | **Admis.** C'est le cas du feu vert remonté par la carte qui se prolonge après une compaction ; le cas est testé et décrit dans la fiche concept. |
| `JAM_ORCA_BIN` non exécutable → introuvable, sans repli | **Admis.** Un choix explicite qui échoue est signalé au lieu d'être remplacé en silence. C'est documenté et testé. |
| Première ligne du récapitulatif « [jam] Reprise de contexte » au lieu d'un titre `##` | **Admis.** La marque doit ouvrir le message (« commence par `[jam]` », plan §2). |
| `scripts/fixtures/fake_orca.py` et `scripts/fixtures/__init__.py` ajoutés | **Admis.** Un seul faux binaire partagé, écrit par chaque test dans un dossier temporaire, comme le demande le plan ; le `__init__.py` est nécessaire à l'import par la découverte des tests. |
| Délai de la CLI porté à 5 s dans les tests du récapitulatif qui attendent une réponse, 1 s gardée pour le test de lenteur | **Admis.** Le délai réel du hook (1 s) reste testé là où il compte ; le reste est une marge contre un runner de CI chargé. Le hook n'est pas modifié. |

## Repo public

Aucun nom de personne, chemin propre au poste ni nom d'un autre projet dans `hooks/`, `scripts/` ni `.claude-plugin/`, ni dans les docs modifiées (recherche sur le prénom et le nom du mainteneur, `/Users/`, les noms de ses autres projets et son domaine). Les chemins des tests sont fictifs (`/Users/testhome`, `/Users/x/…`, `/work/…`). `/Applications/Orca.app/…` est l'emplacement standard, admis. Pas de secret.

## Constats

### Bloquant

Aucun.

### À corriger

Aucun.

### Suggestions

1. **`hooks/guard_outbound.py:23-26`, docstring « NOT covered »** : `gh` lancé par un autre programme n'est pas reconnu (`xargs gh pr merge`, `timeout 10 gh pr merge 1`, `nice gh …`, `find … -exec gh …`) : seuls `rtk`, les affectations, quelques mots-clés du shell et `bash -c` sont traversés. C'est une forme rare, et la garde est un garde-fou, pas un bac à sable. Correction attendue : l'ajouter à la liste « NOT covered », par exemple « gh launched by another program (xargs, timeout, nice, find -exec…) ». Le même lecteur peut noter que `git -c k=v commit` échappe aux expressions de commit et de push, comportement repris du poste (annexe A).
2. **`hooks/test_guard_outbound.py:2`, docstring** : « the PreToolUse guard of commit and push » ne dit plus tout ; la garde couvre aussi les écritures `gh`. Correction attendue : « the single outbound guard: commit, push and gh writes ».
3. **`hooks/test_session_start_recap.py:21`** : « Run: python3 test_session_start_recap.py » diffère des autres fichiers de tests. Correction attendue : « Run: python3 -m unittest hooks.test_session_start_recap ».
4. **`hooks/test_guard_outbound.py:269`, commentaire** : « A gh command that is neither on the read list nor parseable » couvre deux cas différents (`gh issue create --title 'l`, illisible, et `gh alias set …`, lisible mais hors de la liste de lecture). Correction attendue : un commentaire par cas.

RELECTURE : OK
