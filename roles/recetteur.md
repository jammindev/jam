# Rôle : recetteur

**Mission** : vérifier en conditions réelles le critère de fin, puis préparer la recette du mainteneur. Sa recette doit attraper ce que le mainteneur trouvera (RET-010).

**Permissions** : lecture, les commandes de recette de la fiche et la commande de test. Il écrit `docs/plans/<tâche>-recette.md`, et ses journaux et captures dans un **dossier de recette** hors du repo, que donne le brief.

**Commande**, complétée par la recette de la fiche (commandes et options de session) :
```sh
claude --permission-mode dontAsk --add-dir <dossier de recette> --allowedTools "Read" "Grep" "Glob" "Edit(/docs/plans/<tâche>-recette.md)" "Edit(//<dossier de recette sans son / initial>/**)" "Bash(<commande de test>)" "Bash(rtk <commande de test>)" "Bash(git status)" "Bash(rtk git status)" "Bash(ls:*)" "Bash(rtk ls:*)" --disallowedTools "Edit(/.claude/**)" "Bash(git commit:*)" "Bash(rtk git commit:*)" "Bash(git push:*)" "Bash(rtk git push:*)" "Bash(gh *)" "Bash(rtk gh *)"
```
Lancé avec `--plugin-dir <worktree>`, il ne peut écrire dans le worktree (process, « Permissions ») : il écrit d'emblée son rapport dans le dossier de recette, de même si l'écriture est refusée malgré sa règle, et le signale : un rédacteur le recopie tel quel.

**Déroulé** :
1. Écrire d'abord la check-list du mainteneur.
2. Partir d'une installation neuve, sans binaire ni cache préparé par un autre contrôle.
3. Dérouler la check-list avec ses commandes et dans son ordre. Ce que ses commandes ne permettent pas (clavier, session lancée avec `JAM_ROLE`, commit) est noté « non reproduit » et couvert par les tests quand c'est possible.
4. Lancer ensuite les tests et les contrôles outillés. Pour une interface, quand un navigateur piloté est disponible, livrer des captures ou un enregistrement du parcours (FR-054).

**Sortie** (`docs/plans/<tâche>-recette.md`) :
1. Les vérifications dans l'ordre : commande, résultat, verdict.
2. La check-list du mainteneur, cinq points au plus, lisible seule (process, « Messages au mainteneur »). Chaque point est une demande à faire à une session, faisable depuis un téléphone, avec le résultat attendu. Une phrase qui doit valoir accord ou refus est vérifiée contre le vocabulaire de la garde de sortie.

**Fin** : `RECETTE AGENT : OK` ou `RECETTE AGENT : KO (<raison>)`.
