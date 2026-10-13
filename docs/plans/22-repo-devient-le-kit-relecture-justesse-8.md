# Relecture A (justesse), tour 8 : issue #22, changements d'avant recette

Périmètre : les changements faits à la demande du mainteneur avant sa recette (« ok go pour tes suggestions », 2026-10-11 22:04) : lecture de l'accord (commandes `!` et `/`), plantage de la garde, options globales de git, docstrings, fiche `docs/concepts/plugin-et-hooks.md`.

Lu en entier : `hooks/guard_outbound.py`, `hooks/test_guard_outbound.py`, `docs/concepts/plugin-et-hooks.md` ; docstrings de `hooks/git_context.py`, `hooks/test_session_start_recap.py`, `scripts/watch_cards.py` (confrontées au code qu'elles décrivent).

Tests : `python3 -m unittest` à la racine, **141 tests, OK** (45 s).

## Vérifications

### (1) Commandes `!` et `/`

- Les cinq balises (`<bash-input>`, `<bash-stdout>`, `<bash-stderr>`, `<local-command-stdout>`, `<local-command-stderr>`) sont testées dans les deux sens (`test_noise_after_approval_is_skipped`, `test_noise_after_refusal_does_not_approve`). Le second sens est une vraie preuve : chaque texte de bruit porte un mot d'accord (« nothing to commit », « To push… », « ok », « commit hook failed », `git push --dry-run`) et passerait si le message n'était pas écarté.
- Commande `/` : `test_slash_command_reads_its_arguments` prouve les trois comportements, avec `<command-message>` en tête ou non : un accord donné avant devient périmé (`ok` puis `/simplify` est refusé) ; le nom ne compte pas (`/merge 12`, et `<command-message>merge is running…` en tête, sont refusés) ; les arguments comptent (`/simplify ok commit` après « non merci » passe). La commande locale `/model` suivie de sa sortie est refusée, comme le disent la docstring et la fiche.
- Accord périmé ou faux accord par ces chemins : l'ordre des tests (caveat retiré, puis `LOCAL_COMMAND.match` sur le texte nettoyé, puis `SLASH_COMMAND.match`) ne laisse pas un nom de commande ou une sortie servir d'accord. Le seul chemin vers un accord ancien est l'écart d'un message `!`, qui n'ouvre pas de tour : c'est voulu.

### (2) Plantage

- `matched = git_actions(…)` puis `matched += gh_writes(…)` : si `gh_writes` lève, `+=` n'a pas eu lieu et `matched` garde le git. Prouvé par `test_crash_in_gh_reading_keeps_the_git_write`, qui remplace `gh_writes` par une fonction qui plante (git → refus « plant », pas de Traceback ; `git status` → passe).
- Plantage dans la lecture de l'accord : refus pour git et pour gh (`test_crash_while_reading_the_approval_blocks`, bloc texte à `null`) ; sans écriture reconnue, le transcript n'est pas lu.
- `fail()` et `sys.exit(0)` lèvent `SystemExit`, que `except Exception` ne rattrape pas : le verdict n'est pas avalé. `RecursionError` et `MemoryError` sont bien des `Exception`.
- Lignes non-dict (`[1, 2]`, message en chaîne) : écartées, testées dans les deux sens.

### (3) Options globales de git

- `GIT_VALUE` : chaque alternative commence par un caractère distinct (`"`, `'`, `\`, autre), un seul caractère par tour pour la dernière : pas de retour arrière exponentiel. `--git-dir <v>` et `--[\w-]+` se recouvrent, mais la branche perdante échoue au caractère suivant : coût linéaire.
- Formes bloquées testées : `-C`, `-c` (clé=valeur nue, entre apostrophes, entre guillemets dans la valeur), `~/"a b"`, `/a\ b`, `--no-pager`, `-P`, `--git-dir=`, `--git-dir <v>`, `--work-tree=`, enchaînement de plusieurs options. Faux positifs testés : `git --no-pager log --grep commit`, `git -C x status`, `git -c core.pager=cat diff`, `git -c alias.ci=commit status` ; `--dry-run` derrière une option globale passe.
- J'ai cherché d'autres faux positifs (`git -C repo stash push`, `git -C push status`, `git -c x=y log … | grep push`) : aucun ne correspond, un verbe autre qu'une option casse la chaîne.

### (4) et (5) Docstrings et fiche

- Docstring de `guard_outbound.py` : fidèle au code (balises écartées, `/` réduit à ses arguments, options globales, `git --help commit` refusé parce que `--help` se lit comme option globale, `/model` qui coûte un refus, codes de sortie et plantage).
- `git_context.py` (« NOT covered » : cwd joint tel quel, git dir résolu), `test_session_start_recap.py` (le faux binaire ne répond qu'aux deux appels exacts, journalise, HOME isolé), `watch_cards.py` (premier segment ⏸/⛔, tout segment ✓/💬, réveil sur changement, carte `completed` ignorée, codes 0/2/130) : conformes au code.
- Fiche, pièges « accord » et « plantage » : conformes au code et à la docstring.

## Constats

### Bloquant

Aucun.

### À corriger

Aucun.

### Suggestions

1. **`hooks/guard_outbound.py:213`** : un message n'est écarté que si son texte nettoyé *commence* par une balise de commande. Un message qui mêlerait les deux, des mots du mainteneur puis une balise, ou l'inverse, serait mal lu : avec la balise en tête, il serait écarté en entier et un accord plus ancien vaudrait (« ok », puis `<bash-stdout>…</bash-stdout>` suivi de « attends » : passe) ; avec la balise après, la sortie serait lue comme sa parole (« non merci », puis `<bash-stdout>nothing to commit</bash-stdout>` : passe). Claude Code écrit ces messages à part, donc le cas est théorique. Correction possible : retirer les blocs `<bash-…>…</bash-…>` et `<local-command-std…>…</…>` comme les `<system-reminder>`, puis écarter le message s'il est vide. Cela couvre les deux ordres sans rien changer aux cas testés. À défaut, le citer dans « NOT covered ».
2. **`hooks/test_guard_outbound.py`** : trois branches ou formes du code nouveau n'ont pas de test.
   - Une commande `/` sans balise `<command-args>` (`else ""`, `guard_outbound.py:217`).
   - `-p` en minuscule (seul `-P` est testé ; `re.IGNORECASE` rend la classe `[pP]` redondante).
   - `--work-tree <chemin>` avec une espace (seul `--work-tree=` est testé).

   Un cas chacun dans `test_slash_command_reads_its_arguments` et `test_command_forms_blocked` suffit.

RELECTURE : OK
