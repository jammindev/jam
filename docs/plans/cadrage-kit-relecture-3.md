# Relecture du cadrage `cadrage-kit` — tour 3

Relecteur seul, contexte neuf. Relu : la rédaction non commitée du worktree (ADR 0016 et 0017, `docs/specs/00` à `04`, `GLOSSARY.md`, `OPEN-QUESTIONS.md`, `RETOURS.md`, `docs/decisions/README.md`, `docs/process/README.md` et les profils modifiés, `docs/references/orca.md`, `AGENTS.md`, `README.md`, brouillons `docs/plans/cadrage-kit-issues.md`). Inventaire des hooks cité par K1-1 vérifié sur le dossier des hooks du poste, en lecture seule.

## Vérifications sans constat

- Numérotation : FR-042 à FR-056, NFR-013 à NFR-016, Q-054 à Q-063, RET-014 à RET-016, ADR 0016 et 0017 : aucun numéro réutilisé. Les exigences de l'app sont gardées avec une colonne « État », non supprimées.
- Sort des ADR (ADR 0016) cohérent avec `AGENTS.md` (ADR caduques 0002, 0004 à 0007, 0010), avec l'ADR 0017 (0015 en partie remplacée, 0013 qui retrouve sa ligne « Lancement ») et avec le statut actuel de l'ADR 0013.
- `docs/process/` : les seuls passages touchés sont ceux que contredit l'ADR 0017 (acteurs, correspondance, lancement du coordinateur, profil du coordinateur) ; plus aucune mention du `cd` ni du terminal flottant comme place du coordinateur.
- Découpage RET-016 respecté : trois issues, mesure unique, aucun autre projet dans le périmètre ; skills, modèles et script d'indicateurs renvoyés à Q-062.
- Inventaire des hooks : les quatre hooks de la table de K1-1 existent sur le poste ; deux seulement ont des tests, ce que K1-1 prévoit (« les hooks sans tests en reçoivent d'abord »). La forme `git rm` exacte de l'implémenteur correspond aux fichiers présents à la racine.
- Repo public : aucun chemin du poste, nom d'hôte, adresse ni nom de machine dans les fichiers modifiés ; la machine est remplacée par « le poste de travail » (RET-014). Les mentions d'un autre projet (`house`, dans Q-035 et RET-002, RET-011) existaient avant ce cadrage, sont dans `docs/` et non dans les dossiers du plugin (NFR-014) ; rien de nouveau.

## Bloquant

Aucun.

## À corriger

### C-1 — La garde de sortie unique empêche le coordinateur d'agir sur un feu vert remonté par la carte

- **Fichiers** : `docs/plans/cadrage-kit-issues.md` l. 62 (garde de sortie : « sans accord explicite dans le dernier message du mainteneur ») ; `docs/process/README.md` l. 129 (feu vert donné dans le worktree, cité dans un segment `✓` de la carte, sur lequel le coordinateur merge ou publie) ; ADR 0016 l. 32 et 96.
- **Constat** : la garde lit le dernier message du mainteneur **dans la session qui lance la commande**. Elle couvre désormais `gh pr merge` et les écritures `gh` (publication des issues et des milestones). Or le process fait agir le coordinateur sur un segment `✓` de la carte, sans que le mainteneur ne lui parle. Après K1-1, ce merge et cette publication sont refusés. La garde actuelle du poste ne couvre que commit et push : le conflit est nouveau, et rien ne le traite.
- **Correction attendue** : dans K1-1 (table des hooks, ou point 2), nommer ce cas et la règle retenue. La plus simple : un feu vert qui ouvre une action du coordinateur, donné dans le worktree, est confirmé par le mainteneur dans le terminal du coordinateur avant le merge ou la publication. Ajouter un test de la garde pour ce cas, et inscrire la règle dans le point 3 de K1-2 (relais d'un feu vert).

### C-2 — Recette de K1-1 : un refus ne prouve pas que le hook du plugin est câblé

- **Fichiers** : `docs/plans/cadrage-kit-issues.md` l. 79 (critère de fin : « installé sur le poste, le plugin câble les quatre hooks… sont refusés ») et l. 84 (recette : « Pendant la recette, les hooks du poste tournent aussi »).
- **Constat** : pendant la recette, la garde du coordinateur et la garde de sortie du poste sont actives. Un `git commit` refusé ou une écriture du coordinateur refusée le seraient même si le plugin ne câblait rien. Le doublon est prévu pour le récapitulatif, pas pour les refus. Ce point du critère de fin n'est donc pas vérifiable tel qu'écrit.
- **Correction attendue** : exiger que chaque refus d'un hook du plugin porte une marque reconnaissable (par exemple un préfixe propre au plugin dans le message). La check-list vérifie cette marque, ou vérifie la liste des hooks chargés et leur source. Seul un refus marqué compte.

### C-3 — Recette de K1-1 : le recetteur ne peut pas dérouler la check-list qu'on lui attribue

- **Fichiers** : `docs/plans/cadrage-kit-issues.md` l. 34 (« Elle déroule d'abord la check-list du mainteneur, puis les tests ») et l. 84 ; `docs/process/roles/recetteur.md` l. 9 et 11.
- **Constat** : la check-list de K1-1 demande une session lancée avec `JAM_ROLE=coordinateur`, un `git commit` dans un repo jetable, une carte Orca de test et le lancement du script de veille. Ce sont les commandes du recetteur qui l'en empêchent : `git commit` est dans ses `--disallowedTools` (un refus viendrait des permissions, pas du hook), et il n'a ni `orca`, ni `git init`, ni le lancement d'un script, ni celui d'une session `claude`. Le §2 laisse croire que la recette de l'agent couvre ces points (RET-010).
- **Correction attendue** : dans K1-1 (Recette) et au §2, dire quels points le recetteur note « non reproduit », sur le modèle de la règle « Clavier » du profil du recetteur. Il les couvre par les tests, et seul le mainteneur les déroule. Ne pas ajouter de commande au recetteur.

### C-4 — Clone de référence d'Orca encore imposé aux tâches de jam

- **Fichiers** : `docs/process/roles/planificateur.md` l. 11 (« Pour une tâche de jam, la commande se termine par `--add-dir <clone-orca>` ») ; `docs/process/roles/orchestrateur-tache.md` l. 31 (préparation du clone, `chmod` soumis à l'accord du mainteneur, carte en `⛔`) ; ADR 0016 l. 98 (ADR 0014 historique, aucune reprise).
- **Constat** : K1-1 et K1-2 tournent avec ces profils, au niveau *standard*. L'orchestrateur de tâche préparerait un clone inutile, avec une invite d'accord et une carte bloquée. La ligne « Orca » des issues (l. 86, 135, 159) dit seulement qu'il n'y a rien à reprendre. Elle ne dit pas qu'il n'y a pas de clone. C'est une règle trompeuse laissée sur `main`.
- **Correction attendue** : dans la ligne « Orca » de K1-1 et de K1-2 (ou au §2, si le corps y renvoie), ajouter : « pas de clone de référence : le planificateur est lancé sans `--add-dir <clone-orca>` (ADR 0016, ADR 0014 historique) ». Les deux profils restent inchangés jusqu'à K1-2, qui sort cette règle du générique.

### C-5 — K1-1 : aucun accès prévu aux hooks à rapatrier

- **Fichiers** : `docs/plans/cadrage-kit-issues.md` l. 58 et 67 (« Le plan inventorie les gardes de sortie actuelles des postes ») ; `docs/process/roles/implementeur.md` l. 13.
- **Constat** : le planificateur et l'implémenteur doivent lire les hooks du poste, qui sont hors du worktree. Aucun profil ni aucune issue ne dit comment. La lecture hors du worktree en `dontAsk` est elle-même une question ouverte (Q-043). C'est une commande nécessaire à la première issue, et elle manque.
- **Correction attendue** : au §2 et dans K1-1 (« Commandes des rôles »), écrire que l'orchestrateur de tâche donne dans le brief le chemin du dossier des hooks du poste. Il ajoute `--add-dir <dossier des hooks du poste>` à la commande du planificateur et à celle de l'implémenteur. Le chemin reste dans le brief, jamais dans le repo. L'implémenteur n'y écrit pas : son `Edit(./**)` ne le couvre pas. Préciser aussi que seul le poste de travail est inventorié : les autres postes n'ont pas d'agent pour le faire.

### C-6 — K1-2 : aucune commande ne permet de vider `docs/process/`

- **Fichiers** : `docs/plans/cadrage-kit-issues.md` l. 32 (« seule K1-2 tourne dans cet intervalle, avec ces formes ») et l. 126 (critère de fin : « `docs/process/` ne contient plus qu'un renvoi ») ; `docs/process/roles/implementeur.md` l. 9 et 13.
- **Constat** : déplacer ou supprimer les sept profils de `docs/process/roles/` demande une commande shell. L'implémenteur a `Edit(docs/process/**)` interdit, et sa seule forme `git rm` vise les fichiers de l'app. Le rédacteur n'a aucune commande de suppression. K1-2 ne peut donc pas atteindre son critère de fin avec les profils que ce cadrage merge.
- **Correction attendue** : ajouter au passage « Kit » de l'implémenteur les formes exactes pour K1-2 (sans joker), par exemple `"Bash(git mv docs/process/roles roles)"` et `"Bash(git mv docs/process/README.md process/README.md)"`, avec leurs formes `rtk`. Le rédacteur réécrit ensuite `docs/process/README.md` en renvoi. `git mv` garde aussi l'historique des profils. Sinon, le §2 doit dire comment K1-2 obtient ces formes.

### C-7 — K1-2 ne prévoit pas la mise à jour de la règle 6 d'`AGENTS.md`

- **Fichiers** : `AGENTS.md`, règle 6 (feu vert relayé : « mots exacts, heure, session » ; « l'orchestrateur de tâche committe… seul le coordinateur merge ») ; `docs/plans/cadrage-kit-issues.md` l. 103 et 110 à 118, 129.
- **Constat** : après K1-2, deux règles du process contredisent la règle 6. Le relais allégé (FR-053) accepte un « ok » transmis pour le plan et la recette. Le niveau *léger* (FR-052) fait committer et ouvrir la PR au coordinateur. K1-2 ne fait d'`AGENTS.md` qu'un « renvoi au process du plugin et à la fiche », et son critère de fin ne parle que du process et des profils.
- **Correction attendue** : dans K1-2, point 3 (relais allégé, niveau *léger*), ajouter « et la règle 6 d'`AGENTS.md`, par le rédacteur ». Dans le critère de fin, ajouter « la règle 6 d'`AGENTS.md` est cohérente avec FR-052 et FR-053 ».

### C-8 — Le jalon exige le temps mesuré sur « chaque issue du jalon », y compris K1-3, qui ne peut pas citer le sien

- **Fichiers** : `docs/specs/04-ROADMAP.md` l. 15 ; `docs/specs/00-VISION.md` l. 40 ; `docs/plans/cadrage-kit-issues.md` l. 20 (description du milestone) ; à comparer avec l. 151 (K1-3 : « issues du jalon déjà mergées »).
- **Constat** : le temps de K1-3 n'est connu qu'à son feu vert merge, donc après l'écriture de la page. Le critère de fin du jalon est circulaire, et il contredit K1-3.
- **Correction attendue** : écrire « avec le temps du mainteneur mesuré sur K1-1 et K1-2 » (ou « sur chaque issue mergée avant K1-3 ») dans les trois endroits.

### C-9 — Schéma de la CLI Orca : versionné d'office ou à décider ?

- **Fichiers** : ADR 0017 l. 29 (« outils de veille des cartes et schéma de la CLI Orca : dans le plugin (`scripts/`), par la première issue ») ; `docs/plans/cadrage-kit-issues.md` l. 68 (« Le plan dit si le schéma de la CLI Orca… doit être versionné »).
- **Constat** : l'ADR tranche, et l'issue laisse le plan décider. Ce sont deux règles contradictoires.
- **Correction attendue** : aligner. Par exemple, dans l'ADR : « schéma de la CLI Orca : versionné dans le plugin s'il est indispensable aux scripts, ce que dit le plan de K1-1 (NFR-013) ». Ou bien retirer « le plan dit si » de l'issue.

### C-10 — Le plafond porte sur les agents « en cours » ou « actifs » ?

- **Fichiers** : `docs/specs/01-REQUIREMENTS.md` l. 20 (FR-051 : « lit les agents en cours (`orca terminal list`) ») ; ADR 0016 l. 63 ; `docs/plans/cadrage-kit-issues.md` l. 68 (script de lancement : « nombre d'agents en cours ») ; `docs/specs/GLOSSARY.md` l. 33 (« Agent actif »… « Le plafond d'agents global en borne le nombre ») ; `docs/process/README.md` l. 192 (un agent qui attend ne compte pas).
- **Constat** : un terminal listé n'est pas un agent actif : un orchestrateur de tâche dans `orca terminal wait` est en cours, mais pas actif. Le script de K1-1 doit compter l'un ou l'autre, et les textes divergent.
- **Correction attendue** : choisir un seul terme et l'écrire partout. Le plus simple pour un script : « agents en cours », c'est-à-dire les sessions d'agent que liste `orca terminal list`. Mettre alors à jour la définition du glossaire. K1-2 aligne ensuite le process (l. 192).

### C-11 — K1-1 : actions sur le poste placées dans le critère de fin, et impossibles pour le coordinateur

- **Fichiers** : `docs/plans/cadrage-kit-issues.md` l. 82 (« après le feu vert merge, les gardes de sortie et les hooks rapatriés sont retirés des réglages du poste, par le mainteneur ou par le coordinateur avec son accord ») ; l. 79 (« installé sur le poste »).
- **Constat** : (1) Un critère de fin tenu après le merge ne peut être vérifié ni à la recette ni au feu vert merge. (2) La garde du coordinateur refuse toute écriture dans les réglages de Claude Code du poste, et elle laisse l'inscription d'un hook au mainteneur : « par le coordinateur avec son accord » est faux. (3) Personne n'est chargé d'installer le plugin sur le poste.
- **Correction attendue** : sortir ce point du critère de fin. Le placer dans les « Actions de publication » (§1), ou dans une ligne « Après le merge » de K1-1. Il serait fait par le mainteneur : installer le plugin selon la décision de Q-055, retirer des réglages du poste les hooks devenus doublons, puis vérifier qu'un seul récapitulatif s'affiche.

## Suggestions

- **S-1** — `docs/plans/cadrage-kit-issues.md` l. 72 : « (section 2) » ne renverra à rien une fois l'issue publiée, puisque le corps commence à **Exigences**. Remplacer par un lien vers `docs/plans/cadrage-kit-issues.md` sur `main`, ou recopier les deux phrases utiles.
- **S-2** — K1-1, recette (l. 84) : la garde de sortie actuelle du poste laisse passer les dépôts placés dans les dossiers temporaires de session. Si le hook rendu générique garde cette exemption, un repo jetable créé là ne montrera aucun refus. Dire où le créer, ou demander au plan de trancher l'exemption.
- **S-3** — NFR-015 (`01-REQUIREMENTS.md` l. 33) : préciser si le gabarit `process/fiche-projet.md` compte dans le plafond. La base mesurée inclut les passages « Kit » ajoutés par ce cadrage.
- **S-4** — `01-REQUIREMENTS.md` l. 121 et 123 : NFR-009 (« trois feux verts par tâche ») et NFR-012 (exceptions des ADR 0012 et 0013) sont dites « Valable » sans le niveau *léger*. Ajouter « deux en *léger* (FR-052) » et « en *léger*, le coordinateur committe et ouvre la PR (ADR 0016) ».
- **S-5** — `GLOSSARY.md` l. 26 (« Pipeline ») et `01-REQUIREMENTS.md` l. 47 (état de FR-021) : « tenu par l'orchestrateur de tâche ». Ajouter « ou par le coordinateur au niveau *léger* ».
- **S-6** — ADR 0016 l. 93 : l'ADR 0009 est dite « Valable » alors que la ligne liste une part caduque. Écrire plutôt « Valable en partie », comme pour 0008 et 0011, puisque le statut à reporter à l'acceptation en dépend (l. 101).
- **S-7** — Mesure (§2 l. 36, critères de fin des trois issues) : le temps est donné au feu vert merge, après l'ouverture de la PR. Dire qui l'inscrit (le coordinateur avant le merge, par `gh pr edit` ou par un commentaire de PR), sachant que c'est une écriture `gh` soumise à la garde de sortie.
- **S-8** — `docs/process/README.md` l. 3 : l'introduction (« En attendant que jam sache dérouler son pipeline… alimente E0 ») et la l. 109 (« dans jam, c'est le cœur qui injectera ce contexte ») sont fausses depuis l'ADR 0016 et le resteront jusqu'à K1-2. Le brief limite les retouches du process à l'ADR 0017 : au mieux, une ligne de statut en tête qui renvoie à l'ADR 0016 et à K1-2.
- **S-9** — K1-1 est de loin le plus gros lot du jalon : retrait de l'app, quatre hooks, une garde étendue, deux scripts, manifeste, CI, installation, fiche concept. Pour tenir les deux ou trois jours, le plan pourrait ordonner le travail de façon que les scripts (FR-046, priorité S) passent en dernier et puissent sortir du lot.

RELECTURE : CORRECTIONS (11)
