# Brouillons d'issues — cadrage `specs-retours-dora`

> Rédigés par le rédacteur. Le coordinateur les publie sur `jammindev/jam` après le feu vert de cadrage (RET-001).
> Ce cadrage est antérieur à la règle de nommage `cadrage-<slug>` et aux fichiers de relecture numérotés par tour : son worktree et ses fichiers gardent leur nom.
> Une issue = un petit lot ([ADR 0011](../decisions/0011-pratiques-et-metriques-dora.md)). Seul le **S2** est découpé ici : le S3 et le S4 le seront au début de leur jalon, par un cadrage `cadrage-s3`, puis `cadrage-s4`.
> Aucune date d'échéance sur les milestones (décision du mainteneur).

## 1. Milestones

| Milestone | Titre | Description |
|---|---|---|
| S1 | `E0-S1 Squelette` (inchangé) | Inchangée. |
| S2 | `E0-S2 Issue → worktree → un rôle` (inchangé) | Voir ci-dessous. |
| S3 | `E0-S3 Pipeline jusqu'à la PR` (inchangé) | Voir ci-dessous. |
| S4 | `E0-S4 Merge, nettoyage, parallélisme, métriques` (renommé, ancien titre : `E0-S4 Merge et parallélisme`) | Voir ci-dessous. |

**E0-S2** :
> Lecture des issues via `gh`, création du worktree et de sa branche, exécution du planificateur en headless avec son profil (ADR 0009), injection du contexte d'environnement au rôle (FR-038), état SQLite horodaté (FR-036), fil résumé. Fini quand : le mainteneur choisit l'issue n de `house`, le worktree est créé et le plan s'affiche ; le planificateur est lancé avec son profil de permissions ; le brief qu'il reçoit contient le worktree, l'issue, l'étape et le process ; l'état enregistre le début et la fin de l'étape ; le fil résumé montre les événements significatifs de l'étape ; après redémarrage de l'app, l'état est conservé.

**E0-S3** :
> Enchaînement des rôles, boucle tests, boucle de relecture jusqu'à OK (pour le code, au moins deux relecteurs neufs, un par axe), garde-fous (itérations, budget, absence de progrès en relecture), trois feux verts, file « À toi », notifications filtrées. Fini quand : une vraie issue de `house` arrive jusqu'à une PR avec la CI verte, le mainteneur n'intervient que via la file, et seuls les passages dans la file déclenchent une notification. Découpé en petites issues au début du jalon.

**E0-S4** :
> Feu vert 3 → `gh pr merge`, suppression du worktree et des branches, trois tâches en parallèle, écran minimal des métriques DORA et désignation du workflow de déploiement par repo (FR-037, ADR 0011). Fini quand : trois issues de `house` traversent le pipeline en parallèle jusqu'au merge (critère de fin d'E0) ; l'écran « Métriques » affiche, pour `house`, les cinq métriques DORA et les indicateurs agents, et pour jam, les cinq métriques ; les indicateurs agents de jam peuvent rester vides tant que ses tâches passent par Orca (ADR 0011 §5). Ce second critère tombe si l'écran est coupé, et se limite à `house` si le multi-repo est coupé. Découpé en petites issues au début du jalon.

## 2. Sort des issues existantes

| Issue | Proposition | Commentaire à poster |
|---|---|---|
| #1 Squelette | **Aucune action** : livrée par la PR #5 et déjà fermée par elle. Elle n'a pas été redécoupée, par exception aux petits lots, car son plan était validé et en cours avant ce cadrage. Son lien vers `docs/plans/E0-S1-squelette.md` fonctionne, le plan étant dans `main`. | Aucun. |
| #2 Issue → worktree → un rôle | **Fermée**, remplacée par les six issues S2 ci-dessous. | « Remplacée par #a à #f : le jalon est découpé en petits lots (ADR 0011). » (#a à #f : numéros réels des issues S2-a à S2-f, à substituer à la publication) |
| #3 Pipeline jusqu'à la PR | **Fermée.** Le périmètre et le critère de fin restent dans la description du milestone, jusqu'au découpage au début du S3. | « Le S3 sera découpé en petites issues au début du jalon (ADR 0011). Le périmètre est dans la description du milestone. » |
| #4 Merge, nettoyage et parallélisme | **Fermée**, même raison. | Idem, pour le S4. |

Pourquoi fermer #3 et #4 plutôt que les garder ouvertes : une issue ouverte d'une semaine de travail peut être prise pour une tâche, à l'encontre des petits lots. Le milestone suffit à garder le périmètre visible.

## 3. Issues du S2

Ordre : S2-a → S2-b → S2-c → S2-d → S2-e → S2-f, chacune lancée après le merge de la précédente. S2-c démarre après le merge de S2-b : une étape appartient à une tâche, et S2-b comme S2-c ajoutent une migration à la même liste (ADR 0010), ce qui créerait un conflit en parallèle.

### S2-a — Lister les issues d'un repo via `gh`

- **Milestone** : E0-S2 · **Labels** : `enhancement`
- **Exigences** : FR-020

**Périmètre**
- Le cœur lit les issues ouvertes d'un repo configuré avec `gh`, et valide la réponse avec zod.
- Une méthode du protocole expose cette liste.
- Une commande de palette « Choisir une issue » l'affiche (numéro, titre).

**Critère de fin**
- Sur `house`, Cmd+K → « Choisir une issue » liste les issues ouvertes.
- Les tests simulent la sortie de `gh`, y compris une liste vide, et `gh` absent ou non authentifié (message d'erreur lisible).

**Hors périmètre** : création du worktree.

### S2-b — Créer la tâche : worktree et branche d'une issue

- **Milestone** : E0-S2 · **Labels** : `enhancement`
- **Exigences** : FR-020, FR-027, FR-036

**Périmètre**
- Choisir une issue crée une **tâche** : un worktree et sa branche, nommés `<numéro>-<slug>`.
- La tâche est enregistrée dans SQLite avec son heure de création. La table des tâches arrive par une nouvelle migration numérotée, dans la base posée au S1 (ADR 0010).
- Une deuxième tâche sur la même issue est refusée.

**Critère de fin**
- Le mainteneur choisit l'issue n de `house` : le worktree `<n>-<slug>` existe, sur sa branche.
- Après redémarrage de l'app, la tâche est toujours listée.
- Les tests couvrent l'issue déjà prise et un titre avec accents ou caractères spéciaux.
- Fiche concept : worktree.

**Hors périmètre** : lancement d'un rôle.

### S2-c — Backend Claude Code : lancer un rôle en headless et lire le `stream-json`

- **Milestone** : E0-S2 · **Labels** : `enhancement`
- **Exigences** : FR-012, FR-036 ; ADR 0004

**Périmètre**
- Le cœur lance Claude Code en headless (`stream-json`) dans un worktree.
- Les événements sont lus et validés en un seul endroit (le backend Claude Code).
- L'état enregistre l'identifiant de session, le coût, et l'heure de début et de fin de l'étape.

**Critère de fin**
- Un test rejoue un flux enregistré : les événements sont normalisés, le coût et les heures de début et de fin sont relevés.
- Un essai réel lance un rôle sur `house`, en `dontAsk` avec les seuls outils de lecture (`Read`, `Grep`, `Glob`), jamais sans permission (ADR 0009), et l'étape se termine.
- Fiche concept : stream-json.

**Hors périmètre** : profil de permissions (S2-d), enchaînement de plusieurs étapes (S3).

### S2-d — Profil de permissions du rôle et refus

- **Milestone** : E0-S2 · **Labels** : `enhancement`
- **Exigences** : FR-022, NFR-011 ; ADR 0009 ; Q-012

**Périmètre**
- Le backend construit la ligne de commande d'un rôle à partir de son profil de rôle, dont l'emplacement et le format sont tranchés dans le plan (Q-012). Les profils de `docs/process/roles/` servent au déroulé dans Orca et ne sont pas lus tels quels : ils n'existent pas dans les autres repos et contiennent les formes `rtk` propres au poste.
- Les refus de permission du flux sont repérés et enregistrés.

**Critère de fin**
- Un test vérifie que la ligne de commande construite pour le planificateur contient exactement les options de son profil.
- Un test vérifie que la ligne de commande ne contient jamais `bypassPermissions` (NFR-011).
- Un test rejoue un flux qui contient un refus : le refus est enregistré avec la commande demandée.

**Hors périmètre** : passage à « bloqué » et file « À toi » sur refus (S3).

### S2-e — Injecter le contexte d'environnement au rôle

- **Milestone** : E0-S2 · **Labels** : `enhancement`
- **Exigences** : FR-038 ; RET-004

**Périmètre**
- Le brief d'un rôle contient, en plus de sa consigne : le worktree, l'issue (numéro, titre, corps), l'étape en cours et le process suivi, c'est-à-dire la liste des étapes du pipeline, la place de l'étape en cours et les feux verts qui suivent.
- Le brief envoyé est enregistré avec l'étape.

**Critère de fin**
- Un test vérifie que le brief du planificateur contient : le chemin du worktree, le numéro, le titre et le corps de l'issue, le nom de l'étape, la liste des étapes du pipeline avec l'étape en cours repérée, et les feux verts qui suivent.
- Lors de l'essai réel, le brief enregistré pour l'étape contient le numéro et le titre de l'issue et le chemin du worktree.

**Hors périmètre** : briefs des autres rôles (S3).

### S2-f — Étape plan de bout en bout et fil résumé

- **Milestone** : E0-S2 · **Labels** : `enhancement`
- **Exigences** : FR-027, FR-033

**Périmètre**
- Choisir une issue enchaîne : création de la tâche, lancement du planificateur, affichage du plan produit.
- Le fil résumé de la tâche montre les événements significatifs de l'étape (début, fin, coût, refus), pas chaque message.

**Critère de fin**
- Le mainteneur choisit l'issue n de `house` : le worktree est créé et le plan s'affiche.
- Le planificateur est lancé avec la ligne de commande construite depuis son profil (S2-d), visible dans l'état de l'étape.
- Le fil résumé montre le début et la fin de l'étape, son coût et ses éventuels refus.
- Après redémarrage de l'app, la tâche, son étape et son plan sont conservés.

**Hors périmètre** : feu vert 1 et étapes suivantes (S3).

## 4. Hors du repo

La garde du coordinateur (RET-005, [ADR 0012](../decisions/0012-coordinateur-role-garde-fous-hook.md)) est un hook personnel du poste du mainteneur, hors du repo. Elle ne donne donc lieu à aucune issue sur `jammindev/jam`.
