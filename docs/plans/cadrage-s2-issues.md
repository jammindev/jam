# Brouillons d'issues — cadrage `cadrage-s2`

> Rédigés par le rédacteur. Le coordinateur les publie sur `jammindev/jam` après le feu vert de cadrage, une fois la PR du cadrage mergée (feu vert merge) : leurs renvois vers les docs fonctionnent alors sur `main`.
> Ce brouillon remplace les §1 à §3 de [`specs-retours-dora-issues.md`](specs-retours-dora-issues.md), relu avec la PR #6 mais antérieur à RET-010, RET-011, aux ADR 0013 à 0015 et à Q-050. L'ancien fichier reste, comme trace de son cadrage, avec en tête un renvoi vers celui-ci.
> Une issue = un petit lot ([ADR 0011](../decisions/0011-pratiques-et-metriques-dora.md)). Aucune date d'échéance sur les milestones (décision du mainteneur).

**Lecture des sections d'issue** : le titre publié est le texte après « S2-x — ». Le corps publié commence à la ligne **Exigences** et va jusqu'à la fin de la section. Les lettres S2-a à S2-h ne sont pas des numéros GitHub. Elles servent aussi de renvoi dans `OPEN-QUESTIONS.md` et dans le profil du recetteur, qui donnent le titre de l'issue : on la retrouve sur GitHub par ce titre publié. Dans les corps d'issues, chaque renvoi « S2-x » est remplacé à la publication par le numéro réel de l'issue, dans une seconde passe une fois les huit issues créées, puisque des corps renvoient à des issues suivantes (voir §6).

**Conduite des tâches** : chaque issue est une tâche, avec son worktree `<numéro>-<slug>` créé par le coordinateur et son orchestrateur de tâche ([ADR 0013](../decisions/0013-orchestration-deux-niveaux.md), [ADR 0015](../decisions/0015-remontee-carte-seule-coordinateur-flottant.md)). Pour chacune, l'orchestrateur de tâche prépare le clone de référence d'Orca et le donne au planificateur, dont le plan a une section « Orca » (RET-011). Le bloc **Orca** de chaque corps dit quelles entrées de la carte (§0 de [`docs/references/orca.md`](../references/orca.md)) consulter.

## 1. Milestones

| Milestone | Titre | Description |
|---|---|---|
| #1 | `E0-S1 Squelette` | Fermé. Aucune action. |
| #2 | `E0-S2 Issue → worktree → un rôle` (inchangé) | À mettre à jour, voir ci-dessous. |
| #3 | `E0-S3 Pipeline jusqu'à la PR` (inchangé) | À mettre à jour, voir ci-dessous. |
| #4 | **À renommer** `E0-S4 Merge, nettoyage, parallélisme, métriques` (titre actuel : `E0-S4 Merge et parallélisme`) | À mettre à jour, voir ci-dessous. |

État relevé sur GitHub le 2026-10-09 : le renommage du S4 et les descriptions prévus par le cadrage `specs-retours-dora` n'ont pas été publiés. Les descriptions en ligne sont encore les anciennes, plus courtes. Les textes ci-dessous reprennent ceux de l'ancien brouillon, alignés sur `04-ROADMAP.md`.

**E0-S2** :
> Lecture des issues via `gh`, création du worktree et de sa branche, exécution du planificateur en headless avec son profil (ADR 0009), injection du contexte d'environnement au rôle (FR-038), état SQLite horodaté (FR-036), fil résumé. Fini quand : le mainteneur choisit l'issue n de `house`, le worktree est créé et le plan s'affiche ; le planificateur est lancé avec son profil de permissions ; le brief qu'il reçoit contient le worktree, l'issue, l'étape et le process ; l'état enregistre le début et la fin de l'étape ; le fil résumé montre les événements significatifs de l'étape ; après redémarrage de l'app, l'état est conservé. Fiches concept : worktree, stream-json.

**E0-S3** :
> Enchaînement des rôles, boucle tests, boucle de relecture jusqu'à OK (pour le code, au moins deux relecteurs neufs, un par axe), garde-fous (itérations, budget, absence de progrès en relecture), trois feux verts, file « À toi », notifications filtrées. Fini quand : une vraie issue de `house` arrive jusqu'à une PR avec la CI verte, le mainteneur n'intervient que via la file, et seuls les passages dans la file déclenchent une notification. Fiche concept : boucle extérieure. Découpé en petites issues au début du jalon.

**E0-S4** :
> Feu vert 3 → `gh pr merge`, suppression du worktree et des branches, trois tâches en parallèle, écran minimal des métriques DORA et désignation du workflow de déploiement par repo (FR-037, ADR 0011). Fini quand : trois issues de `house` traversent le pipeline en parallèle jusqu'au merge (critère de fin d'E0) ; l'écran « Métriques » affiche, pour `house`, les cinq métriques DORA et les indicateurs agents, et pour jam, les cinq métriques ; les indicateurs agents de jam peuvent rester vides tant que ses tâches passent par Orca (ADR 0011 §5). Fiche concept : métriques DORA. Ce second critère, comme la fiche concept métriques DORA, tombe si l'écran est coupé, et se limite à `house` si le multi-repo est coupé. Découpé en petites issues au début du jalon.

## 2. Sort des issues existantes

| Issue | Proposition | Commentaire à poster |
|---|---|---|
| #2 Issue → worktree → un rôle | **Fermée**, remplacée par les huit issues S2 ci-dessous. | « Remplacée par #A, #B, #C, #D, #E, #F, #G et #H : le jalon est découpé en petits lots (ADR 0011). Les fiches concept worktree et stream-json sont dans les critères de fin de #C et #F. » (#A à #H : numéros réels de S2-a à S2-h, #C celui de S2-c, #F celui de S2-f) |
| #3 Pipeline jusqu'à la PR | **Fermée.** Le périmètre et le critère de fin restent dans la description du milestone, jusqu'au découpage au début du S3. | « Le S3 sera découpé en petites issues au début du jalon, par un cadrage (ADR 0011). Le périmètre et le critère de fin sont dans la description du milestone « E0-S3 Pipeline jusqu'à la PR ». » |
| #4 Merge, nettoyage et parallélisme | **Fermée**, même raison. | « Le S4 sera découpé en petites issues au début du jalon, par un cadrage (ADR 0011). Le périmètre et le critère de fin sont dans la description du milestone « E0-S4 Merge, nettoyage, parallélisme, métriques ». » |

La proposition de l'ancien brouillon est confirmée. Pourquoi fermer #3 et #4 plutôt que les garder ouvertes : une issue ouverte d'une semaine de travail peut être prise pour une tâche, à l'encontre des petits lots. Le milestone suffit à garder le périmètre visible.

Les trois issues sont fermées avec la raison « not planned » : aucune n'est livrée telle quelle, et une fermeture « completed » laisserait croire à une livraison.

## 3. Ordre, dépendances et taille

| Issue | Dépend de | Migration SQLite |
|---|---|---|
| S2-a — base par instance | — | Non |
| S2-b — lister les issues | S2-a | Non |
| S2-c — créer la tâche | S2-a, S2-b | Oui (tâches) |
| S2-d — ligne de commande d'un rôle | S2-a | Non |
| S2-e — brief d'un rôle | S2-b, S2-c | Non |
| S2-f — lire un flux `stream-json` | S2-a | Non |
| S2-g — lancer un rôle et enregistrer son étape | S2-c, S2-d, S2-e, S2-f | Oui (étapes) |
| S2-h — étape plan de bout en bout | S2-g | Non |

**Ordre conseillé** : S2-a → S2-b → … → S2-h, chacune lancée après le merge de la précédente. Avec environ 3 agents actifs et deux relecteurs par diff de code, une seule tâche avance vraiment à la fois (Q-038). S2-d et S2-f ne dépendent que de S2-a et n'ajoutent pas de migration : une fois S2-a mergée, le coordinateur peut les lancer plus tôt, en parallèle, si le plafond d'agents actifs le permet.

**Migrations** : seules S2-c et S2-g en ajoutent une, à la même liste ([ADR 0010](../decisions/0010-persistance-sqlite.md)). S2-g vient après S2-c : pas de conflit. Les refus et le brief, que l'ancien brouillon enregistrait dans S2-d et S2-e, sont enregistrés avec l'étape par S2-g, qui pose la table des étapes : S2-d et S2-e n'écrivent pas dans la base.

**S2-a avant toutes les autres** (Q-050) : le cœur refuse d'ouvrir une base d'une version plus récente que son code. Sur la base partagée, le risque joue dans les deux sens :
- une recette lancée depuis le worktree de S2-c la migrerait : l'instance du mainteneur, lancée depuis `main`, ne s'ouvrirait plus jusqu'au merge, et les tâches d'essai iraient dans la base réelle ;
- une tâche partie de `main` avant le merge de S2-c (S2-d lancée plus tôt, par exemple) trouverait à sa recette une base déjà migrée, et son app refuserait de l'ouvrir.

D'où la règle : aucune tâche du S2 ne démarre avant le merge de S2-a, et toute recette, de l'agent comme du mainteneur, lance l'app avec `JAM_DATA_DIR` sur un dossier temporaire.

**Taille des lots**, par rapport à l'ancien brouillon :
- **ajoutée** : S2-a, pour Q-050 ;
- **redécoupée** : l'ancienne S2-c (lancement, lecture du flux, état, essai réel, fiche concept) devient S2-f (lire le flux, sans lancer) et S2-g (lancer et enregistrer). Elle aurait aussi reçu l'enregistrement des refus et du brief ;
- **allégées** : les anciennes S2-d et S2-e deviennent des modules sans écriture dans la base ;
- **pas de fusion** : la ligne de commande (S2-d) et le brief (S2-e) restent deux issues, car elles ne dépendent pas l'une de l'autre et chacune a sa question propre (Q-012 pour S2-d, FR-038 pour S2-e).

| Ancien brouillon | Ce brouillon |
|---|---|
| — | S2-a |
| S2-a | S2-b |
| S2-b | S2-c |
| S2-d (sans l'enregistrement des refus) | S2-d |
| S2-e (sans l'enregistrement du brief) | S2-e |
| S2-c, lecture du flux | S2-f |
| S2-c, lancement et état ; refus de S2-d ; brief de S2-e | S2-g |
| S2-f | S2-h |

## 4. Issues du S2

### S2-a — Une base par instance en développement : l'app suit `JAM_DATA_DIR`

- **Milestone** : `E0-S2 Issue → worktree → un rôle` · **Labels** : `enhancement`

**Exigences** : ADR 0010 ; Q-050

**Pourquoi**
Deux instances de jam lancées en même temps, depuis `main` et depuis un worktree, partagent la même base : l'app passe au cœur le chemin de son dossier de données par `--db`, et `JAM_DATA_DIR` ne la déplace pas. À partir du S2, des tâches ajoutent des migrations. Le cœur refuse une base plus récente que son code : une recette lancée depuis un worktree migrerait la base partagée, et l'instance lancée depuis `main` ne s'ouvrirait plus jusqu'au merge.

**Périmètre**
- Quand `JAM_DATA_DIR` est défini, l'app ouvre `jam.db` dans ce dossier, comme le cœur lancé en CLI.
- Sans la variable, rien ne change : l'app ouvre la base de son dossier de données.

**Critère de fin**
- `JAM_DATA_DIR=<dossier vide> pnpm dev` ouvre l'app et crée `<dossier vide>/jam.db`. Dans cette instance, « Lister les repos » ne montre aucun repo ; l'instance lancée sans la variable montre toujours les repos du mainteneur.
- Les tests vérifient le chemin de la base choisi par l'app, avec et sans la variable, et que l'app et le cœur en CLI désignent la même base pour la même valeur de `JAM_DATA_DIR`.
- **Recette** (RET-010) : depuis une installation neuve (`node_modules` supprimés, `pnpm install`), la check-list du mainteneur d'abord, avec ses commandes et dans son ordre. L'agent vérifie que `jam.db` apparaît dans le dossier désigné après `pnpm dev`. Restent à la check-list du mainteneur : « Lister les repos » par la palette (l'agent ne simule pas le clavier) et l'instance lancée sans la variable (l'agent hérite de `JAM_DATA_DIR` pour toutes ses commandes).

**Hors périmètre** : une base par worktree choisie automatiquement ; le dossier de données hors macOS (Q-021).

**Orca** (pour le plan, RET-011) : aucune entrée de la carte ne couvre le dossier de données de l'app. Liste noire, toujours écartée : terminal interactif (PTY) et détection de l'état d'une TUI.

### S2-b — Lister les issues ouvertes d'un repo via `gh`

- **Milestone** : `E0-S2 Issue → worktree → un rôle` · **Labels** : `enhancement`

**Exigences** : FR-020

**Dépend de** : S2-a (une base par instance, pour la recette)

**Périmètre**
- Le cœur lit les issues ouvertes d'un repo configuré avec `gh`, et valide la réponse avec zod. Les pull requests n'y figurent pas.
- Une méthode du protocole expose cette liste (numéro, titre).
- Une commande de palette « Choisir une issue » l'affiche, pour un repo choisi parmi les repos configurés.

**Critère de fin**
- Sur `house`, Cmd+K → « Choisir une issue » liste les issues ouvertes.
- Les tests simulent la sortie de `gh` : liste vide ; `gh` absent ; `gh` non authentifié ; repo sans remote GitHub. Chaque échec donne un message d'erreur lisible, distinct d'une liste vide.
- **Recette** (RET-010) : depuis une installation neuve (`node_modules` supprimés, `pnpm install`), la check-list du mainteneur d'abord, avec ses commandes et dans son ordre. Elle commence par `gh auth status`. L'app est lancée avec `JAM_DATA_DIR` sur un dossier temporaire (S2-a), où `house` est ajouté par la palette. Deux étapes ne sont pas reproduites par l'agent et restent à la check-list du mainteneur ; le rapport les note « non reproduit » : `gh auth status` (`gh` est interdit au profil du recetteur) et Cmd+K (l'agent ne simule pas le clavier). Le critère principal, la liste par la palette, reste donc à la check-list du mainteneur (moyen de le reproduire sans clavier : Q-053) ; l'agent vérifie l'installation, le lancement et les tests.

**Hors périmètre** : création du worktree (S2-c) ; lecture du corps d'une issue (S2-e).

**Questions renvoyées au plan** : nombre d'issues lues (toutes les issues ouvertes, ou une limite). La langue des messages d'erreur reste ouverte (Q-020) : le plan suit la convention en place.

**Orca** (pour le plan, RET-011) : entrées « Liste des issues d'un repo » et « `gh` : issues, PR, checks » de la carte (§0 de `docs/references/orca.md`). Liste noire, toujours écartée : terminal interactif (PTY) et détection de l'état d'une TUI.

### S2-c — Créer la tâche : worktree et branche d'une issue

- **Milestone** : `E0-S2 Issue → worktree → un rôle` · **Labels** : `enhancement`

**Exigences** : FR-020, FR-027, FR-036 ; ADR 0010

**Dépend de** : S2-a (une base par instance, pour la recette), S2-b (choix d'une issue)

**Périmètre**
- Choisir une issue dans « Choisir une issue » crée une **tâche** : un worktree et sa branche, nommés `<numéro>-<slug>`, partis de la branche par défaut du repo.
- La tâche est enregistrée dans SQLite avec son heure de création. La table des tâches arrive par une nouvelle migration numérotée, à la suite de celle du S1 (ADR 0010).
- Une deuxième tâche sur la même issue est refusée.
- Une commande de palette « Lister les tâches » montre les tâches enregistrées.

**Critère de fin**
- Le mainteneur choisit l'issue n de `house` : le worktree `<n>-<slug>` existe, sur sa branche.
- Après redémarrage de l'app, la tâche est toujours listée.
- Les tests couvrent l'issue déjà prise, un titre avec accents ou caractères spéciaux (le slug reste un nom de branche valide pour git) et l'échec de la création du worktree (aucune tâche n'est alors enregistrée).
- **Recette** (RET-010) : depuis une installation neuve (`node_modules` supprimés, `pnpm install`), la check-list du mainteneur d'abord, avec ses commandes et dans son ordre. L'app est lancée avec `JAM_DATA_DIR` sur un dossier temporaire (S2-a), où `house` est ajouté par la palette. La check-list fait noter au mainteneur le chemin du worktree et le nom de la branche créés dans `house`, et se termine par leur suppression, avec les commandes à lancer (le nettoyage automatique vient au S4). Sans clavier simulé, l'agent ne peut ni ajouter `house`, ni choisir l'issue, ni lister les tâches par la palette : ces étapes, donc le critère principal, restent à la check-list du mainteneur. Le moyen de les reproduire sans clavier est une question ouverte (Q-053).
- Fiche concept : worktree.

**Hors périmètre** : lancement d'un rôle (S2-g) ; suppression du worktree et de la branche (S4) ; nouvelle tâche sur une issue dont le worktree a été supprimé (Q-052).

**Questions renvoyées au plan** : emplacement des worktrees créés par jam ; mise à jour de la branche par défaut avant la création (`git fetch`).

**Orca** (pour le plan, RET-011) : entrées « Création et nommage des worktrees » et « Nom d'un worktree et de sa branche depuis une issue » de la carte (§0 de `docs/references/orca.md`). Le mécanisme de migrations de jam existe depuis le S1 : rien à prendre à Orca pour lui. Liste noire, toujours écartée : terminal interactif (PTY) et détection de l'état d'une TUI.

### S2-d — Construire la ligne de commande d'un rôle depuis son profil

- **Milestone** : `E0-S2 Issue → worktree → un rôle` · **Labels** : `enhancement`

**Exigences** : FR-022, NFR-011 ; ADR 0004, ADR 0009 ; Q-012, Q-022, Q-027

**Dépend de** : S2-a (une base par instance, pour la recette)

**Périmètre**
- Le backend Claude Code construit la ligne de commande headless d'un rôle (`claude -p --output-format stream-json`, `--permission-mode dontAsk`, `--allowedTools`, `--disallowedTools`) à partir de son **profil de rôle**. L'emplacement et le format des profils sont tranchés dans le plan (Q-012).
- Le profil du planificateur suit l'ADR 0009 : lecture seule ; shell limité à `git diff`, `git log`, `git status` et à la commande de tests du repo (configuration du repo, FR-028) ; pas de réseau, donc ni `WebSearch` ni `WebFetch` (Q-027).
- Le profil du planificateur n'a **aucun droit d'écriture** : le plan qu'il produit est le texte final de son étape, que le cœur enregistre (S2-g), et non un fichier écrit dans le worktree. C'est la lecture seule de l'ADR 0009, et rien n'est écrit dans le repo cible avant le feu vert plan. Un plan écrit dans un fichier demanderait une ADR qui précise l'ADR 0009.
- Les profils de `docs/process/roles/` servent au déroulé dans Orca et ne sont pas lus tels quels : ils n'existent pas dans les autres repos, et contiennent les formes `rtk` propres au poste et le clone de référence propre aux tâches de jam (RET-011).

**Critère de fin**
- Un test vérifie la ligne de commande construite pour le planificateur contre une liste attendue, écrite dans le test d'après l'ADR 0009 et non lue dans le profil : `--permission-mode dontAsk` ; des outils de lecture seulement, sans outil d'écriture ; un shell limité à `git diff`, `git log`, `git status` et à la commande de tests du repo ; ni `WebSearch` ni `WebFetch`. Un profil qui donnerait l'écriture ou le réseau au planificateur fait échouer ce test.
- Un test vérifie qu'aucune ligne de commande construite, quel que soit le profil, ne contient `bypassPermissions` ni `--dangerously-skip-permissions` (NFR-011).
- Si le profil est une donnée lue dans un fichier, il est validé avec zod, et un profil invalide est refusé avec un message lisible.
- **Recette** (RET-010) : depuis une installation neuve (`node_modules` supprimés, `pnpm install`), la check-list du mainteneur d'abord : `pnpm check` passe et l'app, lancée avec `JAM_DATA_DIR` sur un dossier temporaire (S2-a), se lance comme avant. La ligne de commande devient visible avec S2-g.

**Hors périmètre** : lancement du rôle et lecture des refus (S2-g, S2-f) ; profils des autres rôles (S3).

**Questions renvoyées au plan**
- La commande de tests du repo, autorisée au planificateur, peut exécuter ce que contient le script de tests du repo cible : le plan le note, sans le corriger (sandbox, risque R-03).
- Si l'observation de Q-043 montre qu'une règle `Read` sans chemin lit hors du worktree, le plan le note de même.
- Le Claude Code lancé par jam charge, comme toute session, les réglages et les hooks de l'utilisateur du poste : le hook RTK, qui réécrit `git log` en `rtk git log` avant le contrôle de la permission (Q-022), et le hook de démarrage, qui ajoute un contexte propre à Orca (RET-004). Un profil sans forme `rtk` verrait donc refuser les commandes git que l'ADR 0009 donne au planificateur. Le plan choisit : écarter ces réglages au lancement (par une option de la CLI qui limite les sources de réglages, à vérifier sur la version testée, R-04), ou accepter ces refus à l'essai réel de S2-g et les noter. Ajouter les formes `rtk` au profil est exclu : les profils de jam valent pour tout poste, et `rtk` est propre à celui du mainteneur.

**Orca** (pour le plan, RET-011) : entrée « Ligne de commande d'une CLI d'agent headless, vie de son processus » de la carte (§0 de `docs/references/orca.md`), pour la construction des arguments seulement. À écarter : le lancement des agents sans permission, comportement par défaut d'Orca (ADR 0009). Liste noire, toujours écartée : terminal interactif (PTY) et détection de l'état d'une TUI.

### S2-e — Composer le brief d'un rôle avec son contexte d'environnement

- **Milestone** : `E0-S2 Issue → worktree → un rôle` · **Labels** : `enhancement`

**Exigences** : FR-038 ; RET-004

**Dépend de** : S2-b (issue), S2-c (tâche et worktree)

**Périmètre**
- Le brief d'un rôle contient, en plus de sa consigne : le worktree, l'issue (numéro, titre, corps), l'étape en cours et le process suivi, c'est-à-dire la liste des étapes du pipeline, la place de l'étape en cours et les feux verts qui suivent.
- Le corps de l'issue est lu avec `gh` et validé avec zod.

**Critère de fin**
- Un test vérifie que le brief du planificateur contient : le chemin du worktree, le numéro, le titre et le corps de l'issue, le nom de l'étape, la liste des étapes du pipeline avec l'étape en cours repérée, et les feux verts qui suivent.
- Un test couvre une issue sans corps.
- **Recette** (RET-010) : depuis une installation neuve (`node_modules` supprimés, `pnpm install`), la check-list du mainteneur d'abord : `pnpm check` passe et l'app, lancée avec `JAM_DATA_DIR` sur un dossier temporaire (S2-a), se lance comme avant. Le brief devient visible avec S2-g.

**Hors périmètre** : enregistrement du brief avec l'étape (S2-g) ; briefs des autres rôles (S3).

**Questions renvoyées au plan** : moment de la lecture du corps (à la création de la tâche, ou au lancement du rôle).

**Orca** (pour le plan, RET-011) : entrée « Orchestration durable (run, task, mailbox) » de la carte (§0 de `docs/references/orca.md`), fichier `src/main/runtime/orchestration/preamble.ts` seulement : la forme du contexte injecté à un agent lancé. À écarter : ce que le préambule demande à l'agent (signaler sa fin, battements de cœur), qui repose sur son obéissance ; dans jam, le cœur connaît la fin de l'étape par le flux. Liste noire, toujours écartée : terminal interactif (PTY) et détection de l'état d'une TUI.

### S2-f — Lire un flux `stream-json`

- **Milestone** : `E0-S2 Issue → worktree → un rôle` · **Labels** : `enhancement`

**Exigences** : FR-011, FR-012 ; ADR 0004, ADR 0009 ; risque R-04

**Dépend de** : S2-a (une base par instance : aucune tâche du S2 ne démarre avant son merge)

**Périmètre**
- Le flux de Claude Code headless est lu et validé avec zod en un seul endroit, le backend Claude Code (R-04).
- Les événements sont normalisés : début de session (identifiant de session), messages et outils appelés, résultat (réussi ou en échec, coût, durée), refus de permission avec l'outil et l'entrée demandés (champ `permission_denials` du résultat, à vérifier, ADR 0009).
- Les événements normalisés ne dépendent pas de Claude Code : ce sont ceux que tout backend d'agent émettra, le harness maison compris (FR-011, ADR 0004). Seul le backend Claude Code connaît le format `stream-json`.
- Une ligne invalide ou d'un type inconnu n'arrête pas la lecture.
- La version de Claude Code testée est notée avec les flux de test (R-04).

**Critère de fin**
- Un test rejoue un flux enregistré : événements normalisés, identifiant de session, coût et état final de l'exécution (réussie ou en échec) relevés.
- Un test rejoue un flux qui contient un refus : le refus est relevé avec l'outil et l'entrée demandés.
- Un test couvre une ligne invalide au milieu d'un flux réussi : la lecture continue, les événements suivants sont normalisés et l'exécution est réussie.
- Un autre test couvre un flux coupé avant son résultat : l'exécution n'est pas comptée comme réussie.
- **Recette** (RET-010) : depuis une installation neuve (`node_modules` supprimés, `pnpm install`), la check-list du mainteneur d'abord : `pnpm check` passe.
- Fiche concept : stream-json.

**Hors périmètre** : lancement de Claude Code et enregistrement de l'étape (S2-g) ; reprise de session par `--resume` (S3) ; branchement du harness maison comme deuxième backend (E2).

**Questions renvoyées au plan** : provenance des flux de test. L'implémenteur ne lance pas Claude Code (sa liste blanche ne le permet pas) : flux écrits d'après le format documenté, ou enregistrés par le mainteneur avec une commande que donne le plan. L'essai réel de S2-g confirme la lecture sur un flux réel.

**Orca** (pour le plan, RET-011) : entrées « Lancement d'une CLI d'agent en headless » (le schéma des événements `stream-json`, pour le format seulement) et « Fin d'une exécution headless : résultat `stream-json` » de la carte (§0 de `docs/references/orca.md`). À écarter : l'Agent SDK (ADR 0004) et la relecture des transcripts propres à chaque CLI. Liste noire, toujours écartée : terminal interactif (PTY) et détection de l'état d'une TUI.

### S2-g — Lancer un rôle en headless et enregistrer son étape

- **Milestone** : `E0-S2 Issue → worktree → un rôle` · **Labels** : `enhancement`

**Exigences** : FR-012, FR-027, FR-036, NFR-011 ; ADR 0004, ADR 0009, ADR 0010 ; risque R-02

**Dépend de** : S2-c (tâche), S2-d (ligne de commande), S2-e (brief), S2-f (lecture du flux)

**Périmètre**
- Le cœur lance Claude Code headless dans le worktree d'une tâche, avec la ligne de commande construite depuis le profil du rôle (S2-d) et le brief (S2-e), et lit son flux (S2-f).
- Une **étape** est enregistrée, par une nouvelle migration numérotée : tâche, rôle, ligne de commande, brief envoyé, identifiant de session, coût, heures de début et de fin, état final de l'étape (réussie, en échec, interrompue), texte final du résultat (pour le planificateur, c'est le plan : S2-d), et les événements résumés pour le fil d'activité (début, fin, coût, refus avec la commande demandée) (ADR 0010).
- Une commande de palette « Lancer le planificateur » lance l'étape sur une tâche existante. À la fin de l'étape, elle affiche l'étape telle qu'elle est enregistrée, relue dans la base : c'est par là que le mainteneur la lit, en attendant la vue de la tâche (S2-h).
- Si le cœur s'arrête **normalement** pendant l'étape (fermeture de son entrée standard par l'app, ou signal d'arrêt), il arrête le processus de Claude Code avant de sortir, dans le délai de 2 s que l'app lui laisse avant de le tuer : aucun agent orphelin ne consomme le quota (R-02). C'est le cas courant de la fermeture de l'app pendant une étape. Or le cœur attend aujourd'hui la réponse de chaque requête en cours avant de sortir, et « Lancer le planificateur » ne répond qu'à la fin de l'étape. Le plan choisit le moyen : répondre à la requête en attente par une étape interrompue, ou ne pas attendre la fin de l'étape pour répondre.
- Au démarrage suivant, une étape sans heure de fin est marquée interrompue, quelle que soit la façon dont le cœur s'est arrêté.

**Critère de fin**
- Essai réel sur une tâche de `house` : le planificateur tourne en `dontAsk` avec son profil, jamais sans permission (ADR 0009), et l'étape se termine. L'étape qu'affiche « Lancer le planificateur » à la fin contient la ligne de commande, le brief (numéro et titre de l'issue, chemin du worktree), l'identifiant de session, le coût et les heures de début et de fin.
- Les tests lancent un faux Claude Code qui rejoue des flux enregistrés : étape réussie, en échec, avec un refus enregistré.
- Un test ferme l'entrée standard du cœur pendant une étape, alors que la requête qui l'a lancée attend sa réponse : le processus enfant est arrêté et le cœur sort en moins de 2 s, le délai que lui laisse l'app (`apps/desktop/src/main/core-process.ts`). Un test fait de même avec un signal d'arrêt. Un autre test rouvre la base avec une étape sans heure de fin : elle est marquée interrompue.
- **Recette** (RET-010) : depuis une installation neuve (`node_modules` supprimés, `pnpm install`), la check-list du mainteneur d'abord, avec ses commandes et dans son ordre. L'app est lancée avec `JAM_DATA_DIR` sur un dossier temporaire (S2-a). L'essai réel consomme du quota : une seule étape. La check-list fait noter au mainteneur le chemin du worktree et le nom de la branche créés dans `house`, et se termine par leur suppression, avec les commandes à lancer. Sans clavier simulé, l'agent ne peut ni créer la tâche ni lancer « Lancer le planificateur » par la palette : l'essai réel, critère principal, reste à la check-list du mainteneur (moyen de le reproduire sans clavier : Q-053). L'agent couvre le reste par les tests au faux Claude Code. Réglages et hooks du poste (Q-022, choix du plan de S2-d) : la check-list le vérifie dans l'étape enregistrée. Si jam les écarte, la ligne de commande enregistrée contient l'option retenue au plan de S2-d. Sinon, tout refus survenu est enregistré dans l'étape, avec la commande demandée. La check-list prend une issue de `house` qui n'a servi à aucune recette précédente : un worktree supprimé puis recréé au même chemin `<n>-<slug>` hériterait de l'historique de Claude Code de l'ancien (Q-052).

**Hors périmètre** : enchaînement du choix d'une issue jusqu'au plan, et affichage (S2-h) ; passage à « bloqué » et file « À toi » sur un refus (S3) ; reprise d'une étape interrompue et cœur qui survit à l'app (Q-014) ; cœur tué (par exemple le `SIGKILL` que l'app envoie au bout de 2 s si le cœur ne s'est pas arrêté) ou planté : il ne peut pas arrêter son enfant, l'étape est seulement marquée interrompue au démarrage suivant, et un agent orphelin reste possible. Le plan peut lancer Claude Code dans son propre groupe de processus, sans que ce soit exigé.

**Orca** (pour le plan, RET-011) : entrées « Lancement d'une CLI d'agent en headless » (le lancement du processus) et « Ligne de commande d'une CLI d'agent headless, vie de son processus » (délai maximal, arrêt du processus enfant) de la carte (§0 de `docs/references/orca.md`). À écarter : le lancement sans permission (ADR 0009). Liste noire, toujours écartée : terminal interactif (PTY) et détection de l'état d'une TUI.

### S2-h — Étape plan de bout en bout et fil résumé

- **Milestone** : `E0-S2 Issue → worktree → un rôle` · **Labels** : `enhancement`

**Exigences** : FR-027, FR-033

**Dépend de** : S2-g (étape enregistrée)

**Périmètre**
- Choisir une issue enchaîne : création de la tâche, lancement du planificateur, affichage du plan produit, c'est-à-dire le texte final de l'étape enregistré par S2-g (S2-d).
- Une vue de la tâche montre son étape (avec la ligne de commande du rôle), son état et son **fil résumé** : les événements significatifs (tâche créée, étape commencée, étape terminée avec sa durée et son coût, refus, échec ou interruption), pas chaque message.
- La vue suit l'étape en cours sans relancer l'app. Le mécanisme, interrogation régulière du cœur ou notifications du cœur vers l'UI, est tranché dans le plan (Q-015, Q-017).

**Critère de fin**
- Le mainteneur choisit l'issue n de `house` : le worktree est créé et le plan s'affiche.
- Le planificateur est lancé avec la ligne de commande construite depuis son profil, visible dans la vue de la tâche.
- La vue de la tâche, ouverte pendant l'étape, passe d'« en cours » à « terminée » et affiche le plan sans être rouverte ni relancée, et l'app reste utilisable pendant l'étape.
- Le fil résumé montre le début et la fin de l'étape, son coût et ses éventuels refus.
- Après redémarrage de l'app, la tâche, son étape, son fil et son plan sont conservés.
- **Recette** (RET-010) : depuis une installation neuve (`node_modules` supprimés, `pnpm install`), la check-list du mainteneur d'abord, avec ses commandes et dans son ordre. L'app est lancée avec `JAM_DATA_DIR` sur un dossier temporaire (S2-a). La check-list fait noter au mainteneur le chemin du worktree et le nom de la branche créés dans `house`, et se termine par leur suppression, avec les commandes à lancer. Sans clavier simulé, l'agent ne peut pas choisir l'issue par la palette : le parcours de bout en bout, le suivi de l'étape par la vue ouverte et l'affichage du plan, critère principal, restent à la check-list du mainteneur (moyen de les reproduire sans clavier : Q-053). La check-list prend une issue de `house` qui n'a servi à aucune recette précédente, celles de S2-c et S2-g comprises : un worktree supprimé puis recréé au même chemin `<n>-<slug>` hériterait de l'historique de Claude Code de l'ancien (Q-052).

**Hors périmètre** : feu vert 1 et étapes suivantes, file « À toi » et notifications (S3).

**Orca** (pour le plan, RET-011) : aucune brique de la carte n'est propre à cette issue. L'entrée « Statut par worktree » (modèle à 4 états) ne sert que si le plan définit des états de tâche. À écarter : la relecture des transcripts propres à chaque CLI pour le fil ; jam résume les événements du flux qu'il a déjà lus. Liste noire, toujours écartée : terminal interactif (PTY) et détection de l'état d'une TUI.

## 5. Questions ouvertes qui touchent le S2

| Question | Sort | Où |
|---|---|---|
| Q-050 — base partagée entre deux instances | **Tranchée** : l'app suit `JAM_DATA_DIR` (S2-a), aucune tâche du S2 ne démarre avant le merge de S2-a, et toute recette lance l'app avec un dossier de données propre | S2-a ; profil du recetteur ; `OPEN-QUESTIONS.md` |
| Q-012 — emplacement et format des profils de rôle | Renvoyée au plan de S2-d | S2-d ; `OPEN-QUESTIONS.md` |
| Q-022 — hook RTK du poste et permissions des rôles | Pour le Claude Code lancé par jam, renvoyée au plan de S2-d : écarter les réglages et hooks du poste au lancement, ou accepter des refus à l'essai réel de S2-g, dont la check-list dit ce qu'elle attend. Les formes `rtk` n'entrent pas dans les profils de jam. Reste ouvert : lancer sans RTK les rôles déroulés dans Orca | S2-d, S2-g ; `OPEN-QUESTIONS.md` |
| Q-027 — profil du planificateur (`git diff`, commande de tests, réseau) | **Tranchée en partie** : le profil que jam construit suit l'ADR 0009, sans réseau. Reste ouvert : le profil du planificateur dans Orca, qui revient au mainteneur | S2-d ; `OPEN-QUESTIONS.md` |
| Q-040 — montée de la version de référence d'Orca ; référence de lecture dans la configuration d'un repo | Laissée ouverte. Le S2 lance le planificateur sur `house`, qui n'a pas de référence de lecture : la question ne pèse pas sur le format des profils de S2-d | `OPEN-QUESTIONS.md` |
| Q-043 — accès au clone par `Read` et `--add-dir` | Laissée ouverte. Elle se tranche au premier plan qui reçoit le clone, celui de S2-a, par son orchestrateur de tâche. S2-d note la réponse si elle touche les profils de jam | S2-d |
| Q-015, Q-017 — notifications du cœur vers l'UI | Renvoyées au plan de S2-h, pour le suivi d'une étape en cours | S2-h ; `OPEN-QUESTIONS.md` (Q-015) |
| Q-014 — cœur qui survit à l'app | Laissée ouverte (S3). S2-g arrête Claude Code quand le cœur s'arrête normalement, et marque interrompue une étape restée sans fin ; un cœur tué ou planté peut laisser un agent orphelin | S2-g |
| Q-020 — langue des messages d'erreur | Laissée ouverte. S2-b suit la convention en place | S2-b |
| Q-038 — plafond d'agents actifs et parallélisme | Laissée ouverte. Elle fixe l'ordre conseillé (§3) | §3 |
| Q-052 — nouvelle tâche sur une issue dont le worktree a été supprimé | **Nouvelle**, pour le S4. Elle se pose dès les recettes du S2, qui suppriment à la main le worktree créé dans `house` : les check-lists de S2-g et S2-h prennent une issue qui n'a servi à aucune recette précédente | S2-c, S2-g, S2-h ; `OPEN-QUESTIONS.md` |
| Q-053 — reproduire sans clavier les recettes qui passent par la palette | **Nouvelle**, laissée au mainteneur. D'ici là, le critère principal de S2-b, S2-c, S2-g et S2-h reste à la check-list du mainteneur | S2-b, S2-c, S2-g, S2-h ; `OPEN-QUESTIONS.md` |

## 6. Actions de publication (coordinateur)

Après le feu vert de cadrage, la PR du cadrage, le feu vert merge et le merge. Dans cet ordre :

**Textes par fichier.** Les descriptions, titres, corps et commentaires contiennent des apostrophes (« l'issue », « jusqu'à ») et des accents graves (`` `gh` ``) : passés en ligne entre apostrophes, le shell couperait la chaîne ; entre guillemets doubles, il exécuterait les accents graves. Chaque texte est donc écrit dans un fichier temporaire, puis passé par fichier. Les seuls textes passés en ligne, entre apostrophes, n'en contiennent pas (titre du milestone S4, titre du milestone S2, raison de fermeture).

1. **Milestones** (avant la fermeture de #3 et #4, dont les commentaires renvoient aux descriptions). Revérifier d'abord les numéros avec `gh api 'repos/jammindev/jam/milestones?state=all'` (entre apostrophes : sous zsh, `?` est un joker) :
   - `gh api -X PATCH repos/jammindev/jam/milestones/2 -F description=@<fichier : texte E0-S2 du §1>` ;
   - `gh api -X PATCH repos/jammindev/jam/milestones/3 -F description=@<fichier : texte E0-S3 du §1>` ;
   - `gh api -X PATCH repos/jammindev/jam/milestones/4 -f title='E0-S4 Merge, nettoyage, parallélisme, métriques' -F description=@<fichier : texte E0-S4 du §1>`.
2. **Issues S2**, en deux passes, car des corps renvoient à des issues suivantes (S2-b à S2-c et S2-e, S2-d à S2-f et S2-g, par exemple) :
   - **création**, dans l'ordre S2-a → S2-h, pour que les numéros suivent l'ordre conseillé : `gh issue create --repo jammindev/jam --title "$(cat <fichier du titre>)" --milestone 'E0-S2 Issue → worktree → un rôle' --label enhancement --body-file <fichier du corps>`. Le résultat d'une substitution `$(…)` n'est pas réinterprété : apostrophes et accents graves du titre passent tels quels. Relever le numéro de chaque issue créée ;
   - **substitution**, une fois les huit numéros connus : dans chaque corps, remplacer chaque « S2-x » par le numéro de l'issue correspondante (`#n`), puis `gh issue edit <n> --repo jammindev/jam --body-file <fichier du corps substitué>`. Vérifier qu'aucun corps publié ne contient plus « S2- ».
3. **Fermer #2** : `gh issue close` n'accepte pas de fichier pour son commentaire, qui est donc posté d'abord :
   - `gh issue comment 2 --repo jammindev/jam --body-file <fichier : commentaire du §2, numéros substitués>` ;
   - `gh issue close 2 --repo jammindev/jam --reason 'not planned'`.
4. **Fermer #3 et #4**, de même, avec leurs commentaires du §2.
5. Milestone `E0-S1 Squelette` : déjà fermé, rien à faire.

## 7. Hors du repo

Aucune issue pour l'outillage du poste du mainteneur (gardes, hooks) : il reste hors du repo (ADR 0012, Q-036).
