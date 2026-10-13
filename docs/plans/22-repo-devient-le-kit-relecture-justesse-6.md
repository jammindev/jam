# Relecture #22 — axe A, justesse, tour 6

> Relecteur A (justesse), contexte neuf. Lu : profil du relecteur (section Kit comprise), `AGENTS.md`, ADR 0016, plan `22-repo-devient-le-kit.md` (dont « Ajustements validés après le feu vert plan »), section K1-1 de `cadrage-kit-issues.md`. Relu en entier : `hooks/` (quatre hooks, `hooks.json`, cinq fichiers de tests), `scripts/` (`orca_cli.py`, `watch_cards.py`, `launch_task.py`, leurs tests, `fixtures/fake_orca.py`, `fixtures/orca/*.json`), `.claude-plugin/`, `.github/workflows/ci.yml`, `.gitignore`, `docs/concepts/plugin-et-hooks.md`, et le diff des docs modifiées (`README.md`, `AGENTS.md`, fiches concept, `02-ARCHITECTURE.md`, `OPEN-QUESTIONS.md`). Aucune relecture d'un tour précédent lue.

## Tests

`python3 -m unittest` à la racine : **137 tests, OK** (41,9 s).

## Écarts au plan déclarés par l'implémenteur

Tous acceptables sur l'axe justesse :

- `owner.name` dans `marketplace.json` : champ exigé par le schéma des marketplaces ; c'est le nom de l'organisation GitHub, déjà présent dans `repository`.
- Id du worktree pris dans la réponse de `orca worktree create` : plus simple qu'une relecture par `ps`, et sans course entre la création et la relecture. Le contrat est la fixture `worktree-create.json` (`result.worktree.id`), testée (`test_creates_worktree_then_starts_role`, `test_created_worktree_without_id`). Le lancement réel n'est pas reproduit en recette (plan) : seul le contrat fourni par l'orchestrateur fait foi.
- Ajouts de sûreté (`watch_cards` en 2 sur projet sans carte ou liste tronquée, 30 s par défaut ; `launch_task` qui refuse sur liste tronquée et sort en 2 sur brief illisible ; codes 0/1/2) : corrects, testés, cohérents avec les docstrings.
- `gh`, `gh --help`, `gh pr` en lecture ; commande illisible contenant `gh` refusée ; `api graphql` avec `--input` ou `-F …=@…` refusé ; substitutions de commande reconnues ; continuations de ligne réunies : corrects et testés (`GH_WRITES`, `GH_READS`).
- Résumés de compaction ignorés : correct, testé dans les deux sens (après accord, après refus) et sur le cas du feu vert remonté par la carte.
- `JAM_ORCA_BIN` non exécutable = introuvable sans repli : correct, testé (`test_explicit_variable_not_executable_is_not_replaced`, `test_cli_missing`).
- Première ligne « [jam] Reprise de contexte » ; `fake_orca.py` et `fixtures/__init__.py` ; délais de 5 s / 1 s dans `test_session_start_recap.py` : corrects.

## Constats

### Bloquant

Aucun.

### À corriger

Aucun.

### Suggestions

1. **`hooks/guard_outbound.py:111-164`, sortie d'une commande `!` lue comme un accord** (comportement repris du poste, d'où le classement ; c'est la suggestion la plus importante de ce rapport). Quand le mainteneur lance une commande `! …` dans la session, Claude Code écrit dans le transcript deux messages `user` qui ne sont ni `isMeta` ni des résultats d'outil : `<bash-input>…</bash-input>` puis `<bash-stdout>…</bash-stdout><bash-stderr>…</bash-stderr>` (de même `<local-command-stdout>` pour une commande `/…`). Le hook retire le bloc `<local-command-caveat>` mais garde ces messages, et les prend pour le dernier mot du mainteneur. Exemple concret : `! git status` affiche « nothing to commit, working tree clean » ou « Changes not staged for commit » ; « commit » est dans le vocabulaire d'accord, donc un `git commit`, un `git push` ou un `gh pr merge` passe sans accord. Correction attendue : ignorer (`continue`) un message dont le texte, une fois nettoyé, commence par `<bash-input>`, `<bash-stdout>`, `<local-command-stdout>` ou `<command-name>` ; un test par forme, dans `noise()` de `hooks/test_guard_outbound.py`, sur le modèle des résumés de compaction. À défaut, la limite est à citer dans la fiche concept (piège « L'accord est lu sur le seul dernier message »). À soumettre au mainteneur : c'est un faux accord dans la seule garde de sortie, et la correction tient en quelques lignes.

2. **`hooks/guard_outbound.py:339-352`, un plantage laisse passer.** Toute exception non prévue dans `check_outbound` ou `last_user_message` sort en code 1 avec une trace, que Claude Code traite comme une erreur non bloquante : la commande s'exécute. Formes qui plantent : entrée JSON qui n'est pas un objet (`[]`), `tool_input` ou `cwd` d'un autre type, ligne de transcript qui est un tableau JSON ou un `message` en chaîne, bloc `text` à `None`. Claude Code n'envoie pas ces formes, d'où la suggestion ; mais la docstring et la fiche disent « un transcript illisible bloque ». Correction attendue : dans `main()`, envelopper `check_outbound` dans un `try/except Exception` qui bloque avec un message `[jam]` (seulement si une écriture a été reconnue, sinon laisser passer), et faire `continue` quand `event` ou `message` n'est pas un `dict` dans `last_user_message`. Un test : ligne de transcript `[1, 2]` après un refus, `git commit` → refusé et sans trace.

3. **`hooks/guard_outbound.py:42-43`, formes de `git` non vues par les regex** (comportement repris du poste). Passent sans accord : `git -c commit.gpgsign=false commit -m x` (forme qu'un agent emploie quand la signature échoue), `git --no-pager push`, `git -C "/chemin avec espace" commit`. Correction attendue : accepter une suite d'options globales entre `git` et le verbe, par exemple `\bgit\b(?:\s+(?:-[Cc]\s+(?:"[^"]*"|'[^']*'|\S+)|--[\w-]+(?:=\S+)?))*\s+commit\b`, avec un test par forme dans `test_command_forms_blocked` ; ou, a minima, les citer dans la section « NOT covered » de la docstring.

4. **`hooks/guard_outbound.py:207-235`, requête GraphQL hors de vue par une variable ou une substitution.** `gh api graphql -f query="$(cat q.graphql)"` ou `-f query="$Q"` passe comme une lecture : le mot « mutation » n'est pas dans le texte de la commande, alors que `-F query=@q.graphql`, qui revient au même, est refusé. Correction attendue : dans la branche `graphql`, compter comme caché un champ dont la valeur contient `$` ou `` ` `` ; ou citer cette forme dans la docstring à côté de `@fichier`.

5. **`hooks/guard_outbound.py:80` et `:191-196`, enveloppes de commande non reconnues**, à citer dans « NOT covered » ou à traiter : `timeout 60 gh pr merge 1`, `xargs gh pr merge`, `nice gh …`, `env -i gh …` et `sudo -u x gh …` (option avant `gh`), `find … -exec gh … ;`, et une redirection placée avant la commande (`>out.txt gh pr merge 1`, où `out.txt` devient le nom de la commande). La garde du coordinateur traite déjà `xargs` et `find -exec` : la même logique peut servir ici.

6. **`hooks/guard_outbound.py:238-265`, `gh <commande> <sous-commande> --help` refusé.** `gh pr merge --help` (lecture de l'aide, fréquente avant un premier usage) est refusé sans accord alors que `gh --help` et `gh pr` passent. Correction attendue : `--help` ou `-h` n'importe où dans les arguments → lecture, avec un cas dans `GH_READS`.

7. **`scripts/watch_cards.py:57-59` et `:79-83`, réveil répété par un `✓` resté sur la carte.** Le test s'appelle `test_wakes_on_green_light_or_message_added` et le plan parle d'un segment « ajouté », mais le code réveille à **tout** changement du commentaire tant qu'un segment `✓` ou `💬` y figure. Si un `✓ feu vert plan` reste sur la carte, chaque passage `▶ implémenteur` → `▶ relecteur` → `▶ recette` réveille le coordinateur. Correction attendue : comparer l'ensemble des segments `✓`/`💬` avant et après, et ne réveiller que sur un segment nouveau ; test : `▶ a · ✓ x` → `▶ b · ✓ x` sans réveil. Si la convention du process est de retirer le segment une fois relayé, le comportement actuel suffit : le dire dans la docstring.

8. **Cas limites non testés** (profil : au moins un par fonction exposée) :
   - `scripts/watch_cards.py:99-100` : `--interval 0` ou négatif → sortie 2 marquée `[jam]`, sans appel à la CLI ;
   - `scripts/launch_task.py:51-55` et `:102-104` : `--cap 0` refusé en 2 sans appel ; réponse de `terminal create` sans `handle` → sortie 2, ni `wait` ni `send` ;
   - `scripts/orca_cli.py:67-68` : binaire présent mais non lançable (`OSError`) → `OrcaError` ; par exemple un fichier exécutable sans shebang valide.

9. **`hooks/git_context.py:68-71`, faux « worktree secondaire » sous un lien symbolique** (comportement repris du poste). `--git-common-dir` relatif est joint au `cwd` reçu, non résolu, puis comparé à `--absolute-git-dir`, résolu par git : dans un repo ouvert par `/tmp/…` sur macOS (`/tmp` → `/private/tmp`), le worktree principal est signalé secondaire. Le test contourne le cas par `realpath` (`test_git_context.py:26-28`). Correction attendue : comparer `os.path.realpath` des deux côtés, avec un test sur un lien symbolique vers le repo.

10. **`hooks/guard_outbound.py:310-311`, exemption du dossier de session sur le seul `cwd`** (comportement repris du poste, exemption gardée par la question 6 du plan). Depuis un `cwd` sous `/tmp/claude-*`, `git -C ~/vrai-repo push` ou `cd ~/vrai-repo && git push` passent sans accord. À citer au moins dans la docstring.

11. **`scripts/watch_cards.py:15-19`** (cosmétique) : la sortie 130 sur Ctrl+C n'est pas dans la liste des codes de sortie de la docstring.

RELECTURE : OK
