# Relecture conformité — #23 Process élagué (K1-2), tour 7

Relecteur B, axe conformité. Relu : tout le travail non commité de la branche (`git status`, `git diff`, fichiers non suivis), d'abord les changements qui suivent la recette refusée (mesure limitée aux sessions du coordinateur, explication de la friction 18, règle « Messages au mainteneur », retrait de « Le mainteneur valide le chiffre », Q-064).

**Tests** : `python3 -m unittest` donne `Ran 182 tests`, `OK` (test de taille de `hooks/test_plugin.py` compris, plafond 4904).

## Critère de fin, point par point

| Point | Constat |
|---|---|
| `process/`, `roles/`, `process/fiche-projet.md` | Présents ; les sept profils sont en renommages depuis `docs/process/roles/`. OK |
| `docs/process/` réduit à un renvoi | `docs/process/README.md` : renvoi seul, liens justes. OK |
| Plafond de 4904 mots | Test de taille vert. OK |
| Ni `pnpm`, ni chemin, ni nom d'hôte ou d'autre projet dans `process/` et `roles/` | Aucun trouvé (Grep, en ignorant la casse). Les chemins `/Users/testhome`, `/private/tmp/claude-…` de `hooks/` sont des valeurs de test ou des dossiers génériques de Claude Code. OK |
| Règles du point 3 dans le process et dans le profil qui les applique, avec RET ou FR | FR-049 (coordinateur, planificateur), FR-050 (relecteur, orchestrateur, coordinateur), FR-051, FR-052, FR-053, FR-054 (recetteur), FR-055 et RET-018 (coordinateur, orchestrateur). OK |
| Planificateur : niveau motivé quand une tâche monte | `roles/planificateur.md:16`. OK |
| Règle 6 d'`AGENTS.md` et FR-052, FR-053 | Cohérente (commit par l'orchestrateur en *standard*, par le coordinateur en *léger* ; « ok » pour plan et recette ; forme complète pour le merge de jam, d'après la fiche). OK |
| `docs/methode.md` au niveau *léger* | OK |
| Q-058 tranchée, cohérente avec le profil de l'orchestrateur et les ADR | Q-058, ADR 0018, `roles/orchestrateur-tache.md:7` et glossaire (« Note de suivi ») concordent. OK |

Autres points vérifiés sans constat : changements des ADR 0009, 0012 et 0013 limités aux liens ; ADR 0018 « proposée », RET-017 et RET-018 « en application » ; aucun lien vers l'ancien `docs/process/` hors `docs/plans/` et le renvoi ; niveau *léger* décrit de la même façon dans le process, le profil du coordinateur, `AGENTS.md`, la fiche et le glossaire ; « Le mainteneur valide le chiffre » retiré partout, trace dans RET-018 ; écart à l'issue sur la mesure acté dans l'ADR 0018 (l. 42), RET-018, FR-055, `02-ARCHITECTURE.md`, le process (« Mesure ») et la fiche concept, en accord avec `scripts/maintainer_time.py` (docstring et `read_sessions`, transcript illisible ignoré) ; explication de la friction 18 identique dans `process/README.md:103`, `roles/recetteur.md:11`, l'ADR 0018 (l. 60), `docs/methode.md:13` et Q-064, et plus aucune doc hors `docs/plans/` ne présente l'ancrage par `/` comme le remède ; règle « Messages au mainteneur » fidèle au retour, en deux phrases (`process/README.md:59`).

## Bloquant

Aucun.

## À corriger

### 1. La règle « Messages au mainteneur » ne dit pas ce qu'elle remplace et n'a aucune trace

- **Fichiers** : `process/README.md:59` ; `docs/decisions/0018-process-elague.md`, tableau « Ce que chaque règle nouvelle remplace ou retire » (l. 46 à 69) ; `docs/specs/RETOURS.md`.
- **Ce qui est violé** : NFR-016 (« toute nouvelle règle dit laquelle elle remplace ou retire ») et la grille de la fiche (`docs/methode.md:10` : la règle le dit « dans une ADR »). Le process affirme aussi, l. 3, que « l'ADR 0018 dit aussi quelle règle chaque règle de ce process remplace » : pour cette règle, c'est faux.
- **Scénario d'échec** : après le merge, un lecteur cherche pourquoi le process impose de remplacer « friction 18 » ou « #22 » par ce qu'ils désignent. Le process ne porte plus d'origine (ADR 0018, conséquence (−) : « pour comprendre une règle, il faut lire cette ADR »), l'ADR 0018 ne cite pas la règle, et `RETOURS.md` n'a aucun retour sur ce point. La seule trace est `docs/plans/23-process-elague-retours.md`, une note de suivi non relue que rien ne désigne. Le retour voisin, reçu au même relais (« Le mainteneur ne valide pas le chiffre »), est lui inscrit dans RET-018 : l'écart de traitement montre l'oubli. Toutes les autres règles nouvelles du process portent leur référence (RET-017, FR-050…) ; celle-ci n'en porte aucune.
- **Correction attendue** :
  - un retour dans `RETOURS.md` (prochain numéro libre, RET-019), « en application », qui reprend la remarque et l'analyse de la note de suivi (§1) ;
  - une ligne dans le tableau de l'ADR 0018 : « Messages au mainteneur : tout message qui lui est adressé se lit seul, projet et tâche en mots, références internes remplacées par ce qu'elles désignent | Rien : ajout | RET-019 » ; et RET-019 dans la ligne « Tranche » ;
  - la référence `(RET-019)` à la fin de `process/README.md:59`, comme pour les autres règles.

### 2. Les rôles qui écrivent pour le mainteneur ne connaissent pas la règle « Messages au mainteneur »

- **Fichiers** : `roles/planificateur.md:21` (« Questions au mainteneur ») ; `roles/recetteur.md:21` (check-list du mainteneur).
- **Ce qui est violé** : le principe du critère de fin repris pour toute règle du process : une règle est dans le process **et** dans le profil du rôle qui l'applique. Seuls le coordinateur (`roles/coordinateur.md:21`) et l'orchestrateur de tâche (`roles/orchestrateur-tache.md:16`) la portent.
- **Scénario d'échec** : à la prochaine tâche *standard*, le planificateur, qui ne lit que la fiche, ce qu'elle désigne et l'issue (`roles/planificateur.md:12`), jamais le process, écrit ses « Questions au mainteneur » comme l'a fait le plan de #23 : « 4. **Q-058** : … », « 6. Numéros réservés : … RET-017 … RET-018 … ». Ces questions sont le message que le mainteneur lit au feu vert plan, depuis son téléphone et entre plusieurs projets : il doit aller chercher ce que désigne Q-058, ce que la règle veut éviter. De même, la check-list du recetteur, que le mainteneur déroule seul, peut citer « friction 18 » ou « point 8 de l'issue » sans dire ce qu'ils désignent, comme la tête du rapport de recette de #23.
- **Correction attendue** : dans `roles/planificateur.md:21`, « **Questions au mainteneur**, numérotées, chacune avec sa recommandation, lisibles seules (process, « Messages au mainteneur ») » ; dans `roles/recetteur.md:21`, ajouter « lisible seule (process, « Messages au mainteneur ») » à la description de la check-list. Quelques mots, sous le plafond.

## Suggestions

1. `docs/specs/01-REQUIREMENTS.md`, FR-055 : la parenthèse « commandes `!`, briefs et relais exclus » date de la lecture des deux côtés. Le script ne lit plus que la session du coordinateur, où ni brief ni relais n'arrivent comme message du mainteneur ; il n'a plus de règle pour les écarter. Écrire plutôt « commandes `!` et messages d'autres agents exclus », ce que fait `maintainer_words`.
2. `docs/plans/23-process-elague-recette.md:3` à `:6` : la tête « À décider » cite « point 8 de l'issue » et « Friction 18 » sans dire ce qu'ils désignent. Elle précède la règle, mais la recette sera refaite avant le feu vert : la nouvelle tête devra la suivre (« l'écriture refusée au recetteur lancé sur le plugin du worktree » plutôt que « friction 18 »).

RELECTURE : CORRECTIONS (2)
