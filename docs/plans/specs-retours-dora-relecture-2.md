# Relecture, tour 2 — specs-retours-dora (RET-001 à RET-007)

> Relecteur seul, contexte neuf. Objet : les changements de specs non commités du worktree `specs-retours-dora` (11 fichiers modifiés, 7 nouveaux), y compris le brouillon d'issues `docs/plans/specs-retours-dora-issues.md`.
> Grille d'un cadrage : suivi des constats du tour 1, cohérence entre fichiers, fidélité aux retours, repo public, clarté, permissions des profils, petits lots.
> Le brief demandait de vérifier les constats du tour 1 : j'ai donc lu `specs-retours-dora-relecture.md`, ce que le profil du relecteur exclut (voir suggestion S1).

## Synthèse

- **Tour 1** : les neuf constats sont traités. B1 est retiré comme fausse alerte (le process, l. 68-72, décrit maintenant le hook RTK comme une simple réécriture). Seul C4 laisse un reliquat : le glossaire n'a pas suivi le profil du rédacteur (C3 ci-dessous). Les suggestions S1 à S10 et S12 sont appliquées ; S11 est rejetée par le mainteneur et cette décision est notée (issues, l. 5).
- **Numérotation** : FR-036, FR-037, FR-038, ADR 0011 et 0012, RET-001 à RET-007 sont libres, cohérents d'un fichier à l'autre et indexés (`docs/decisions/README.md`). Il ne reste aucune trace des anciens numéros R-001 à R-004 hors de la relecture du tour 1.
- **Repo public** : aucun secret, aucune donnée de tiers, aucun chemin propre à une machine. Le hook de l'ADR 0012 calcule ses dossiers à partir de l'environnement.
- **Commit, push, `gh` en écriture** : aucun profil de rôle du pipeline ou du cadrage ne les ouvre directement. La variante `gh` du relecteur n'utilise que des formes exactes en lecture. Il reste une voie indirecte par les réglages du projet (C7).
- **Nouveaux retours** : RET-005 crée une contradiction (le coordinateur devient un rôle, alors que « aucun rôle ne committe »). RET-006 entre en tension avec la règle « boucles sur critères objectifs ». Sept points à corriger, aucun bloquant.

## Bloquant

Aucun.

## À corriger

### C1 — Le coordinateur est un rôle, mais « aucun rôle ne committe »
- **Fichiers** : `docs/decisions/0012-coordinateur-role-garde-fous-hook.md` l. 15-19 ; `docs/process/README.md` l. 101 ; `AGENTS.md` l. 39 ; `docs/decisions/0009-permissions-par-role.md` l. 14 et 23 ; `docs/specs/01-REQUIREMENTS.md` l. 89 (NFR-012) ; `docs/specs/GLOSSARY.md` l. 13.
- **Constat** : depuis RET-005, le coordinateur est un rôle, et son profil est rangé dans `docs/process/roles/`. Or :
  - le process (l. 101) dit « aucun rôle ne committe, ne pousse ni ne merge, ni ne publie » ;
  - `AGENTS.md` (l. 39) dit « les rôles du pipeline (`docs/process/roles/`) ne committent jamais », et ce dossier contient désormais `coordinateur.md` ;
  - l'ADR 0009, qui est acceptée, dit « aucun rôle ne committe » (l. 23) et exige que tout rôle refuse sans invite ce qui sort de son profil (l. 14). Le coordinateur, lui, tourne en session interactive (`coordinateur.md` l. 12).

  Un agent qui lit ces fichiers reçoit donc deux consignes contraires. L'ADR 0012 « complète » l'ADR 0009, mais elle n'écrit nulle part qu'elle y fait exception.
- **Correction attendue** :
  1. Dans la section Décision de l'ADR 0012, écrire explicitement les deux exceptions à l'ADR 0009 : le coordinateur committe, pousse, publie et merge après le feu vert et avec l'accord du mainteneur ; il tourne en mode interactif, puisque le mainteneur est présent.
  2. Dans le process (l. 101) et dans `AGENTS.md` (l. 39), écrire « aucun rôle du pipeline ni du cadrage (rédacteur, planificateur, implémenteur, relecteur, recetteur) ». Dans `AGENTS.md`, ne plus désigner ces rôles par le seul dossier `docs/process/roles/`.

### C2 — Le hook du coordinateur est décrit comme actif, alors qu'il n'est pas livré
- **Fichiers** : `docs/process/README.md` l. 8 (« un hook refuse ses écritures de fichiers ») et l. 102 (« Son hook refuse ses écritures ») ; `docs/specs/GLOSSARY.md` l. 17 (« avec son profil et son hook »).
- **Constat** : le hook fait l'objet d'un brouillon d'issue. Seul `coordinateur.md` (l. 14) dit qu'en attendant, la règle ne repose que sur le profil. Un mainteneur qui ne lit que le process croira le garde-fou en place, alors qu'il ne l'est pas.
- **Correction attendue** : au process, l. 8 et l. 102, écrire « un hook refusera ses écritures de fichiers (ADR 0012, issue à venir) ; d'ici là, la règle repose sur son profil ». Au glossaire, écrire « avec son profil et, une fois livré, son hook ».

### C3 — Le glossaire limite toujours le rédacteur à `docs/` (reliquat de C4, tour 1)
- **Fichier** : `docs/specs/GLOSSARY.md` l. 14.
- **Constat** : « Il n'écrit que dans `docs/` », alors que son profil (`redacteur.md` l. 5 et 9) et RET-004 (l. 47) l'autorisent aussi à écrire `AGENTS.md` et `README.md`.
- **Correction attendue** : « Il écrit dans `docs/`, `AGENTS.md` et `README.md`, et ne touche jamais au code. »

### C4 — La boucle de relecture n'a pas de critère objectif, contrairement à ce qu'affirme l'ADR 0011
- **Fichiers** : `docs/decisions/0011-pratiques-et-metriques-dora.md` l. 39 ; `docs/specs/RETOURS.md` l. 66 ; `docs/specs/01-REQUIREMENTS.md` l. 16 (FR-023) et l. 90 (NFR-010) ; `docs/decisions/0008-boucle-exterieure-pipeline.md` l. 45.
- **Constat** :
  - l'ADR 0011, écrite dans ce lot, affirme que « les vérifications automatiques (tests, CI) restent les seuls critères des boucles (NFR-010) » ;
  - or FR-023 fait désormais boucler la relecture jusqu'au verdict `RELECTURE : OK` des relecteurs, qui n'est ni un test ni une CI ;
  - RET-006 dit que la boucle « reste bornée, ce qui respecte l'esprit de NFR-010 ». Mais NFR-010 et l'ADR 0008 (l. 45) parlent du critère de la boucle, pas de ses bornes.

  La boucle relecture → implémentation figurait déjà dans le schéma de l'ADR 0008 (l. 35). Ce lot supprime cependant son plafond de deux tours, sans le dire au regard de NFR-010.
- **Correction attendue** :
  1. À l'ADR 0011, l. 39, écrire : « Les boucles d'implémentation et de CI n'ont pour critère que des vérifications automatiques (NFR-010). La boucle de relecture, déjà présente dans l'ADR 0008, a pour critère le verdict des relecteurs, et pour bornes les garde-fous (RET-006). »
  2. Corriger la phrase de RET-006 dans le même sens.
  3. Si le mainteneur juge que cela s'écarte de l'ADR 0008 (l. 45), une nouvelle ADR est nécessaire. Sinon, l'écrire dans l'analyse de RET-006.

### C5 — Deux profils sortent de la table de l'ADR 0009 sans décision tracée
- **Fichiers** : `docs/decisions/0009-permissions-par-role.md` l. 16-21 ; `docs/process/roles/relecteur.md` l. 12-15 ; `docs/process/roles/redacteur.md` l. 5 et 9 ; `docs/decisions/0012-coordinateur-role-garde-fous-hook.md`.
- **Constat** :
  - la table de l'ADR 0009, qui est acceptée, donne au relecteur « Réseau / Git distant : Non ». Sa nouvelle variante ouvre `gh` en lecture, donc le réseau ;
  - le rôle rédacteur (écriture dans `docs/`, `AGENTS.md` et `README.md`, recherche web) n'apparaît dans aucune ADR.

  Une décision actée ne se contourne pas. Ces écarts doivent donc être tracés.
- **Correction attendue** : soit ajouter à l'ADR 0012, qui est encore « proposée » et appartient à ce lot, une ligne pour le rédacteur et une ligne pour la variante du relecteur ; soit retirer la variante du relecteur. Elle servait à la relecture rétroactive de RET-001, qui est déjà faite, et la retirer va dans le sens de « pas de sur-ingénierie ».

### C6 — Le critère de S2-d dépend du bon vouloir du modèle
- **Fichier** : `docs/plans/specs-retours-dora-issues.md` l. 103.
- **Constat** : « le planificateur cite sans qu'on le lui demande l'issue et le worktree ». Ce comportement est spontané, donc variable d'un essai à l'autre. Le critère peut échouer alors que la fonction marche, ou l'inverse.
- **Correction attendue** : remplacer ce critère par un contrôle déterministe, par exemple : « lors de l'essai réel, le brief enregistré pour l'étape contient le numéro et le titre de l'issue et le chemin du worktree ». Le premier critère (le test, l. 102) suffit sinon.

### C7 — L'implémenteur peut modifier les réglages Claude Code du projet, que liront les rôles suivants
- **Fichiers** : `docs/process/roles/implementeur.md` l. 9 ; `docs/process/README.md` l. 104-107.
- **Constat** : `Edit(./**)` permet d'écrire `.claude/settings.json` dans le worktree. Le relecteur et le recetteur, lancés ensuite dans ce même worktree, lisent ces réglages. Une règle « autoriser » ajoutée là (par exemple `Bash(*)`) élargirait alors leurs droits, jusqu'à `git push` ou `gh`, car leurs profils n'ont aucune liste d'interdits. Ce passage d'un rôle à l'autre n'est pas couvert par les limites déjà documentées, qui ne portent que sur le rôle lui-même. Le même dossier accueillera le hook de l'ADR 0012. Je n'ai pas vérifié si Claude Code protège déjà ce dossier ; la correction reste peu coûteuse dans les deux cas.
- **Correction attendue** :
  1. Ajouter `"Edit(.claude/**)"` aux interdits de l'implémenteur.
  2. Dans « Ce qu'Orca ne permet pas », ajouter qu'un rôle qui écrit dans le worktree peut modifier les réglages lus par les rôles suivants, et que seul le sandbox (R-03) ferme aussi la voie `node -e`.

## Suggestions

- **S1 — Le brief contredit le profil du relecteur.** `relecteur.md` l. 30 dit que le relecteur ne lit pas les relectures des tours précédents, et que la comparaison revient au coordinateur. Le brief de ce tour demandait l'inverse. Il faut choisir : garder l'indépendance, qui est plus solide, et ne plus le demander dans les briefs ; ou écrire au profil que, pour un cadrage, le brief peut demander de vérifier les constats du tour précédent.
- **S2 — L'« absence de progrès » est ambiguë.** Process l. 100 (« les constats bloquants ou à corriger d'un tour reviennent »), FR-024 l. 17, RET-006 l. 66. Un seul constat qui revient suffit-il ? Proposition : « au moins un constat bloquant ou à corriger du tour précédent revient tel quel, ou leur nombre ne baisse pas ». C'est utile au coordinateur, qui juge seul aujourd'hui.
- **S3 — RET-007, l. 78** : la remarque dit « deux agents différents ». L'analyse en fait deux instances du même modèle, et renvoie la diversité de modèles à E2. Le seuil est marqué « validé par le mainteneur », mais pas cette lecture. La faire valider de la même façon.
- **S4 — Glossaire.**
  - L. 17 : « Coordinateur : cadrage, issues, arbitrages » se lit comme s'il les produisait. Écrire « orchestre le cadrage et les issues, arbitre ».
  - L. 18 : « Livrable : tout ce qu'une tâche produit » laisse de côté le cadrage, qui n'est pas une tâche. Écrire « ce qu'une tâche ou un cadrage produit ».
  - L. 13 : la définition de « Rôle » change, mais son statut reste « Validé ». La repasser en « Provisoire » jusqu'au feu vert, ou le signaler au mainteneur.
- **S5 — Roadmap.**
  - Le périmètre d'E0 (l. 17-24) et la ligne E0 des étapes (l. 9) ne mentionnent ni la mesure (FR-036, FR-037) ni l'injection du contexte (FR-038), alors que la coupe 1 (l. 30) retire l'écran des métriques. Ajouter une brique « Mesure ».
  - R-03 (l. 59) peut citer l'ADR 0012 dans sa mitigation.
- **S6 — Brouillon d'issues.**
  - (a) La description du milestone S2 (l. 17) omet deux critères de la roadmap (l. 43) : le planificateur lancé avec son profil, et le fil résumé. Celle du S4 (l. 23) omet la réduction à `house` si la coupe 3 s'applique. Aligner sur la roadmap.
  - (b) S2-c (l. 74-91) est la plus grosse issue : lancement headless, lecture et validation du flux, coût, refus, ligne de commande du profil, essai réel et fiche concept. Envisager de la découper en « lancer un rôle et lire le flux » puis « profil de permissions et refus ».
  - (c) Hook (l. 135-137) : ajouter aux tests une écriture dans le dossier de mémoire, qui doit passer, et un chemin qui sort du dossier temporaire par `..` ou par un lien symbolique, qui doit être refusé.
- **S7 — Écritures trop larges.** `Edit(docs/plans/**)` permet au relecteur (`relecteur.md` l. 9) de réécrire le plan ou le brouillon d'issues qu'il relit. `Edit(docs/**)` permet au rédacteur de modifier un fichier de relecture. Restreindre le relecteur à `Edit(docs/plans/*-relecture*.md)`.
- **S8 — Profil du coordinateur.** `coordinateur.md` l. 7 limite son shell à `orca`, `git` et `gh`, mais la commande (l. 12) ne l'impose pas. Préciser que la session est interactive : toute commande hors des réglages demande l'accord du mainteneur, et c'est ce qui tient la limite.
- **S9 — ADR.**
  - ADR 0012, l. 9 : « elle a été enfreinte une première fois » est anachronique, puisque la règle est née de cet épisode (RET-001). Écrire plutôt « c'est cet épisode qui a donné RET-001 ».
  - ADR 0009, l. 3, et l'index : « complétée par 0012 » renvoie à une ADR encore « proposée ». Ne l'écrire qu'au passage de 0012 à « acceptée ».
- **S10 — Planificateur** (antérieur à ce lot) : son profil (`planificateur.md` l. 9) n'a ni `git diff` ni la commande de tests prévus par l'ADR 0009 (l. 18), mais il a `ls`, `WebSearch` et `WebFetch`, ce qui ouvre le réseau. À aligner lors d'un prochain cadrage.
- **S11 — Nommage** : ce cadrage ne suit pas encore la règle `cadrage-<slug>`, ni pour le worktree, ni pour les fichiers, et le fichier du tour 1 n'a pas de numéro de tour. Une ligne en tête du brouillon d'issues suffit à dire que ce cadrage est antérieur à la règle.

RELECTURE : CORRECTIONS (7)
