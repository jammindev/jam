# Relecture #23 — axe conformité, tour 4

Relu : tout le travail non commité de la branche (`git status`, `git diff -M`, fichiers non suivis : `process/fiche-projet.md`, `scripts/maintainer_time.py` et ses tests, `docs/methode.md`, `docs/decisions/0018-process-elague.md`, `docs/concepts/veille-et-mesure.md`, `docs/process/README.md`), comparé au plan validé, à l'issue (brouillon K1-2 de `docs/plans/cadrage-kit-issues.md`, l. 91 à 140), aux ADR 0012, 0013, 0015, 0016, 0017 et 0018, et à l'ancien `docs/process/` du worktree principal.

Tests : `python3 -m unittest` → 181 tests, OK.

## Vérifié sans constat

- **Critère de fin** :
  - `process/`, `roles/` et `process/fiche-projet.md` existent ; `docs/process/` ne contient plus que `README.md`, un renvoi ;
  - plafond de 4904 mots tenu par `hooks/test_plugin.py` (vert), qui compte aussi la fiche et refuse tout fichier non compté ;
  - ni `pnpm`, ni chemin du poste, ni nom d'hôte, de personne ou d'un autre projet dans `process/` et `roles/` : seuls `JAM_ROLE` et la marque `[jam]` du plugin lui-même ;
  - règles du point 3 présentes dans le process et dans le profil qui les applique, chacune avec sa référence : niveaux (FR-049 : process, coordinateur, planificateur), *léger* (FR-052 : process, coordinateur, implémenteur), seuil (FR-050 : process, relecteur, orchestrateur, coordinateur), plafonds (FR-051 : process, coordinateur, orchestrateur), relais (FR-053 et RET-017 : process, coordinateur, orchestrateur), recette d'interface (FR-054 : process, recetteur), mesure (FR-055 et RET-018 : process, coordinateur, orchestrateur), ADR 0017 (lancement par Orca, NFR-013, fenêtre d'autorisation : process et coordinateur ; Q-058 : process et orchestrateur) ;
  - le planificateur exige un niveau motivé (`roles/planificateur.md:16`) ;
  - la règle 6 d'`AGENTS.md` est cohérente avec FR-052 et FR-053 ;
  - `docs/methode.md` existe, au niveau *léger* ; Q-058 est tranchée, de façon cohérente avec le profil de l'orchestrateur, l'ADR 0018 et la mention prévue au statut de l'ADR 0013.
- **NFR-016** : plus aucun « Origine : … » dans `process/` ni `roles/` ; chaque origine a sa trace (tableau « Origines retirées » de l'ADR 0018, ou RET).
- **ADR acceptées** : aucune décision de 0012, 0013, 0015, 0016 ou 0017 n'est perdue sans être actée. Ce qui change (relais allégé, mesure par script, note de suivi de l'orchestrateur, vérification à la main d'une carte remplacée par la veille sauf pour la fenêtre d'autorisation) est porté par l'ADR 0018 et ses mentions de statut prévues. Les ADR existantes ne changent que par leurs liens (0009, 0012, 0013) et par l'index.
- **Liens** : aucun lien cassé vers l'ancien `docs/process/` hors de `docs/plans/` ; les liens réécrits (`../../roles/`, `../../process/`, `../methode.md`) se résolvent.
- **Repo public** : rien du poste dans les fichiers ajoutés. Les chemins des tests (`/Users/testhome`, `/Users/x/…`) sont inventés et existaient déjà.
- **Vocabulaire** : « agent en cours », « épisode », « moment », « note de suivi », « veille des cartes », « session libre » sont définis dans le glossaire, et utilisés tels quels.

## Bloquant

Aucun.

## À corriger

### C-1 — Une carte inactive au niveau *léger* fait relancer un orchestrateur de tâche qui n'existe pas

- **Fichiers** : `process/README.md:77` (« Pour une carte inactive, le coordinateur relance l'orchestrateur de tâche ou passe la carte en `⛔` ») ; `roles/coordinateur.md:20` (« Carte inactive (« aucun agent au travail ») : il relance l'orchestrateur de tâche, ou passe la carte en `⛔` »).
- **Exigence** : FR-052 : au niveau *léger*, pas d'orchestrateur de tâche ; c'est le coordinateur qui tient la carte. *Léger* est le niveau par défaut de jam (`docs/methode.md:5`).
- **Scénario d'échec** : une tâche de jam, au niveau *léger*. Le coordinateur pose `▶ implémenteur en cours` et lance l'implémenteur. Celui-ci s'arrête sur `BLOQUÉ : …` pendant que le coordinateur discute d'autre chose avec le mainteneur. Dix minutes plus tard, la veille se réveille : « aucun agent au travail ». Le profil dit au coordinateur de relancer l'orchestrateur de tâche. Il n'y en a pas : soit il en lance un (`JAM_ROLE=orchestrateur-tache`), ce qui contredit FR-052 et consomme un agent sous le plafond ; soit il improvise, sans règle.
- **Correction attendue** : dans les deux passages, écrire que le coordinateur relance celui qui tient la carte : l'orchestrateur de tâche au niveau *standard* ; au niveau *léger*, il lit lui-même la fin du rôle (`orca terminal read`) et reprend la tâche. L'issue de sortie par `⛔` reste. Une demi-ligne de plus dans chaque fichier, sous le plafond.

### C-2 — Les règles propres de jam portent sur un plan qui n'existe pas au niveau de jam

- **Fichiers** : `docs/methode.md:18` (« le plan a deux sections de plus : **Orca** … ; **Concepts** … ») et `:19` (« Si un plan marque un morceau « repris » ») ; `AGENTS.md:41`, règle 9 (« Le plan de chaque tâche de jam a une section « Orca » »).
- **Exigence** : FR-052 (au niveau *léger*, pas de planificateur : l'issue tient lieu de plan) ; `AGENTS.md`, règle 9, et RET-011, que la fiche reprend.
- **Scénario d'échec** : une tâche de jam au niveau *léger*, qui touche une brique qu'Orca possède. Pas de planificateur, donc pas de plan. Le coordinateur lance l'implémenteur sur l'issue. Personne n'écrit la section « Orca » : la fiche et la règle 9 ne la demandent qu'au plan. La consultation d'Orca (RET-011) et le contrôle d'une reprise ne se font pas, sans que rien ne le signale. La section « Concepts » disparaît de la même façon.
- **Correction attendue** : dans `docs/methode.md:18`, écrire « le plan, ou au niveau *léger* l'issue qui en tient lieu (FR-052), a deux sections de plus », et « Si le plan ou l'issue marque un morceau « repris » » à la l. 19. Dans `AGENTS.md:41`, écrire « Le plan de chaque tâche de jam (l'issue, au niveau *léger*) a une section « Orca » ». C'est alors au brouillon d'issue du rédacteur de les porter.

## Suggestions

- **S-1** — `roles/relecteur.md:9` : `Edit(/docs/plans/<rapport>)` limite le relecteur à son seul rapport, au lieu de `Edit(docs/plans/*-relecture*.md)`. C'est un mieux : il ne peut plus réécrire les rapports des tours précédents. Mais le tableau « Ce que chaque règle nouvelle remplace ou retire » de l'ADR 0018 (l. 42 à 65) ne le dit pas : la ligne sur les règles `Edit` ancrées par `/` (l. 56) ne parle que de l'ancrage. Ajouter une ligne : « Relecteur : une seule règle `Edit`, sur son rapport | `Edit(docs/plans/*-relecture*.md)` et la limite « il peut réécrire les rapports des tours précédents » | Plan de #23 » (NFR-016).
- **S-2** — `process/fiche-projet.md:13` (« En production, le feu vert merge se relaie sous sa forme complète ») laisse entendre qu'un merge hors production se relaie par un simple « ok ». Or `process/README.md:72` exige la forme complète pour « tout autre feu vert » que le plan et la recette, donc pour tout merge, comme FR-053. Le « donc » de `docs/methode.md:14` et le « celui de jam compris » d'`AGENTS.md:38` suivent la même lecture. L'effet pratique est nul, puisqu'un merge remonté par la carte est de toute façon confirmé dans le terminal du coordinateur. Écrire dans le gabarit : « Merge : ce qu'il déclenche, mise en production ou non » sans la phrase sur le relais, et dans `process/README.md:72` simplement « tout autre feu vert, merge compris ».
- **S-3** — `docs/decisions/0018-process-elague.md:95` : la mention prévue au statut de l'ADR 0016 se limite à « précisée (0018) ». Or l'ADR 0018 change une phrase de sa décision : la mesure n'est plus « notée à la main » (ADR 0016, l. 67) mais estimée par un script et validée par le mainteneur, et le plafond prend une valeur. Comme pour l'ADR 0013, détailler : « précisée (0018) : temps du mainteneur estimé par un script et validé par lui ; plafond de 6 agents en cours au poste ».
- **S-4** — `roles/relecteur.md:11` : la variante « issues publiées » (tracée dans l'ADR 0012) a perdu la forme `?state=all`. Sans elle, `gh api repos/<dépôt>/milestones` omet les milestones fermés, et un relecteur pourrait conclure à un milestone manquant. Ajouter « (et `?state=all`, pour les milestones fermés) ».
- **S-5** — `hooks/test_plugin.py:2` à `:6` : la docstring ne parle que du câblage du plugin (« these three files ») alors que le fichier teste aussi la taille et la généricité de la méthode (`MethodTest`). Une phrase de plus, pour qu'un lecteur qui ne code pas sache où vit le contrôle de NFR-014 et NFR-015.
- **S-6** — `process/README.md:20` : la ligne *léger* dit « committe et ouvre la PR », sans « pousse », que le profil du coordinateur écrit (`roles/coordinateur.md:19`). Aligner sur le profil.

RELECTURE : CORRECTIONS (2)
