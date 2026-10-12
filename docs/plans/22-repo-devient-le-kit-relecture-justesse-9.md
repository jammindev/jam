# Relecture de l'issue #22, axe A (justesse), tour 9

Périmètre : la négation qui vaut refus dans la garde de sortie (décision du mainteneur, « Ok negation feu vert recette », 2026-10-12 21:52). Fichiers relus : `hooks/guard_outbound.py` (`NEGATION`, `check_approval`, docstring), `hooks/test_guard_outbound.py` (tests de négation, l. 126 à 165), `docs/concepts/plugin-et-hooks.md` (paragraphe sur l'accord, l. 39).

Tests : `python3 -m unittest` depuis la racine, 145 tests, OK.

## Ce qui est juste

- La liste du mainteneur est couverte et rien n'y est ajouté : `ne … pas` et `n'… pas` dans le même message (`re.S`, donc par-dessus un retour à la ligne), `pas de`, `non`, `attends`, `stop`, `jamais` (`hooks/guard_outbound.py:116-120`).
- La règle ignore la casse (`re.IGNORECASE`). Elle travaille en mots entiers : `\b` des deux côtés, donc « pastel », « nonne », « stopper » et « jamaisvu » ne sont pas des négations. Elle reconnaît les deux apostrophes, droite `'` et typographique `’`.
- La règle s'applique au texte d'où l'accord est lu, après réduction d'une commande `/` à ses `<command-args>` : un `/simplify ne commit pas` est refusé, et le nom de la commande ne compte pas.
- La négation est vérifiée avant l'accord (`hooks/guard_outbound.py:398-400`). Le refus garde le préfixe `[jam] BLOQUÉ :`, et la ligne qui parle de la négation n'apparaît que si c'est elle qui cause le refus (testé, l. 162).
- Les refus en trop (« pas de souci, go », « ok, non bloquant ») sont documentés dans la docstring et dans la fiche concept. C'est voulu, donc ce n'est pas un constat.

## Constats

### À corriger

1. **« pas d'accord » passe comme un accord** (`hooks/guard_outbound.py:118`). `\bpas\s+de\b` ne reconnaît pas la forme élidée « pas d' ». Or `d'accord` fait partie du vocabulaire d'accord (`APPROVAL`, l. 102). Résultat : à « Je committe ? », la réponse « pas d'accord » laisse passer `git commit`. C'est le refus le plus naturel qui contienne un mot d'accord. « pas d' » n'ajoute rien à la liste du mainteneur : c'est « pas de » élidé, exactement comme `n'` est `ne` élidé, que la règle traite déjà. Correction attendue : `\bpas\s+(?:de\b|d['’])`, plus un test refusé « pas d'accord » sur `git commit`.

2. **« n … pas » sans apostrophe passe comme un accord** (`hooks/guard_outbound.py:117`). Avec `\b(?:ne\b|n['’])`, il faut une apostrophe après le `n`. « ce n est pas le feu vert merge » ou « je n ai pas dit push » ne contiennent donc aucune négation reconnue, mais contiennent un mot d'accord : `gh pr merge` ou `git push` passent. Or c'est précisément le relais qui, selon la doc (`docs/concepts/plugin-et-hooks.md:39`, docstring l. 52-53), « ne vaut pas accord ». Et ce cas existe : les relais envoyés par `orca terminal send` perdent leurs apostrophes, comme le brief de ce tour (« l issue », « d une », « n … pas »). Le texte relayé compte comme un message du mainteneur. Correction attendue : accepter `n` seul comme mot, `\b(?:ne|n)\b|\bn['’]`, ou plus simplement `\bn(?:e\b|\b|['’])`. Ajouter un test refusé « ce n est pas le feu vert merge » sur `gh pr merge 12`. Ce qu'on accepte de refuser en plus : « n° » suivi de « pas » ailleurs dans le message, ce qui reste du côté sûr.

3. **Les tests ne prouvent pas trois des formes demandées** (`hooks/test_guard_outbound.py:129-138`). On peut retirer `re.S` de `check_approval` (l. 398) ou l'apostrophe `’` de `NEGATION` (l. 117) sans qu'aucun test ne tombe. Et aucun message tout en majuscules n'est testé. Correction attendue : ajouter à `test_negation_refuses_despite_an_approval_word` les cas « ne commit\npas » (négation sur deux lignes), « go, mais n’ouvre pas la PR » (apostrophe typographique) et « NE PUSH PAS ». Si les points 1 et 2 sont corrigés, y ajouter aussi leurs cas.

### Suggestions

4. **Négations hors de la liste** (à soumettre au mainteneur, pas à corriger d'office puisque la liste est la sienne). À l'oral, on laisse tomber le « ne » : « push pas encore », « merge pas » passent comme accords. « ne merge plus » et « ne push rien » aussi. Ajouter « pas » seul refuserait beaucoup plus de messages (« pas mal, go ») ; c'est un arbitrage du mainteneur. On peut au moins noter ces formes dans la liste de ce que la garde ne couvre pas.

5. Une fois les points 1 et 2 corrigés, mettre à jour la liste des formes dans la docstring (l. 13-15) et dans `docs/concepts/plugin-et-hooks.md:39` (« pas d' », « n » sans apostrophe).

## Bilan

La règle est juste dans son principe et fidèle à la liste du mainteneur, mais deux formes de cette liste laissent passer un accord : « pas d'accord » et « n … pas » sans apostrophe. Ce sont deux refus naturels, et le second est le cas de relais que la doc promet de bloquer. À cela s'ajoutent les tests manquants (point 3). Trois constats à corriger, aucun bloquant.

RELECTURE : À CORRIGER
