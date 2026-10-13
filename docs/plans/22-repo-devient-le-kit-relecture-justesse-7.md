# Relecture A (justesse), tour 7 : issue #22, changements demandés avant la recette

Périmètre : les changements demandés par le mainteneur (« ok go pour tes suggestions », 2026-10-11 22:04, session du coordinateur) :
- `hooks/guard_outbound.py` et `hooks/test_guard_outbound.py`, lus en entier ;
- les docstrings de `hooks/test_session_start_recap.py`, `hooks/git_context.py` et `scripts/watch_cards.py` ;
- la fiche `docs/concepts/plugin-et-hooks.md`.

Tests : `python3 -m unittest` à la racine donne 139 tests, OK (45 s).

Le profil ne permet que `python3 -m unittest` : je n'ai pas pu lancer le hook sur des commandes de sonde. Les constats sur les expressions régulières viennent donc d'une lecture pas à pas, que je détaille à chaque fois.

## Ce qui est juste

- **(1) Commandes `!` et `/`.** `LOCAL_COMMAND.match` porte sur le texte nettoyé : les balises caveat, system-reminder et « The user sent a new message while you were working » ont déjà été retirées, puis le texte passe par `strip()`. Un `!` lancé pendant que l'agent travaille est donc lui aussi écarté. Les quatre formes sont testées dans les deux sens (`test_noise_after_approval_is_skipped`, `test_noise_after_refusal_does_not_approve`). Le cas qui a motivé le changement, « nothing to commit », y figure.
- **(2) Plantage.** Avec `fail()`, `SystemExit` remonte sans être pris par `except Exception`, et le `sys.exit(0)` d'un outil autre que Bash aussi. Un plantage pendant la lecture de l'accord, avec `matched` non vide, bloque avec un message `[jam]` et sans traceback. Le test est `test_crash_while_reading_the_approval_blocks` : un bloc texte `None` fait planter `join`, et le cas est vérifié pour git et pour gh. Le même test montre `git status` qui passe sans que le transcript soit lu. Les lignes JSON valides qui ne sont pas un événement (tableau, `message` en chaîne) sont ignorées dans les deux sens (`test_malformed_transcript_lines_skipped`). L'entrée invalide laisse passer (`test_invalid_input_allowed`).
- **(3) Options globales de git.** Les formes suivantes sont reconnues et testées : `-C` avec ou sans guillemets, `-c clé=valeur`, `-c 'clé=valeur avec espace'`, `--no-pager`, `-P`, `--git-dir=`, `--git-dir <valeur>` et un enchaînement de plusieurs options. Les faux positifs demandés passent : `git -c alias.ci=commit status`, `git -C x status`, `git -c core.pager=cat diff` et `git --no-pager log --grep commit`. Le `--dry-run` derrière une option globale passe aussi. Lecture pas à pas de `-c alias.ci=commit status` : `[^\s;|&]+` prend `alias.ci=commit` en entier, puis `\s+commit\b` bute sur `status`. Raccourcir la valeur exigerait un blanc qui n'existe pas, donc le retour en arrière ne trouve rien.
- **Cas déjà couverts.** Toute la suite gh (écritures, lectures, substitutions, continuations de ligne, dossiers de session) reste verte.
- **(4) Docstrings.** Celles de `git_context.py` (le lien symbolique), de `watch_cards.py` (premier segment ⏸/⛔, n'importe quel segment ✓/💬, `completed` exclu, réveil sur changement seulement, codes 0/2/130, liste tronquée) et de `test_guard_outbound.py` décrivent fidèlement le code.

## Constats

### À corriger

1. **Un tour ouvert par une commande `/` hérite de l'accord précédent.** Fichiers : `hooks/guard_outbound.py:73-76` et `:197`, `docs/concepts/plugin-et-hooks.md:39`.
   - **Le problème.** Une commande `/` qui lance un skill (`/code-review --fix`, `/simplify`, un skill du projet) ouvre un tour de l'agent. Une commande `!` ou une commande locale (`/model`) n'en ouvre pas. Or la garde saute aussi le message `<command-name>` d'un skill et lit l'accord sur le message tapé avant. Le prompt du skill, lui, arrive en `isMeta` et est déjà sauté.
   - **Scénario.** Le mainteneur écrit « ok push » et l'agent pousse. Plus tard, il tape `/code-review --fix`. Dans ce tour, l'agent applique les corrections puis committe et pousse : la garde laisse passer, parce que le dernier message lu est encore « ok push ».
   - **Pourquoi c'est un recul.** Avant ce changement, le message `<command-name>/code-review</command-name>…` était lu comme dernier message, sans mot d'accord, et la garde refusait. C'est exactement l'accord périmé que la garde doit attraper : « un accord explicite à chaque étape sortante ».
   - **Ce qui manque à la doc.** Les arguments d'une commande `/` (`<command-args>`) sont des mots du mainteneur, ce que la docstring nie (lignes 9-10 : « are not their words »). La fiche dit bien que l'accord est lu « sur le message tapé avant la commande », mais elle ne dit pas que cela vaut aussi pour un tour lancé par un skill.
   - **Correction attendue, à privilégier.** Ne plus sauter un message qui commence par `<command-name>`. Le lire comme le message du mainteneur, réduit au contenu de `<command-args>` : le nom de la commande ne compte pas, et `/merge` n'est pas un accord. Continuer à sauter `<bash-input>`, `<bash-stdout>` et `<local-command-stdout>`, qui n'ouvrent pas de tour.
   - **Tests à adapter.** Sortir « slash command name » de `noise()`. Ajouter un test : après « ok », `<command-name>/simplify</command-name><command-args></command-args>` bloque, et `<command-args>ok commit</command-args>` passe.
   - **Coût.** Après une commande locale comme `/model` tapée en plein travail de l'agent, un commit sera refusé jusqu'au message suivant. C'est un refus sûr et rare.
   - **Si le coordinateur garde le saut tel qu'il a été décidé.** Écrire au minimum la conséquence dans « NOT covered » et dans le piège de la fiche : un tour ouvert par un skill hérite de l'accord du message précédent.

### Suggestions

2. **Un `-c clé="valeur avec espace"` échappe à la garde.** Fichier : `hooks/guard_outbound.py:60`.
   - **Le problème.** `GIT_VALUE` n'accepte de guillemets qu'en tête de valeur. Prenons `git -c user.name="Prénom Nom" commit -m x`. La troisième branche prend `user.name="Prénom` et s'arrête au blanc. Ce qui suit, `Nom"`, n'est pas une option globale, et `\s+commit` ne trouve pas de prise : le commit passe sans accord. `git -C ~/"a b" commit` et `git -C /a\ b commit` échappent de la même façon.
   - **Pourquoi ça compte.** Un agent écrit naturellement cette forme quand l'identité git manque. Le test ne couvre que la forme entièrement entre guillemets (`'user.name=A B'`).
   - **Correction.** `GIT_VALUE = r"""(?:"[^"]*"|'[^']*'|\\.|[^\s;|&"'\\])+"""`, avec une seule classe de caractères par tour de boucle. La forme `[^…]+` imbriquée dans `+` provoquerait un retour en arrière exponentiel. Ajouter `git -c user.name="A B" commit -m x` à `test_command_forms_blocked`. À défaut, citer cette forme dans « NOT covered ».
3. **Un plantage dans `gh_writes` fait perdre un git déjà reconnu.** Fichiers : `hooks/guard_outbound.py:343-348` et `:391`.
   - **Le problème.** `outbound_actions` trouve d'abord `git commit`/`git push` par expression régulière, puis appelle `gh_writes`. Si cet appel lève une exception, la liste locale est perdue : dans `main`, `matched` vaut encore `[]` et la commande passe. Je n'ai trouvé aucun déclencheur réaliste ; le seul que je vois est une `RecursionError` sur des guillemets imbriqués à des centaines de niveaux.
   - **Pourquoi le noter.** La docstring promet qu'« a crash once a write is recognised blocks ».
   - **Correction.** Dans `main`, calculer les écritures git avant d'appeler `gh_writes` (`matched = git_actions(...)`, puis `matched += gh_writes(cmd)`). Autre option : nuancer la docstring.
4. **Balises voisines non couvertes.** Fichier : `hooks/guard_outbound.py:76`.
   - **Le problème.** Une sortie qui commencerait par `<bash-stderr>` ou `<local-command-stderr>` serait lue comme un message du mainteneur. Même chose si le format de Claude Code plaçait `<command-message>` avant `<command-name>`.
   - **Correction.** Les ajouter à `LOCAL_COMMAND`, sans frais. Ce n'est pas un recul : avant le changement, ces messages étaient déjà tous lus.
5. **Refus et trous à citer dans « NOT covered ».** Fichier : `hooks/guard_outbound.py:26-42`.
   - **Refus à citer.** `git --help commit` est refusé : `--help` est pris pour une option globale. C'est un refus sûr, à placer à côté de `gh … --help` dans « Refused although they only read ».
   - **Trou à citer.** Un alias git (`git ci`, `git -c alias.ci=commit ci`) n'est pas couvert, comme l'alias gh déjà cité.
6. **Une ligne trop longue.** Fichier : `hooks/test_session_start_recap.py:8`. La phrase « HOME points at the temp folder too… » a été collée à la ligne 7 et dépasse largement la longueur des autres lignes. Elle est à rejoindre et recouper.

## Bilan

La garde reste juste sur tout ce qu'elle couvrait déjà, et les points (2), (3) et (5) sont prouvés par des tests.

Le point (1) ouvre un trou réel : un tour lancé par un skill du mainteneur peut committer ou pousser sur l'accord du message précédent. C'est un recul par rapport à l'état d'avant.

RELECTURE : CORRECTIONS (1)
