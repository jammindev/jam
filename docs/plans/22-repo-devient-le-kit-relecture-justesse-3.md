# Relecture A (justesse), tour 3 — #22 Le repo devient le kit

Relecteur A, contexte neuf. Périmètre : tout le diff non commité (suppressions de l'app, `.gitignore`, `ci.yml`, `hooks/`, `scripts/`, `.claude-plugin/`, fiche concept, docs du rédacteur), plan hors relecture. Référentiel : plan validé et ses ajustements a à c, section K1-1 de `cadrage-kit-issues.md`, ADR 0016.

**Tests** : `python3 -m unittest` à la racine : 135 tests, `OK` (41,8 s).

## Bloquant

Aucun.

## À corriger

1. **`hooks/guard_outbound.py:265-287` (`gh_writes`) : une écriture `gh` dans une substitution de commande entre guillemets, ou entre accents graves, passe sans accord.**
   `shlex` garde `"$(…)"` en un seul mot, et `strip_wrappers` jette en plus le mot d'une affectation. Constaté en suivant le découpage :
   - `PR_URL="$(gh pr create --fill)"` : un seul mot `PR_URL=$(gh pr create --fill)`, retiré comme affectation, donc rien n'est analysé : **passe** ;
   - `echo "$(gh pr merge 12)"` : le mot `$(gh pr merge 12)` n'est qu'un argument de `echo` : **passe** ;
   - ``echo `gh pr merge 12` `` : le premier mot est `gh` précédé d'un accent grave, ce qui n'est pas `gh` : **passe** (même chose pour ``X=`gh pr merge 1` ``).

   Récupérer l'URL d'une PR par `URL="$(gh pr create …)"` est une forme courante chez un agent. La garde git, elle, cherche dans le texte brut : `"$(git push)"` est bien refusé. Côté `gh`, l'écart avec `git` n'est donc pas voulu, et la docstring (« NOT covered », l. 22-24) ne le mentionne pas, alors que la garde du coordinateur le documente pour ses propres écritures (`guard_coordinator.py:48`). Le critère de fin (« une écriture `gh` sans accord est refusée ») est tenu pour la forme simple, pas pour celle-ci.

   **Correction attendue** : dans `gh_writes`, analyser aussi le texte de chaque mot qui contient `$(` ou un accent grave, avant `strip_wrappers` pour ne pas perdre les affectations. Par exemple `found.extend(gh_writes(token.replace("`", "\n")))` : `$` et `(` sont déjà des séparateurs, et la récursion s'arrête puisque les mots internes ne contiennent plus la substitution. Ajouter à `GH_WRITES` : `PR="$(gh pr create --fill)"`, `echo "$(gh pr merge 1)"`, ``echo `gh pr merge 1` `` ; et à `GH_READS` : `echo "$(gh pr view 1)"`. Si la correction est écartée, il faut au minimum l'écrire dans la docstring (« NOT covered ») et dans la fiche concept (piège « garde-fou, pas un bac à sable »).

## Suggestions

1. **`hooks/guard_outbound.py:77-79, 188-193` : les préfixes qui prennent des options ou des arguments ne sont pas traversés.** `timeout 60 gh pr merge 1`, `env -i gh …`, `sudo -E gh …`, `nice gh …` et `… | xargs -n1 gh issue close` passent. La garde du coordinateur traite `xargs`, pas celle-ci. Ajouter au moins `xargs` et `timeout <n>`, ou les citer dans « NOT covered ».
2. **`hooks/guard_outbound.py:40-41, 296-297` : comportement repris du poste, hors périmètre (« comportements inchangés »), à noter pour une friction future.**
   - (a) L'exemption `/tmp/claude-*` ne regarde que le dossier courant : depuis le scratchpad, `git -C <vrai repo> push` ou `cd <vrai repo> && git push` passent.
   - (b) `git -c clé=valeur commit`, `git --no-pager push` et `git -C a -C b push` ne sont pas reconnus.
   - (c) Le `--dry-run` est cherché dans tout le reste de la commande : `git commit -m "doc: --dry-run"` passe.
3. **Écart déclaré, accepté : une commande non analysable qui contient `gh` est refusée** (`guard_outbound.py:269-271`). Effet de bord à connaître : un heredoc en français (apostrophe non fermée au sens du shell) qui cite `gh` est refusé sans accord, avec le libellé « gh (commande non analysable) ». C'est conservateur, donc acceptable ; une phrase dans la fiche aiderait un agent à comprendre le refus (passer par l'outil Write).
4. **`scripts/watch_cards.py:35-41` : la liste `orca worktree ps` tronquée n'est pas détectée**, alors que `launch_task.py` la refuse. Une carte au-delà de la liste n'est jamais surveillée, en silence. Sortir en 2 (ou au moins prévenir) si `truncated` est vrai, avec un test.
5. **`scripts/orca_cli.py:26-27, 44-45` : le message « CLI Orca introuvable : ni JAM_ORCA_BIN, … » est trompeur quand `JAM_ORCA_BIN` est posé mais non exécutable** (écart déclaré, comportement accepté). Il laisse croire que la variable est absente. Un message propre à ce cas (« JAM_ORCA_BIN ne désigne pas un exécutable »), toujours sans chemin, ferait gagner du temps. Cosmétique.
6. **`hooks/test_session_start_recap.py:396-402` (`test_cli_too_slow`) : la borne de 2 s couvre le démarrage de Python, cinq appels git et le délai réel de 1 s.** Il reste environ 0,7 s de marge sur un runner chargé, la situation même qui a fait porter les autres tests à 5 s. Le risque est un test instable en CI. Une borne à `REAL_TIMEOUT + 1,5` s environ, ou une comparaison avec le temps de démarrage mesuré d'un hook sans Orca, tiendrait mieux.

## Écarts déclarés par l'implémenteur : jugement

| Écart | Verdict |
|---|---|
| `owner.name` « jammindev » dans `marketplace.json` | Accepté : le schéma d'une marketplace exige `owner` ; c'est le nom de l'organisation, déjà présent dans l'URL `repository`. Test présent (`test_plugin.py:49`). |
| `launch_task.py` prend l'id du worktree dans la réponse de `orca worktree create`, sans relire `ps` | Accepté : un appel de moins et pas de course entre création et relecture. L'id absent ou vide est traité (code 2, test `test_created_worktree_without_id`). La forme de la réponse repose sur la fixture, contrat du plan ; non vérifiable ici contre la vraie CLI (lancement non reproduit en recette). |
| `watch_cards` sort en 2 si le projet n'a aucune carte ; intervalle de 30 s par défaut | Accepté : évite une veille infinie sur une faute de frappe. Test `test_unknown_project`. |
| `launch_task` refuse de créer si la liste `ps` est tronquée | Accepté : évite un worktree jumeau. Test présent. |
| Codes de sortie 0/1/2 | Accepté : refus voulu (1) distinct d'une panne (2), tests à l'appui. |
| `gh` seul, `gh --help` ou `gh pr` passent comme lecture ; commande illisible contenant `gh` refusée | Accepté (voir suggestion 3). |
| `gh api graphql` avec `--input` ou un champ `-F @fichier` compte comme écriture | Accepté : une requête invisible ne peut pas être vérifiée. Sept formes testées. |
| Résumés de compaction ignorés comme messages du mainteneur | Accepté et utile : sans ce filtre, le « Continue the conversation… » du résumé ouvrait la garde. Tests sur les deux drapeaux, seuls et ensemble, et dans le cas du feu vert remonté par la carte. |
| `JAM_ORCA_BIN` non exécutable = CLI introuvable, sans repli | Accepté (voir suggestion 5 pour le message). |
| Première ligne « [jam] Reprise de contexte » au lieu d'un titre `##` | Accepté : la marque doit ouvrir le message. Cosmétique. |
| `scripts/fixtures/fake_orca.py` et `scripts/fixtures/__init__.py` ajoutés | Accepté : le faux binaire commun aux trois tests des scripts, et un paquet sans test que la découverte traverse sans effet. |
| Délai de la CLI Orca à 5 s dans les tests qui attendent une réponse, 1 s gardée pour le test de lenteur | Accepté ; voir suggestion 6 sur la borne du test de lenteur. |

## Vérifié sans constat

- **Retrait de l'app** : `apps/`, `packages/` et les sept fichiers de la racine sont supprimés, et rien d'autre. `.gitignore` est conforme au plan. `ci.yml` lance `python3 -m unittest` sur `ubuntu-latest`, avec `contents: read` et un délai maximal de 10 minutes. Sous Python 3.12 (Ubuntu 24.04), une découverte vide ferait échouer le job.
- **Câblage** : `hooks.json` a l'enveloppe `hooks`, les quatre événements et les matchers du plan, et des commandes `python3 "${CLAUDE_PLUGIN_ROOT}/hooks/…"` vers des fichiers qui existent. `plugin.json` n'a ni `version` ni `author`. Tout est testé.
- **Cas du feu vert remonté par la carte** : `test_green_light_relayed_by_a_card_is_not_an_approval` refuse le merge, y compris après une compaction, puis le laisse passer sur « ok merge ».
- **`orca_cli`** : ordre de recherche, lien cassé, `JAM_ORCA_BIN` vide, délai dépassé, JSON illisible, formes inattendues, message sans chemin. Tout est testé, avec `APP_BIN` remplacé pour ne pas dépendre du poste.
- **`launch_task`** : refus au plafond global et au plafond du projet, chacun à sa limite exacte, sans autre appel. Terminal sans agent ou déconnecté non compté. Worktree réutilisé (même `repoId` seulement). Brief envoyé à l'identique, avec `$(…)` et guillemets. Brief non envoyé si l'agent n'est pas prêt. Rôle filtré par `[a-z-]+`.
- **`watch_cards`** : `▶`→`⏸` et `⛔` réveillent. `▶ a`→`▶ b` et un `⏸` hors du premier segment ne réveillent pas. Un `✓` ou un `💬` ajouté réveille. Une carte déjà en attente au lancement, la carte d'un autre projet et une carte `completed` sont ignorées. La sortie est 2 en cas d'échec, d'erreur ou de JSON illisible, avant ou pendant la veille.
- **Compatibilité Python 3.9** : pas de `match` ni d'annotations `X | Y` ; `shlex` avec `punctuation_chars` existe depuis 3.6.
- **Docs** : la fiche concept, le README (installation, `--plugin-dir`, ordre de recherche de la CLI), `02-ARCHITECTURE`, Q-055, `AGENTS.md` et les fiches historiques sont fidèles au code relu.

RELECTURE : CORRECTIONS (1)
