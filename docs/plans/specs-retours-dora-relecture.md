# Relecture — specs-retours-dora (R-001 à R-004)

> Relecteur, contexte neuf. Objet : les changements de specs non commités du worktree `specs-retours-dora`, puis la relecture rétroactive des milestones et des issues #1 à #4 de `jammindev/jam` demandée par R-001.
> Grille adaptée à un cadrage : cohérence (ADR, FR, glossaire, roadmap, process), fidélité aux retours, exactitude DORA, repo public, clarté, permissions des rôles.

## Synthèse

- **DORA** : les cinq métriques, leurs définitions, leurs deux groupes et leurs dates (MTTR renommé en 2023, taux de reprise ajouté en 2024) sont **conformes** à [dora.dev/guides/dora-metrics](https://dora.dev/guides/dora-metrics/) et à [l'historique des métriques](https://dora.dev/insights/dora-metrics-history/). Les sept capacités du modèle IA 2025 sont exactes. Les définitions adaptées sont des adaptations raisonnables, et l'écart sur le délai de changement est expliqué dans l'ADR.
- **Repo public** : aucun secret, aucune donnée de tiers, aucun chemin propre à une machine dans les fichiers relus.
- **Numérotation** : FR-036, FR-037, FR-038, ADR 0011 et R-001 à R-004 sont libres et cohérents d'un fichier à l'autre.
- Restent un point bloquant sur les permissions et huit points à corriger, surtout des incohérences entre fichiers et des issues qui ne respectent pas encore les petits lots.

## Bloquant

### B1 — Le hook RTK semble contourner les listes blanches des rôles
- **Fichier** : `docs/process/README.md`, l. 64 ; tous les profils de `docs/process/roles/` ; ADR 0009, l. 14.
- **Constat** : pendant cette relecture, lancée en mode `dontAsk`, des commandes **absentes** de la liste blanche du relecteur se sont exécutées sans invite : `cat`, `ls`, `gh issue view`, `gh api …/milestones`. À l'inverse, les commandes que RTK ne réécrit pas (`rtk proxy git diff`, `ps`, un pipe vers `rtk hook`) ont été refusées. L'hypothèse la plus probable : quand le hook réécrit une commande, il renvoie aussi une décision « autoriser », qui passe avant les listes blanches. Je n'ai pas pu le prouver, faute de pouvoir lancer le hook. Je n'ai pas non plus vu la commande exacte qui m'a lancé.
- **Conséquence si c'est confirmé** : les profils d'ADR 0009 ne protègent plus rien pour les commandes que RTK réécrit. Un rôle en `dontAsk` pourrait alors lancer `gh pr create`, `gh issue create` ou `gh api -X POST`, et aucun garde-fou local ne couvre `gh`. La phrase l. 64 (« le refus remonte comme tout refus de permission ») décrit l'inverse de ce qui a été observé.
- **Correction attendue** :
  1. Le coordinateur vérifie, avant le feu vert : il lance un rôle avec son profil, lui fait exécuter une commande en lecture qui n'est pas dans sa liste (par exemple `gh issue list`), et regarde si elle passe.
  2. Si c'est confirmé, les rôles sont lancés **sans le hook RTK** (réglages dédiés aux sessions de rôle), et le paragraphe l. 62-64 est réécrit en conséquence. Les formes `rtk …` des listes deviennent alors inutiles.
  3. Le constat est noté dans `OPEN-QUESTIONS.md` et rattaché à ADR 0009 (risque R-03 de la roadmap).

## À corriger

### C1 — « Trois feux verts » contre « feu vert cadrage »
- **Fichiers** : `docs/process/README.md` l. 26 et 71 (nouveau feu vert « cadrage ») ; `docs/specs/GLOSSARY.md` l. 20 (« Il y en a trois ») ; `FR-025`, `NFR-009` ; `AGENTS.md` l. 7 ; `00-VISION.md` l. 7 ; `README.md` l. 5.
- **Constat** : le process ajoute un quatrième feu vert, alors que le glossaire, les exigences et la vision en annoncent trois. Un agent qui lit le glossaire ne connaît pas le feu vert cadrage.
- **Correction attendue** : préciser dans le glossaire (« Feu vert ») qu'il y en a trois **dans le pipeline d'une tâche** (plan, recette, merge), et un **feu vert de cadrage en amont**, sur les specs, les ADR et les issues (FR-040). Les autres mentions de « trois feux verts » restent justes si elles parlent de la tâche.

### C2 — Qui écrit dans `RETOURS.md` ?
- **Fichiers** : `docs/specs/RETOURS.md` l. 3 et l. 30 (R-003) ; `docs/process/README.md` l. 23.
- **Constat** : l'en-tête et R-003 disent que **le coordinateur consigne** le retour dans le journal. Le process dit que **le rédacteur l'inscrit**. Selon R-001, le coordinateur ne produit aucun livrable, donc c'est le process qui a raison.
- **Correction attendue** : dans l'en-tête de `RETOURS.md`, écrire « le coordinateur reformule et analyse le retour ; le rédacteur l'inscrit ici et l'applique ; le relecteur relit ». Dans R-003, garder la remarque mot pour mot, mais préciser dans l'analyse que l'inscription revient au rédacteur (R-001).

### C3 — FR-038 est prévue au S2, mais la roadmap ne la mentionne pas
- **Fichiers** : `docs/specs/01-REQUIREMENTS.md` l. 15 (FR-038, « E0 (S2) ») ; `docs/specs/04-ROADMAP.md` l. 43.
- **Constat** : la ligne S2 cite FR-036, mais pas FR-038. Son critère de fin ne vérifie ni l'une ni l'autre.
- **Correction attendue** : ajouter au périmètre S2 « injection du contexte d'environnement au rôle (FR-038) », et au critère de fin quelque chose de vérifiable, par exemple : « le brief reçu par le planificateur contient le worktree, l'issue, l'étape et le process ; l'état enregistre l'heure de début et de fin de l'étape ».

### C4 — Le profil du rédacteur ne permet pas d'écrire `AGENTS.md`
- **Fichiers** : `docs/process/roles/redacteur.md` l. 5 et 9 ; `docs/specs/RETOURS.md` l. 41 (R-004 : impact sur `AGENTS.md`).
- **Constat** : avec `Edit(docs/**)`, le rédacteur ne peut pas modifier `AGENTS.md`, `README.md` ni `THIRD_PARTY_NOTICES.md`, qui sont à la racine. R-004 exige pourtant une modification d'`AGENTS.md`, qui figure dans ce lot. Avec ce profil, ce n'est pas le rédacteur qui a pu la faire.
- **Correction attendue** : ajouter `"Edit(AGENTS.md)"` et `"Edit(README.md)"` au profil, et remplacer « Écriture dans `docs/` seulement » par « Écriture dans `docs/`, `AGENTS.md` et `README.md` ». Le coordinateur indique au mainteneur qui a écrit la modification d'`AGENTS.md` de ce lot. Si c'est lui, c'est un écart à R-001 et il faut le signaler.

### C5 — Des ajouts au-delà de R-002 qui ne sont pas tracés
- **Fichiers** : `docs/decisions/0011-pratiques-et-metriques-dora.md` §3 ; `FR-037` ; `04-ROADMAP.md` l. 30 et l. 45.
- **Constat** : R-002 valide trois niveaux : les pratiques, les métriques DORA par repo avec un écran au S4, et la mesure de jam. Trois éléments n'en découlent pas directement : (a) les **indicateurs agents** (itérations, allers-retours, coût, durée de tâche), ajoutés à l'écran et au critère de fin du S4 ; (b) l'**écran des métriques placé en première coupe** ; (c) l'écran demandé **aussi pour jam** au critère du S4. Ce sont des choix raisonnables, mais le mainteneur ne les a pas demandés, et rien ne montre qu'il les a validés.
- **Correction attendue** : présenter ces trois points au mainteneur comme des « points tranchés ». S'il les valide, les inscrire dans la remarque ou l'analyse de R-002. Sinon, sortir les indicateurs agents du critère du S4 et les noter dans `OPEN-QUESTIONS.md`.

### C6 — Implémenteur : les interdits ne ferment pas commit ni push, et le profil contredit ADR 0009
- **Fichiers** : `docs/process/roles/implementeur.md` l. 5 et 9 ; `docs/process/README.md` l. 36 ; ADR 0009 l. 14.
- **Constat** :
  - `Bash(node *)`, `Bash(npx *)` et `Bash(pnpm *)` permettent d'exécuter n'importe quoi (`node -e …`, `pnpm exec git push`). Quant à `git -C <chemin> commit`, il échappe à l'interdit `git commit:*`. « Ni commit, ni push » n'est donc pas garanti par la liste.
  - Le mode `acceptEdits` **demande** une autorisation pour toute commande hors liste, alors qu'ADR 0009 prévoit qu'elle soit « refusée automatiquement, sans invite ».
- **Correction attendue** : ne pas élargir le jalon, mais documenter la limite dans « Ce qu'Orca ne permet pas » (le profil réduit le risque, il ne le supprime pas, et seul le sandbox viendra le fermer, cf. R-03). Ajouter les interdits `git -C` sous leurs deux formes, puis soit passer l'implémenteur en `dontAsk`, soit noter l'écart à ADR 0009 dans `OPEN-QUESTIONS.md`.

### C7 — Issues #2, #3 et #4 : un jalon entier par issue
- **Issues** : #2, #3, #4 (« À découper en plusieurs issues par le planificateur si nécessaire »).
- **Constat** : chacune couvre une semaine de travail. Cela contredit ADR 0011 §1, où une tâche est une petite issue mergée en quelques jours et le redécoupage se fait **au cadrage**. De plus, le planificateur n'a ni `gh` ni le droit de créer des issues : la consigne ne peut pas s'appliquer.
- **Correction attendue** : au début de chaque jalon, le rédacteur découpe le jalon en petits brouillons d'issues (`docs/plans/<cadrage>-issues.md`), qui passent en relecture puis au feu vert de cadrage. Les milestones servent de regroupement. Les issues #2 à #4 sont alors fermées et remplacées, ou réduites à leur première tranche. #1 peut rester telle quelle, car son plan est déjà validé et en cours (exception à noter).

### C8 — Milestones et issues pas à jour avec ce lot
- **Issues et milestones** : #2 et milestone « E0-S2 » (FR-036, FR-038 absentes) ; #4 et milestone « E0-S4 Merge et parallélisme » (métriques FR-037 absentes, et le titre omet le nettoyage).
- **Constat** : R-001 prévoit que les corrections soient publiées après le feu vert, mais ce lot ne contient **aucun brouillon d'issue**. Le coordinateur n'aurait donc rien de relu à publier.
- **Correction attendue** : le rédacteur écrit `docs/plans/specs-retours-dora-issues.md`, avec les nouveaux titres et descriptions des milestones S2 et S4, et le contenu corrigé (ou de remplacement, voir C7) des issues concernées, en tenant compte de C3 et C5.

## Suggestions

- **S1** — `04-ROADMAP.md` l. 57-60 : les risques sont numérotés R-01 à R-04, et les retours R-001 à R-004. Le lecteur les confondra. Renommer les risques (par exemple `RQ-01`) ou les retours (`RET-001`).
- **S2** — ADR 0011 est « Proposée », mais la vision, les exigences et la roadmap s'en servent déjà comme source, et le glossaire marque « DORA » comme « Validé ». Prévoir que le rédacteur passe l'ADR à « Acceptée » dans le même lot que le feu vert (pas le coordinateur), et marquer « DORA » comme « Provisoire » d'ici là.
- **S3** — `redacteur.md` l. 11 : l'affirmation « `Write(...)` n'est pas reconnu dans `--allowedTools` » n'est pas démontrée. Mieux vaut écrire le fait utile : « `Edit(...)` couvre aussi la création de fichiers ».
- **S4** — `04-ROADMAP.md` l. 3 : « Le découpage en jalons hebdomadaires sera fait en fin d'entretien » est périmé, puisque les jalons existent.
- **S5** — `docs/process/README.md` : un cadrage n'a pas d'issue, donc `<tâche>` n'est pas défini pour `docs/plans/<tâche>-issues.md` ni pour le nom du worktree. Ce worktree (`specs-retours-dora`) ne suit d'ailleurs pas `<numéro>-<slug>`. Proposer `cadrage-<slug>`.
- **S6** — Clarté pour le mainteneur : dire en une phrase ce qu'est RTK (un outil qui compacte la sortie des commandes shell) dans `docs/process/README.md` l. 62, et développer « MTTR » (temps moyen de rétablissement) dans ADR 0011.
- **S7** — Le critère du S4 demande les métriques pour `house` **et** jam, alors que la coupe 3 réduit à un seul repo et que FR-037 est en **S**. Préciser que la seconde phrase du critère tombe si la coupe 1 ou 3 s'applique.
- **S8** — Issue #1 : elle renvoie à `docs/plans/E0-S1-squelette.md`, qui n'existe pas encore sur `main`. Le lien est donc mort sur GitHub jusqu'au merge. Committer le plan avec le S1, ou écrire « dans le worktree de la tâche ».
- **S9** — Issue #2 : le critère « Je choisis l'issue n » ne dit pas qui est « je ». Écrire « le mainteneur ». Ajouter aussi un critère qui vérifie le profil de permissions du planificateur (ADR 0009) et le fil résumé (FR-033), cités au périmètre mais jamais vérifiés.
- **S10** — Issue #3 et ligne S3 de la roadmap : « notifications filtrées » est au périmètre sans critère de fin. Exemple de critère : « seuls les passages en file À toi déclenchent une notification ».
- **S11** — Milestones : aucune date d'échéance. En mettre une par semaine rendrait visible la limite « E0 ≤ 1 mois » (ADR 0002).
- **S12** — Profil du relecteur : la relecture rétroactive d'issues publiées demande `gh` en lecture. Si ce cas doit revenir, ajouter des formes exactes sous les deux écritures (`gh issue view:*`, `gh issue list:*`, et `gh api repos/jammindev/jam/milestones` sans joker, pour ne pas ouvrir `gh api -X POST`), après correction de B1.

RELECTURE : CORRECTIONS (9)
