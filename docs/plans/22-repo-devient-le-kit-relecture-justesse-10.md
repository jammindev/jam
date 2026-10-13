# Relecture de l'issue #22, axe A (justesse), tour 10

Périmètre : la négation qui vaut refus dans la garde de sortie (décision du mainteneur, « Ok negation feu vert recette », 2026-10-12 21:52, session du coordinateur). Fichiers relus : `hooks/guard_outbound.py` (`NEGATION` l. 114-126, `check_approval` l. 394-418, docstring l. 13-16, 46-47 et 53-57), `hooks/test_guard_outbound.py` (tests de négation, l. 126-178), `docs/concepts/plugin-et-hooks.md` (paragraphe sur l'accord, l. 39).

Note de méthode : le brief demandait de vérifier les corrections du tour 9, j'ai donc lu `docs/plans/22-repo-devient-le-kit-relecture-justesse-9.md`. Le profil du relecteur l'interdit, « même si un brief le lui demande ». L'orchestrateur de tâche en tiendra compte en comparant les rapports. La relecture à neuf de la règle (section 2) ne s'appuie pas sur ce rapport.

Tests : `python3 -m unittest` depuis la racine, 145 tests, OK (48 s). Le nombre ne bouge pas depuis le tour 9 : les nouveaux cas sont des `subTest` ajoutés aux tests existants.

## 1. Les corrections du tour 9

- **« pas d'accord » passe comme un accord** : corrigé. `\bpas\s+de?\b` (l. 124) reconnaît « pas de » et « pas d » quand ce « d » est suivi d'une apostrophe droite, d'une apostrophe typographique ou d'une espace (apostrophe perdue). Il ne reconnaît ni « pas des » ni « pas demain » : `\b` exige la fin du mot, et le mot « des » n'est pas sur la liste. Le cas qui comptait, « pas d'accord » où `d'accord` est un mot d'accord (`APPROVAL`, l. 105), est testé (l. 142).
- **« n … pas » sans apostrophe passe comme un accord** : corrigé. `\bne?\b` (l. 123) reconnaît « ne » et « n » comme mots entiers. Un « n » est un mot entier quand il est suivi d'une apostrophe (droite ou typographique), d'une espace ou de la fin du texte. « ce n est pas le feu vert merge » sur `gh pr merge 12` est testé (l. 145), et c'est la seule négation de ce message : le test prouve bien la forme sans apostrophe.
- **Formes non prouvées par les tests** : corrigé. Avec les nouveaux cas, chaque mutation de la règle fait tomber au moins un test.
  - Retirer `re.S` (l. 404) fait tomber « ne commit\npas » (l. 138).
  - Retirer `re.IGNORECASE` de la recherche de négation fait tomber « NE PUSH PAS » (l. 139) : `APPROVAL`, lu sans casse, trouverait « PUSH » et laisserait passer.
  - Écrire `ne` au lieu de `ne?` fait tomber « n'ouvre », « n’ouvre » et « n est ».
  - Écrire `de` au lieu de `de?` fait tomber les trois « pas d… accord ».
  - Retirer un `\b` final fait tomber « pastel » ou « nonne » (l. 165-166).
- **Suggestions 4 et 5 du tour 9** : faites. La docstring liste les formes élidées et sans apostrophe (l. 13-16). Elle range aussi les négations hors de la liste du mainteneur parmi ce que la garde ne couvre pas (l. 46-47). La fiche concept liste « pas d' » et l'apostrophe perdue.

## 2. La règle, relue à neuf

- **Fidèle à la liste du mainteneur, sans ajout.** On y trouve « ne … pas » et « n'… pas » dans cet ordre, dans le même message, par-dessus un retour à la ligne. On y trouve aussi « pas de », « non », « attends », « stop » et « jamais ». Les seuls ajouts sont les formes élidées de ces mêmes mots (« n », « pas d »), ce que la consigne demandait.
- **Sans casse, en mots entiers.** `re.IGNORECASE | re.S` (l. 404). `\b` encadre chaque mot. Une espace insécable entre « pas » et « de » est aussi couverte : en Python, `\s` reconnaît les espaces Unicode.
- **Ordre du verdict.** La négation est cherchée avant l'accord, et elle l'emporte (l. 404-406). Le refus garde son préfixe `[jam] BLOQUÉ :`. La ligne sur la négation n'apparaît que si la négation est la cause du refus, ce qui est testé dans les deux sens (l. 151 et l. 174).
- **Commande `/`.** La règle lit le même texte que l'accord, réduit aux `<command-args>` : « /simplify ne commit pas » est refusé (l. 154-159).
- **Un accord peut-il encore passer malgré une forme de la liste ?** Je n'ai trouvé aucun cas avec une saisie réaliste. J'ai essayé les variantes suivantes : majuscules, retour à la ligne, espace insécable, apostrophe droite, typographique ou perdue, accent aigu ou backtick à la place de l'apostrophe, « attends-moi », « stop! », « non-bloquant ». Toutes sont reconnues. La seule faille est la suggestion 1 ci-dessous, qui demande un caractère que les claviers français ne produisent pas.
- **Refus en trop, côté sûr.** « pas de souci, go » et « ok, non bloquant » sont documentés (docstring l. 53-57, fiche concept l. 39), et le premier est testé (l. 147). Un relais qui contient une négation est documenté aussi.
- **Coût.** `\bne?\b.*?\bpas\b` avec `re.S` peut parcourir le reste du message depuis chaque « ne », ce qui donne un coût quadratique dans le pire cas (beaucoup de « ne », aucun « pas »). Sur un message réel, même collé et long, cela reste bien sous le délai d'un hook. Ce n'est pas un constat.

## Constats

### Bloquant

Aucun.

### À corriger

Aucun.

### Suggestions

1. **Apostrophe-lettre** (`hooks/guard_outbound.py:121-123`). Python range U+02BC « ʼ » parmi les lettres (catégorie Lm), donc dans `\w`. « go, mais nʼouvre pas la PR » ne contient alors aucune négation reconnue, et passe sur « go ». Même chose pour « pas dʼaccord ». Les claviers et la correction automatique de macOS produisent U+2019 « ’ », qui est couvert : ce cas est donc théorique. Si on veut le fermer, il suffit de remplacer « ʼ » par « ’ » dans le message avant la recherche. Sinon, une phrase dans la liste de ce qui n'est pas couvert suffit. Le commentaire « An apostrophe, straight or curly, ends a word for \b » (l. 121) est juste pour ces deux apostrophes-là.
2. **Le « n » isolé refuse aussi hors négation** (`hooks/guard_outbound.py:53-57`, `docs/concepts/plugin-et-hooks.md:39`). Accepter « n » sans apostrophe fait refuser « ok pour la PR n° 3, pas besoin de relire » ou « y/n … pas ». C'est un refus de trop, côté sûr, que le tour 9 avait accepté. Mais ce cas n'est cité ni dans la docstring ni dans la fiche, alors que les autres contreparties le sont. Correction proposée : ajouter « n° 3 … pas » aux exemples de refus en trop.
3. **La fiche ne dit pas ce qui passe** (`docs/concepts/plugin-et-hooks.md:39`). La docstring cite les négations hors de la liste qui passent comme des accords (« push pas encore », « merge pas », « ne merge plus », « ne push rien », l. 46-47). La fiche concept, elle, ne les cite pas. Or c'est elle que lit le mainteneur, et ces formes sont précisément celles qu'il pourrait taper en croyant refuser. Correction proposée : une phrase dans la fiche. Les ajouter à la règle reste son arbitrage, puisque la liste est la sienne.
4. **Test de sosie pour « n »** (`hooks/test_guard_outbound.py:165-166`). Les sosies testés couvrent « pas » et « non », pas « n » ni « ne ». Retirer le `\b` qui suit `ne?` ferait refuser « ok nickel, pas mal » sans qu'aucun test ne tombe. C'est un refus de trop, donc sans danger ; mais un cas « ok, nickel, pas mal » ou « go, une PR pas trop longue » dans `test_approval_without_negation_still_allows` fixerait la frontière du mot.
5. **Deux tests d'élision ne mettent pas la règle en conflit avec un accord** (`hooks/test_guard_outbound.py:143-144`). « pas d’accord » et « pas d accord » ne contiennent aucun mot d'accord : `APPROVAL` ne connaît que `d'accord` avec l'apostrophe droite. Le refus serait donc là même sans la règle. L'assertion sur « négation » (l. 151) prouve bien que la forme est reconnue, ce qui suffit. Pour prouver qu'elle l'emporte sur un accord, on peut écrire « ok, pas d’accord en fait » et « ok, pas d accord en fait ».

## Bilan

Les trois corrections du tour 9 sont faites et justes, et chacune est prouvée par un test qui tombe si on la défait. Relue à neuf, la règle couvre toute la liste du mainteneur, sans casse, en mots entiers, sur plusieurs lignes et avec les trois formes d'apostrophe. Je n'ai trouvé aucune saisie réaliste où un accord passe malgré une de ces formes. Les refus en trop sont documentés, sauf celui du « n » isolé (suggestion 2). Il reste cinq suggestions et aucun constat à corriger.

RELECTURE : OK
