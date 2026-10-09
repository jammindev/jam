# 01 — Exigences

> Statut : thèmes 1, 2 (cas d'usage) et 6 couverts. Retours du mainteneur intégrés au fil de l'eau ([RETOURS.md](RETOURS.md)). Priorités MoSCoW : **M**ust, **S**hould, **C**ould, **W**on't (pour l'instant).
> Étapes : **E0** boucle extérieure sur Claude Code (≤ 1 mois) · **E1** harness maison en CLI · **E2** harness branché dans l'outil · **E3** confort.

## Exigences fonctionnelles

### Pipeline (boucle extérieure) — ADR 0008

| ID | Exigence | Priorité | Étape | Source |
|---|---|---|---|---|
| FR-020 | Une tâche démarre d'une **issue GitHub**, désignée par son numéro. L'outil crée un worktree et une branche dédiés. | M | E0 | ADR 0008 |
| FR-021 | Le cœur déroule le pipeline codé en dur : plan → feu vert 1 → implémentation TDD → relecture → recette → feu vert 2 → PR + CI → feu vert 3 → merge → nettoyage. | M | E0 | ADR 0008 |
| FR-022 | Chaque étape est exécutée par un **rôle** (profil : prompt, outils, permissions), instancié avec un contexte neuf. Une étape peut lancer plusieurs instances du même rôle : la relecture d'un diff qui touche au code applicatif en lance au moins deux, une par axe (justesse, conformité), et davantage si le diff est gros. | M | E0 | ADR 0008, RET-007 |
| FR-023 | L'implémentation boucle jusqu'aux tests verts. La relecture et la correction bouclent jusqu'à ce que tous les relecteurs disent OK, avec des relecteurs neufs à chaque tour. La CI boucle jusqu'au vert. | M | E0 | ADR 0008, RET-006, RET-007 |
| FR-024 | Garde-fous : nombre maximal d'itérations d'implémentation, budget par étape, et pour la relecture, détection d'absence de progrès (un seul constat bloquant ou à corriger qui revient, en substance, au tour suivant suffit). Un déclenchement passe la tâche à l'état « bloqué » et l'ajoute à la file « À toi ». | M | E0 | ADR 0008, RET-006 |
| FR-025 | Trois **feux verts** humains : plan, recette, merge. Aucun push ni merge sans le feu vert correspondant. | M | E0 | ADR 0008, règle du mainteneur |
| FR-026 | Le merge se fait sur GitHub (`gh pr merge`), une fois la CI verte et le feu vert 3 donné. Puis worktree, branche locale et branche distante sont supprimés. | M | E0 | ADR 0008 |
| FR-027 | L'état de chaque tâche (étape, itérations, coût, questions) est persisté par le cœur et survit à un redémarrage. | M | E0 | ADR 0008 |
| FR-028 | Configuration minimale par repo : commande de tests, et commande ou skill de recette. | M | E0 | Cohérence |
| FR-029 | Plusieurs tâches avancent en parallèle (cible : 3 à 5, plafond configurable). | M | E0 | Usage |
| FR-030 | Plusieurs repos sont gérés dans la même instance. | S | E0 | Lot 3 |
| FR-038 | Le cœur injecte à chaque rôle lancé son contexte d'environnement : worktree, tâche (issue), étape en cours et process suivi, c'est-à-dire la liste des étapes du pipeline, la place de l'étape en cours et les feux verts qui suivent. Un rôle n'a pas à le découvrir. | M | E0 (S2) | RET-004. **M** : un contexte neuf ne sait rien de l'endroit où il tourne, et le deviner coûte des tours et des erreurs. |

### Interface

| ID | Exigence | Priorité | Étape | Source |
|---|---|---|---|---|
| FR-031 | Tableau des tâches : issue, étape, état, coût, dernière activité. | M | E0 | ADR 0008 |
| FR-032 | **File « À toi »** : feux verts attendus, questions des agents, tâches bloquées, recettes à faire. | M | E0 | Usage, ADR 0008 |
| FR-033 | Fil d'activité **résumé** par tâche (événements significatifs, pas chaque battement). | M | E0 | Usage |
| FR-034 | Discuter avec le lead d'un worktree (reprise de sa session). | S | E0 | Lot 3 bis |
| FR-008 | Notification macOS seulement quand une décision attend le mainteneur ou qu'une tâche est bloquée. | M | E0 | Usage |
| FR-013 | Notification push sur téléphone (ntfy ou Pushover). | C | E3 | Thème 6 |
| FR-014 | Registre de commandes d'UI typées, partagé par la palette (Cmd+K) et l'agent. | M | E0 | ADR 0007 |
| FR-015 | Actions d'UI accessibles à l'agent, dans l'ordre de l'ADR 0007. | S | E0.5 | ADR 0007, Q-009 |
| FR-016 | Champ de conversation accessible partout par un raccourci global (compatible avec la dictée). La conversation est celle du coordinateur, dont la session tourne dans le worktree principal du repo, quel que soit l'écran d'où le mainteneur lui parle. Avec plusieurs repos : voir Q-051. | S | Avec le coordinateur | ADR 0007, RET-008, RET-012 |
| FR-006 | Vue diff d'un worktree. | C | E3 | Usage : rarement consulté |
| FR-007 | Éditeur intégré, arbre et recherche de fichiers. | C | E3 | Usage |
| FR-009 | Navigateur intégré façon Design Mode. | C | E3 | Prompt initial |

### Mesure (DORA) — ADR 0011

| ID | Exigence | Priorité | Étape | Source |
|---|---|---|---|---|
| FR-036 | L'état d'une tâche horodate chaque étape et chaque feu vert. | M | E0 (S2) | ADR 0011. **M** : peu coûteux, et une donnée non enregistrée ne se rattrape pas. |
| FR-037 | Écran « Métriques » par repo : les cinq métriques DORA et les indicateurs agents sur les quatre dernières semaines, selon les définitions de l'ADR 0011. La livraison vaut merge dans `main` par défaut, ou déploiement si le repo désigne un workflow de déploiement, réglage ajouté à la configuration du repo. | S | E0 (S4) | RET-002, ADR 0011. **S** : ne conditionne pas le critère de fin d'E0, première coupe si le mois ne suffit pas. |

### Backends d'agent

| ID | Exigence | Priorité | Étape | Source |
|---|---|---|---|---|
| FR-012 | Claude Code piloté en headless (`claude -p --output-format stream-json`, reprise par `--resume`). | M | E0 | ADR 0004 |
| FR-011 | Claude Code et le harness maison passent par une même interface « backend d'agent ». | M | E0 | ADR 0002 |
| FR-001 | Le harness exécute une boucle d'agent (modèle → outils → modèle) jusqu'à la fin de la tâche. | M | E1 | Prompt initial |
| FR-002 | Outils minimaux du harness : `read`, `write`, `shell`, `search` (puis `edit`). | M | E1 | Prompt initial |
| FR-035 | Le harness impose le rôle dans une étape (par ex. un planificateur sans écriture). | S | E2 | ADR 0008 |

### Coordinateur conversationnel (après E0)

| ID | Exigence | Priorité | Étape | Source |
|---|---|---|---|---|
| FR-040 | Agent de cadrage : texte libre → specs → issues, arbitrages produit. Le coordinateur orchestre et ne produit aucun livrable : specs, ADR et issues sont rédigés par un rôle rédacteur, relus par un relecteur au contexte neuf, et publiés seulement après le feu vert du mainteneur. | S | Après E0 | ADR 0008, RET-001 |
| FR-041 | Rôles interpellables par leur nom (« @archi ») : un profil avec sa mémoire, instancié à la demande. | C | Après E0 | Discussion sur l'équipe |

### Hors périmètre

| ID | Exigence | Priorité | Source |
|---|---|---|---|
| FR-090 | Même tâche confiée à plusieurs agents pour garder la meilleure solution (S2). | W | Usage : jamais observé |
| FR-091 | Merge local comme mode d'acceptation. | W | Usage |
| FR-092 | Agents permanents qui dialoguent entre eux. | W | ADR 0008 |
| FR-093 | Espaces hors code (dossier persistant avec mémoire, session éphémère). | W au MVP | Usage. Le vocabulaire reste générique. |

## Exigences non fonctionnelles

| ID | Exigence | Priorité | Étape | Source |
|---|---|---|---|---|
| NFR-001 | Le MVP est réalisable par une personne seule sur son temps libre. | M | — | Prompt initial |
| NFR-002 | Repo public : aucun secret, aucune donnée personnelle ou de tiers, aucun chemin machine. Licence explicite. | M | E0 | Thème 1 |
| NFR-003 | Aucune mention d'auteur IA (trailer de commit, signature de PR, docs). | M | — | Thème 1 |
| NFR-004 | Chaque brique livrée est accompagnée d'une fiche concept. | S | — | ADR 0003 |
| NFR-005 | macOS uniquement au MVP. Le cœur reste portable. | M | E0 | ADR 0005 |
| NFR-006 | Le cœur tourne sans UI, dans un processus séparé, derrière un protocole typé. | M | E0 | ADR 0006 |
| NFR-007 | Exécution locale uniquement au MVP. | M | E0 | Thème 6 |
| NFR-008 | L'agent ne modifie l'UI que sur demande explicite. | M | E0 | ADR 0007 |
| NFR-009 | Le mainteneur n'est interrompu que pour une décision : trois feux verts par tâche, plus le feu vert de cadrage, questions, blocages. | M | E0 | Usage |
| NFR-011 | Aucun agent en mode sans permission. Chaque rôle a son profil, et tout refus remonte dans la file « À toi ». | M | E0 | ADR 0009 |
| NFR-012 | Aucun agent ne committe, ne pousse ni ne merge : c'est le cœur qui le fait, après un feu vert. | M | E0 | ADR 0009 |
| NFR-010 | Chaque boucle automatique a un critère d'arrêt explicite. Les boucles de code (implémentation, CI) bouclent sur des tests ou la CI. La boucle de relecture boucle sur le verdict des relecteurs (`RELECTURE : OK`), bornée par la détection d'absence de progrès et le budget (FR-024). | M | E0 | ADR 0008, ADR 0011, RET-006 |
