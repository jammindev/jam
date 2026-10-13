# Relecture — #22, axe A (justesse), tour 4

Relecteur A, contexte neuf. Lus : profil du relecteur, `AGENTS.md`, ADR 0016, plan (y compris les ajustements validés), section K1-1 de `cadrage-kit-issues.md`, puis tout le diff : `hooks/`, `scripts/` (fixtures comprises), `.claude-plugin/`, `.github/workflows/ci.yml`, `.gitignore`, la fiche concept et les docs modifiées par le rédacteur.

Tests : `python3 -m unittest` → **135 tests, OK** (45 s).

## Constats

### Bloquant

Aucun.

### À corriger

**1. `hooks/guard_outbound.py:170-188` (`simple_commands`) : une continuation de ligne (`\` en fin de ligne) coupe la commande en deux, et une écriture `gh api` passe sans accord.**

`shlex` en mode posix lit `\`+saut de ligne comme un caractère échappé et rend le jeton `"\n"`. Or `simple_commands` traite tout jeton fait de caractères de `PUNCT` comme un séparateur, et `\n` en fait partie. Ce qui suit le `\` devient donc une autre commande. Exemple, la forme exacte des exemples « GitHub CLI » de la doc REST de GitHub, qu'un agent recopie volontiers :

```sh
gh api \
  --method POST \
  repos/o/r/issues \
  -f title=x
```

La garde voit d'abord `["gh", "api"]`, un `gh api` sans méthode ni champ, donc une lecture. Puis elle voit `["--method", "POST"]`, `["repos/o/r/issues"]` et `["-f", "title=x"]`, qui ne sont pas des commandes `gh`. Sans accord, la commande passe. Même chose pour `gh \` + saut de ligne + `pr merge 12`, ou `gh -R o/r \` + saut de ligne + `issue create …`. La regex des commandes git a le même défaut pour `git \` + saut de ligne + `commit`, une forme plus rare.

Ce n'est pas une forme exotique hors docstring : c'est la forme multiligne ordinaire d'un `gh api` en écriture, que l'annexe B demande de refuser.

*Correction attendue* : au début de `check_outbound`, réunir les lignes continuées avant toute analyse (`cmd = re.sub(r"\\\r?\n", " ", cmd)`). Cela couvre à la fois la regex git et `gh_writes`. Tests à ajouter :
- dans `GH_WRITES` : `"gh api \\\n  --method POST \\\n  repos/o/r/issues \\\n  -f title=x"` et `"gh \\\n  pr merge 1"` ;
- dans `GH_READS` : `"gh api \\\n  repos/o/r/pulls \\\n  --jq '.[].title'"` ;
- dans `test_command_forms_blocked` : `"git \\\n  commit -m x"`.

### Suggestions

**S1. `hooks/guard_outbound.py:199-235` : une requête GraphQL passée par une variable ou une substitution est lue comme une lecture.** `gh api graphql -f query="$(cat q.graphql)"` et `gh api graphql -f query="$Q"` passent sans accord, alors qu'on ne voit pas leur texte, comme avec `--input` ou `-F @fichier`. Deux corrections possibles : dans `hides_body`, compter comme cachée toute valeur qui contient `$` ou un accent grave ; ou citer ce cas dans le « NOT covered » de la docstring.

**S2. `hooks/guard_outbound.py:79-81, 23-26` : `xargs`, `timeout <n>` et `find -exec` masquent `gh`.** `gh pr list -q '.[].number' | xargs -n1 gh pr close` passe sans accord. La garde du coordinateur traite déjà `xargs` et `find -exec`, avec le même découpage. Reprendre ce traitement, ou citer ces trois enveloppes dans le « NOT covered » de la docstring.

**S3. `scripts/orca_cli.py:26-27, 44-45` : message trompeur quand `JAM_ORCA_BIN` est faux.** L'écart déclaré (« `JAM_ORCA_BIN` non exécutable = CLI introuvable, sans repli ») est juste. Mais le message affiché, « ni JAM_ORCA_BIN, ni orca dans le PATH, ni l'app Orca à son emplacement standard », affirme que le `PATH` et l'app ont été vérifiés, ce qui n'est pas le cas. Un mainteneur qui a Orca dans son `PATH` serait mis sur une fausse piste. Un message distinct suffit, du type « JAM_ORCA_BIN ne désigne pas un exécutable », toujours sans chemin.

**S4. `scripts/launch_task.py:110` : envoi du brief jamais essayé contre le vrai Orca.** Aucun point de la recette (1 à 5) ne lance `launch_task.py` contre le vrai Orca. Les fixtures sont le seul contrat. Deux points ne sont donc pas vérifiés :
- un brief qui commence par `-` (un front matter `---`, par exemple), passé en `--text <brief>`, pourrait être pris pour une option par la CLI d'Orca ;
- on ne sait pas si un brief de plusieurs lignes arrive dans le TUI de Claude Code comme un seul message.

À noter pour l'orchestrateur de tâche : un essai réel avec un brief de plusieurs lignes, sur un worktree jetable, lèverait le doute.

**S5. `hooks/guard_outbound.py:42-43` : un message de commit qui contient `--dry-run` passe sans accord.** Exemple : `git commit -m "docs: explique --dry-run"`. La regex de rejet cherche `--dry-run` dans tout le reste de la commande. Le comportement vient du poste, donc il est hors périmètre, à noter seulement.

**S6. `scripts/watch_cards.py:92-96` : cas limites de `--interval`.** `--interval nan` ou `inf` finissent en trace Python (`time.sleep`). Et aucun test ne couvre le refus de `--interval 0`, ni celui de `--cap 0` dans `launch_task.py`. Cela reste cosmétique.

## Écarts déclarés par l'implémenteur

Tous les écarts sont acceptés.

- **`owner.name` « jammindev » dans `marketplace.json`** : le schéma des marketplaces exige `owner`. C'est le nom de l'organisation GitHub, déjà public dans `repository`, pas celui d'une personne. Le test ne vérifie que la présence du champ. Accepté.
- **Id du worktree lu dans la réponse de `orca worktree create`, sans relire `ps`** : la fixture `worktree-create.json` fixe le contrat, et cela évite un appel ainsi qu'une course où `ps` ne listerait pas encore le worktree créé. Le test `test_created_worktree_without_id` couvre une réponse sans id. Accepté.
- **Sortie 2 si le projet n'a aucune carte, intervalle de 30 s par défaut, refus de créer si la liste `ps` est tronquée, codes de sortie 0/1/2** : ajouts de sûreté cohérents, testés (`test_unknown_project`, `test_truncated_worktree_list_refused`, `test_truncated_terminal_list_refused`). Accepté.
- **`gh` seul, `gh --help` et `gh pr` passent comme lectures ; une commande illisible qui contient `gh` est refusée** : `gh` sans sous-commande affiche l'aide ; le refus par défaut de ce qu'on ne sait pas lire va dans le sens de la question 2 du plan. Accepté.
- **`gh api graphql` avec `--input` ou un champ `-F @fichier` compté comme écriture** : accepté. Le même raisonnement devrait couvrir `$(…)` et `$VAR` (S1).
- **Écritures `gh` dans une substitution de commande reconnues** : vérifié sur `$(…)` entre guillemets et sur les accents graves. La récursion se termine, puisque chaque niveau retire une couche de guillemets. Accepté.
- **Résumés de compaction ignorés** : la garde remonte au dernier vrai message du mainteneur, ce qui est la règle. Le test du feu vert remonté par la carte couvre le cas avec compaction. Accepté.
- **`JAM_ORCA_BIN` non exécutable = CLI introuvable, sans repli** : accepté, avec un message à préciser (S3).
- **Première ligne du récapitulatif « [jam] Reprise de contexte »** : la marque est en tête, comme le veut le plan. Accepté.
- **`scripts/fixtures/fake_orca.py` et `scripts/fixtures/__init__.py`** : ils sont nécessaires à l'import `scripts.fixtures.fake_orca`, et la découverte des tests ne les prend pas pour des tests. Accepté.
- **Délai de 5 s pour la CLI dans les tests qui attendent une réponse, 1 s gardée pour le test de lenteur** : cela rend la suite robuste sur un runner chargé sans affaiblir le test de lenteur, qui mesure toujours moins de 2 s. Accepté.

RELECTURE : CORRECTIONS (1)
