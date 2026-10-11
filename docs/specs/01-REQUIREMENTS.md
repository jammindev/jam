# 01 — Exigences

> Statut : réécrit le 2026-10-11 pour le kit (RET-014, RET-016, [ADR 0016](../decisions/0016-kit-de-methode.md)). Les exigences de l'app sont gardées plus bas avec leur état : un numéro n'est jamais réutilisé. Priorités MoSCoW : **M**ust, **S**hould, **C**ould, **W**on't (pour l'instant).

## Exigences du kit (jalon K1)

### Fonctionnelles

| ID | Exigence | Priorité | Source |
|---|---|---|---|
| FR-042 | Le kit est un plugin Claude Code, dont le repo jam est la racine. Il s'installe une fois sur le poste de travail. | M | RET-014, ADR 0016 |
| FR-043 | Le plugin porte la référence de la méthode : le déroulé (`process/`) et les sept profils de rôle (`roles/`), génériques, sans rien de propre à un projet. Remplace FR-021 ; s'appuie sur FR-022 à FR-026 et FR-040. | M | RET-014, RET-016 |
| FR-044 | Les garde-fous en code sont des hooks du plugin (`hooks/`), versionnés avec leurs tests et câblés par l'installation du plugin : garde du coordinateur ; **garde de sortie unique** (commit, push, merge, écritures `gh`), qui remplace les gardes de sortie qui se recouvrent sur le poste ; reprise de contexte ; contrôle d'état git. Remplace FR-038. | M | RET-014, RET-016, ADR 0012 |
| FR-045 | Chaque projet a une **fiche projet**, `docs/methode.md`, et rien d'autre de la méthode : niveau par défaut (FR-049), commande de test, grille de relecture, recette, sens d'un merge (mise en production ou non), plafond d'agents du projet, borne propre au projet en plus du plafond global (FR-051). Le plugin en fournit le gabarit. Remplace FR-028. | M | RET-014, RET-016 |
| FR-046 | Scripts du plugin (`scripts/`) : veille des cartes Orca d'un projet ; lancement d'une tâche (worktree, session de l'orchestrateur de tâche ou d'un rôle, brief). | S | RET-014, RET-016 |
| FR-047 | Skills du plugin (`skills/`), par exemple : lancer une tâche, présenter un feu vert, reprise. | W | RET-014. Retirée du jalon K1 (RET-016, Q-062) |
| FR-048 | Modèles du plugin (`modeles/`) : brief d'orchestrateur de tâche, plan, rapports de relecture et de recette. | W | RET-014. Retirée du jalon K1 (RET-016, Q-062) |
| FR-049 | Chaque tâche a un **niveau**. Le niveau par défaut est celui du projet, fixé par sa fiche selon son risque : *standard* (déroulé complet) pour un projet en production qui touche à l'argent ou à des données de personnes, *léger* partout ailleurs. Une tâche peut monter d'un niveau, motivé dans l'issue ou au plan ; au-dessus de *standard*, *renforcé* (Q-061). | M | RET-014, RET-016 |
| FR-050 | **Seuil « assez bon »** : un tour de relecture qui ne trouve que du cosmétique clôt la boucle de relecture. Précise FR-023 et FR-024. | M | RET-014 |
| FR-051 | **Plafond d'agents global** au poste de travail, tous projets confondus. Il porte sur les agents en cours : les sessions d'agent que liste `orca terminal list`, qu'elles travaillent ou attendent. Toute session qui lance un agent (coordinateur, ou orchestrateur de tâche au niveau *standard*) les compte avant de le lancer, par exemple par le script de lancement, et ne le lance que si ni ce plafond ni celui de son projet (FR-045) ne sont atteints. Remplace FR-029. | M | RET-014 |
| FR-052 | En niveau *léger*, pas d'orchestrateur de tâche ni de planificateur : l'issue tient lieu de plan, sans feu vert plan ; le coordinateur lance l'implémenteur (ou le rédacteur), puis un seul relecteur, et tient la carte, le commit, la PR et le merge. Pas de recette par un agent. | M | RET-016, ADR 0016 |
| FR-053 | Relais d'un feu vert : la forme complète (mots exacts, heure, session) reste exigée pour le merge d'un projet en production et pour tout feu vert qu'aucune règle n'allège ; pour le feu vert plan et le feu vert recette, un « ok » transmis suffit. Un feu vert remonté par la carte pour une action du coordinateur (merge, publication) est confirmé par le mainteneur dans le terminal du coordinateur (garde de sortie, FR-044). | M | RET-016 |
| FR-054 | Recette d'une interface : quand un navigateur piloté (Playwright) est disponible, le recetteur livre des captures ou un enregistrement du parcours. | S | RET-016 |
| FR-055 | Une seule mesure, notée à la main dans la PR ou le plan : le temps passé par le mainteneur sur l'issue. | M | RET-016. Remplace FR-036 et FR-037 |
| FR-056 | Le `README.md` de jam est la page publique de la méthode : courte, factuelle, avec les seuls chiffres mesurés (FR-055). | M | RET-016 |

### Non fonctionnelles

| ID | Exigence | Priorité | Source |
|---|---|---|---|
| NFR-013 | Rien d'indispensable à la méthode ne vit dans un dossier temporaire ni hors d'un dépôt, sauf ce qui est propre au poste, dans un dossier durable du poste. | M | RET-015, ADR 0017 |
| NFR-014 | Les dossiers du plugin (`process/`, `roles/`, `hooks/`, `scripts/`) et son manifeste ne contiennent ni nom d'un autre projet, ni chemin du poste, ni nom d'hôte ou de machine, ni nom de personne. `docs/`, documentation de jam lui-même, suit NFR-002. | M | RET-014, NFR-002 |
| NFR-015 | Le process et les profils tiennent sous un plafond de taille : au plus la moitié du nombre de mots de `docs/process/`, mesuré sur `main` au départ de la tâche qui l'élague (K1-2). L'historique d'une règle va dans une ADR, pas dans le process. | M | RET-016 |
| NFR-016 | Le kit est gelé une fois le jalon K1 livré : il ne change que sur une friction vécue dans un projet, et toute nouvelle règle dit laquelle elle remplace ou retire. | M | RET-016, ADR 0016 |

Restent valables, plus bas : NFR-001 à NFR-004 et NFR-009 à NFR-012.

## Exigences antérieures (app)

> État au 2026-10-11 (ADR 0016) : **valable** (la méthode l'applique encore, sans app), **abandonnée** (elle portait sur l'app), ou **remplacée** par une exigence du kit. Le texte des exigences n'est pas modifié ; « cœur », « file « À toi » » et « outil » y désignent l'app.

### Pipeline (boucle extérieure) — ADR 0008

| ID | Exigence | Priorité | Étape | Source | État |
|---|---|---|---|---|---|
| FR-020 | Une tâche démarre d'une **issue GitHub**, désignée par son numéro. L'outil crée un worktree et une branche dédiés. | M | E0 | ADR 0008 | Valable : le coordinateur crée le worktree |
| FR-021 | Le cœur déroule le pipeline codé en dur : plan → feu vert 1 → implémentation TDD → relecture → recette → feu vert 2 → PR + CI → feu vert 3 → merge → nettoyage. | M | E0 | ADR 0008 | Remplacée par FR-043 : le même pipeline, tenu par l'orchestrateur de tâche |
| FR-022 | Chaque étape est exécutée par un **rôle** (profil : prompt, outils, permissions), instancié avec un contexte neuf. Une étape peut lancer plusieurs instances du même rôle : la relecture d'un diff qui touche au code applicatif en lance au moins deux, une par axe (justesse, conformité), et davantage si le diff est gros. | M | E0 | ADR 0008, RET-007 | Valable en niveau *standard* ; en *léger*, un seul relecteur (FR-052) |
| FR-023 | L'implémentation boucle jusqu'aux tests verts. La relecture et la correction bouclent jusqu'à ce que tous les relecteurs disent OK, avec des relecteurs neufs à chaque tour. La CI boucle jusqu'au vert. | M | E0 | ADR 0008, RET-006, RET-007 | Valable, précisée par FR-050 |
| FR-024 | Garde-fous : nombre maximal d'itérations d'implémentation, budget par étape, et pour la relecture, détection d'absence de progrès (un seul constat bloquant ou à corriger qui revient, en substance, au tour suivant suffit). Un déclenchement passe la tâche à l'état « bloqué » et l'ajoute à la file « À toi ». | M | E0 | ADR 0008, RET-006 | Valable : « bloqué » est un segment `⛔` de la carte Orca ; précisée par FR-050 |
| FR-025 | Trois **feux verts** humains : plan, recette, merge. Aucun push ni merge sans le feu vert correspondant. | M | E0 | ADR 0008, règle du mainteneur | Valable en niveau *standard* ; en *léger*, pas de feu vert plan (FR-052) |
| FR-026 | Le merge se fait sur GitHub (`gh pr merge`), une fois la CI verte et le feu vert 3 donné. Puis worktree, branche locale et branche distante sont supprimés. | M | E0 | ADR 0008 | Valable : le coordinateur merge et nettoie |
| FR-027 | L'état de chaque tâche (étape, itérations, coût, questions) est persisté par le cœur et survit à un redémarrage. | M | E0 | ADR 0008 | Abandonnée : l'état vit dans la carte Orca et dans `docs/plans/` |
| FR-028 | Configuration minimale par repo : commande de tests, et commande ou skill de recette. | M | E0 | Cohérence | Remplacée par FR-045 |
| FR-029 | Plusieurs tâches avancent en parallèle (cible : 3 à 5, plafond configurable). | M | E0 | Usage | Remplacée par FR-051 |
| FR-030 | Plusieurs repos sont gérés dans la même instance. | S | E0 | Lot 3 | Abandonnée : un coordinateur par projet (ADR 0017) |
| FR-038 | Le cœur injecte à chaque rôle lancé son contexte d'environnement : worktree, tâche (issue), étape en cours et process suivi, c'est-à-dire la liste des étapes du pipeline, la place de l'étape en cours et les feux verts qui suivent. Un rôle n'a pas à le découvrir. | M | E0 (S2) | RET-004 | Remplacée par FR-044 (hook de reprise de contexte) |

### Interface

| ID | Exigence | Priorité | Étape | Source | État |
|---|---|---|---|---|---|
| FR-031 | Tableau des tâches : issue, étape, état, coût, dernière activité. | M | E0 | ADR 0008 | Abandonnée |
| FR-032 | **File « À toi »** : feux verts attendus, questions des agents, tâches bloquées, recettes à faire. | M | E0 | Usage, ADR 0008 | Abandonnée : les cartes `in-review` marquées `⏸` ou `⛔` en tiennent lieu |
| FR-033 | Fil d'activité **résumé** par tâche (événements significatifs, pas chaque battement). | M | E0 | Usage | Abandonnée |
| FR-034 | Discuter avec le lead d'un worktree (reprise de sa session). | S | E0 | Lot 3 bis | Abandonnée : le mainteneur parle à l'orchestrateur de tâche |
| FR-008 | Notification macOS seulement quand une décision attend le mainteneur ou qu'une tâche est bloquée. | M | E0 | Usage | Abandonnée |
| FR-013 | Notification push sur téléphone (ntfy ou Pushover). | C | E3 | Thème 6 | Abandonnée |
| FR-014 | Registre de commandes d'UI typées, partagé par la palette (Cmd+K) et l'agent. | M | E0 | ADR 0007 | Abandonnée |
| FR-015 | Actions d'UI accessibles à l'agent, dans l'ordre de l'ADR 0007. | S | E0.5 | ADR 0007, Q-009 | Abandonnée |
| FR-016 | Champ de conversation accessible partout par un raccourci global (compatible avec la dictée). La conversation est celle du coordinateur, dont la session tourne dans le worktree principal du repo, quel que soit l'écran d'où le mainteneur lui parle. Avec plusieurs repos : voir Q-051. | S | Avec le coordinateur | ADR 0007, RET-008, RET-012 | Abandonnée |
| FR-006 | Vue diff d'un worktree. | C | E3 | Usage : rarement consulté | Abandonnée |
| FR-007 | Éditeur intégré, arbre et recherche de fichiers. | C | E3 | Usage | Abandonnée |
| FR-009 | Navigateur intégré façon Design Mode. | C | E3 | Prompt initial | Abandonnée |

### Mesure (DORA) — ADR 0011

| ID | Exigence | Priorité | Étape | Source | État |
|---|---|---|---|---|---|
| FR-036 | L'état d'une tâche horodate chaque étape et chaque feu vert. | M | E0 (S2) | ADR 0011 | Remplacée par FR-055 |
| FR-037 | Écran « Métriques » par repo : les cinq métriques DORA et les indicateurs agents sur les quatre dernières semaines, selon les définitions de l'ADR 0011. La livraison vaut merge dans `main` par défaut, ou déploiement si le repo désigne un workflow de déploiement, réglage ajouté à la configuration du repo. | S | E0 (S4) | RET-002, ADR 0011 | Remplacée par FR-055 |

### Backends d'agent

| ID | Exigence | Priorité | Étape | Source | État |
|---|---|---|---|---|---|
| FR-012 | Claude Code piloté en headless (`claude -p --output-format stream-json`, reprise par `--resume`). | M | E0 | ADR 0004 | Abandonnée (Q-054) |
| FR-011 | Claude Code et le harness maison passent par une même interface « backend d'agent ». | M | E0 | ADR 0002 | Abandonnée |
| FR-001 | Le harness exécute une boucle d'agent (modèle → outils → modèle) jusqu'à la fin de la tâche. | M | E1 | Prompt initial | Abandonnée |
| FR-002 | Outils minimaux du harness : `read`, `write`, `shell`, `search` (puis `edit`). | M | E1 | Prompt initial | Abandonnée |
| FR-035 | Le harness impose le rôle dans une étape (par ex. un planificateur sans écriture). | S | E2 | ADR 0008 | Abandonnée |

### Coordinateur conversationnel (après E0)

| ID | Exigence | Priorité | Étape | Source | État |
|---|---|---|---|---|---|
| FR-040 | Agent de cadrage : texte libre → specs → issues, arbitrages produit. Le coordinateur orchestre et ne produit aucun livrable : specs, ADR et issues sont rédigés par un rôle rédacteur, relus par un relecteur au contexte neuf, et publiés seulement après le feu vert du mainteneur. | S | Après E0 | ADR 0008, RET-001 | Valable : c'est le cadrage de la méthode |
| FR-041 | Rôles interpellables par leur nom (« @archi ») : un profil avec sa mémoire, instancié à la demande. | C | Après E0 | Discussion sur l'équipe | Abandonnée |

### Hors périmètre

| ID | Exigence | Priorité | Source | État |
|---|---|---|---|---|
| FR-090 | Même tâche confiée à plusieurs agents pour garder la meilleure solution (S2). | W | Usage : jamais observé | Inchangé |
| FR-091 | Merge local comme mode d'acceptation. | W | Usage | Inchangé |
| FR-092 | Agents permanents qui dialoguent entre eux. | W | ADR 0008 | Inchangé |
| FR-093 | Espaces hors code (dossier persistant avec mémoire, session éphémère). | W au MVP | Usage. Le vocabulaire reste générique. | Abandonnée |

### Non fonctionnelles

| ID | Exigence | Priorité | Étape | Source | État |
|---|---|---|---|---|---|
| NFR-001 | Le MVP est réalisable par une personne seule sur son temps libre. | M | — | Prompt initial | Valable, pour le kit |
| NFR-002 | Repo public : aucun secret, aucune donnée personnelle ou de tiers, aucun chemin machine. Licence explicite. | M | E0 | Thème 1 | Valable |
| NFR-003 | Aucune mention d'auteur IA (trailer de commit, signature de PR, docs). | M | — | Thème 1 | Valable |
| NFR-004 | Chaque brique livrée est accompagnée d'une fiche concept. | S | — | ADR 0003 | Valable |
| NFR-005 | macOS uniquement au MVP. Le cœur reste portable. | M | E0 | ADR 0005 | Abandonnée |
| NFR-006 | Le cœur tourne sans UI, dans un processus séparé, derrière un protocole typé. | M | E0 | ADR 0006 | Abandonnée |
| NFR-007 | Exécution locale uniquement au MVP. | M | E0 | Thème 6 | Abandonnée |
| NFR-008 | L'agent ne modifie l'UI que sur demande explicite. | M | E0 | ADR 0007 | Abandonnée |
| NFR-009 | Le mainteneur n'est interrompu que pour une décision : trois feux verts par tâche, plus le feu vert de cadrage, questions, blocages. | M | E0 | Usage | Valable ; deux feux verts au niveau *léger* (FR-052) |
| NFR-011 | Aucun agent en mode sans permission. Chaque rôle a son profil, et tout refus remonte dans la file « À toi ». | M | E0 | ADR 0009 | Valable : un refus remonte par la carte Orca |
| NFR-012 | Aucun agent ne committe, ne pousse ni ne merge : c'est le cœur qui le fait, après un feu vert. | M | E0 | ADR 0009 | Valable, avec les exceptions des ADR 0012 et 0013 : l'orchestrateur de tâche committe, pousse et ouvre la PR, le coordinateur merge ; et, au niveau *léger*, le coordinateur committe, pousse et ouvre la PR (ADR 0016, FR-052) |
| NFR-010 | Chaque boucle automatique a un critère d'arrêt explicite. Les boucles de code (implémentation, CI) bouclent sur des tests ou la CI. La boucle de relecture boucle sur le verdict des relecteurs (`RELECTURE : OK`), bornée par la détection d'absence de progrès et le budget (FR-024). | M | E0 | ADR 0008, ADR 0011, RET-006 | Valable, précisée par FR-050 |
