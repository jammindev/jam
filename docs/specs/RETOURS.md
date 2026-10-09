# Retours du mainteneur

> Journal des remarques et suggestions faites par le mainteneur pendant la construction. Chaque retour est une entrée de specs (RET-003). Le coordinateur reformule et analyse le retour ; le rédacteur l'inscrit ici et l'applique ; le relecteur relit. Les numéros ne sont jamais réutilisés.
>
> Statuts : **consigné** → **en application** (un rôle rédige) → **appliqué** (relu, feu vert de cadrage donné). Le rédacteur passe un retour à « appliqué » juste après le feu vert, avant le commit du coordinateur.

## RET-001 — Le coordinateur ne produit aucun livrable

- **Date** : 2026-10-08
- **Remarque** : le coordinateur a créé lui-même les milestones GitHub et les issues #1 à #4. Comme ces éléments posent les bases de l'app, ils auraient dû être produits par un autre agent, puis relus.
- **Analyse** : le principe « une méthode imposée plutôt qu'espérée » ne vaut pas que pour le code. Le coordinateur orchestre : il ne produit aucun livrable. Tout livrable, y compris hors code (issues, specs, ADR, docs), suit le même chemin : production par un rôle, relecture indépendante, feu vert.
- **Impact** :
  - process : rôle `rédacteur` créé ([roles/redacteur.md](../process/roles/redacteur.md)) ; le cadrage passe par le rédacteur puis le relecteur ([process](../process/README.md)) ;
  - FR-040 précisé ;
  - glossaire : « Coordinateur », « Rôle », « Rédacteur », « Feu vert » ;
  - rattrapage : les milestones et les issues #1 à #4 ont été relus. Les corrections sont dans `docs/plans/specs-retours-dora-issues.md` et seront publiées par le coordinateur après le feu vert.
- **Statut** : en application.

## RET-002 — Appliquer la méthode DORA

- **Date** : 2026-10-08
- **Remarque** : appliquer la méthode DORA. Trois niveaux validés : (1) les pratiques DORA comme principes dès maintenant ; (2) des métriques DORA par repo dans jam, avec un écran minimal au S4 ; (3) la mesure du développement de jam lui-même, qui en découle.
- **Analyse** : jam est un pipeline de livraison, c'est donc l'endroit naturel pour mesurer la livraison. Les pratiques DORA (petits lots, branches courtes, vérifications automatiques) rejoignent les principes existants. D'après DORA 2025, l'IA amplifie les forces et les faiblesses d'une organisation : c'est la méthode qui fait la différence.
- **Compléments validés par le mainteneur** (2026-10-08), proposés par le rédacteur :
  1. les **indicateurs agents** (itérations, tours de relecture, coût, durée de tâche) s'ajoutent aux cinq métriques, sur le même écran et dans le critère de fin du S4 ;
  2. l'**écran des métriques est la première coupe** d'E0 : les horodatages restent enregistrés (FR-036), l'écran peut venir plus tard sans perte ;
  3. le critère du S4 demande l'écran **pour `house` et pour jam**, puisque jam se mesure lui-même.
- **Impact** : [ADR 0011](../decisions/0011-pratiques-et-metriques-dora.md) ; principe dans `00-VISION.md` ; FR-036 et FR-037 ; jalon S4 dans `04-ROADMAP.md` ; termes dans `GLOSSARY.md`.
- **Statut** : en application.

## RET-003 — Les specs évoluent pendant la construction

- **Date** : 2026-10-08
- **Remarque** : les specs évoluent pendant la construction. Chaque remarque ou suggestion du mainteneur est une entrée de specs : le coordinateur la consigne dans ce journal, l'analyse, puis la fait appliquer par un rôle.
- **Analyse** : un retour oral se perd dans le contexte d'une session. Le consigner le rend traçable, et le faire appliquer par un rôle le soumet à la même relecture que le reste. Selon RET-001, le coordinateur ne produit aucun livrable : il consigne le retour **dans le brief** du rédacteur, et c'est le rédacteur qui l'inscrit dans ce journal.
- **Impact** : ce journal ; process (circuit d'un retour) ; profil du rédacteur.
- **Statut** : en application.

## RET-004 — Un agent doit savoir dans quel environnement il tourne

- **Date** : 2026-10-08
- **Remarque** : une session d'agent ouverte dans un worktree ne savait pas qu'elle tournait dans Orca. Elle ne l'a découvert que lorsque le mainteneur l'a interrogée. N'aurait-elle pas dû le savoir plus tôt ?
- **Analyse** : le contexte d'environnement (outil d'orchestration, une tâche = un worktree, état et passation par la CLI `orca`, process dans `docs/process/README.md`) n'arrive pas automatiquement. `AGENTS.md` n'en parle pas, et la mémoire comme le process ne sont lus qu'à la demande. Un contexte neuf, principe des rôles, part donc sans repères.
- **Impact** :
  - `AGENTS.md` : section « Environnement », courte et générique ;
  - FR-038 : le cœur de jam injecte ce contexte à chaque rôle lancé ;
  - sur le poste du mainteneur, hors du repo : un hook de démarrage de session, installé, donne à chaque agent son contexte (worktree, branche, autres worktrees ; dans Orca, la carte du worktree avec son issue et sa PR, le rôle de la session ou « session libre », les autres agents actifs dans le même worktree, la CLI Orca et le chemin du process). C'est la préfiguration de FR-038 ;
  - profil du rédacteur : écriture permise dans `AGENTS.md` et `README.md`.
- **Statut** : en application.

## RET-005 — Le coordinateur aussi a ses garde-fous en code

- **Date** : 2026-10-08
- **Remarque** : « Tu devrais te mettre un hook aussi. »
- **Analyse** : les garde-fous d'un rôle, coordinateur compris, sont tenus par du code et non par la mémoire de l'agent. Que le coordinateur ne produise aucun livrable (RET-001) ne doit pas dépendre de son obéissance. Le coordinateur devient donc un rôle avec son profil : la variable `JAM_ROLE=coordinateur` l'identifie, et un hook refuse ses écritures hors des emplacements autorisés (voir plus bas). Ce hook est personnel au poste du mainteneur, hors du repo. Il a été installé le 2026-10-09, après deux tours de relecture, et n'agit que si la session est lancée avec la variable (un `export` depuis le shell de l'agent n'atteint pas les hooks). Il autorise la mémoire, le plan de la session, les dossiers temporaires et l'installation d'un hook relu (Q-026). Dans jam, c'est le cœur qui jouera ce rôle.
- **Impact** :
  - [ADR 0012](../decisions/0012-coordinateur-role-garde-fous-hook.md), qui complète l'ADR 0009 et y trace aussi les profils du rédacteur et de la variante du relecteur ;
  - profil [roles/coordinateur.md](../process/roles/coordinateur.md) ;
  - process et `AGENTS.md` : « aucun rôle du pipeline ni du cadrage ne committe » ; section « Ce qu'Orca ne permet pas » revue.
- **Statut** : en application.

## RET-006 — Relire jusqu'à satisfaction

- **Date** : 2026-10-08
- **Remarque** : « Pas qu'une relecture : tant que ce n'est pas satisfaisant, on fait relire. »
- **Analyse** : la relecture et la correction bouclent jusqu'à `RELECTURE : OK`, avec un relecteur neuf à chaque tour. Le plafond de deux allers-retours disparaît. À la place, la boucle s'arrête et remonte au mainteneur en cas d'**absence de progrès** ou de **dépassement de budget**. Un seul constat bloquant ou à corriger qui revient, en substance, au tour suivant suffit à escalader. C'est le coordinateur qui compare les rapports d'un tour à l'autre ; le relecteur, lui, ne lit pas les tours précédents.

  Le critère de cette boucle est le verdict des relecteurs, pas un test ni une CI. Le mainteneur a tranché : la relecture boucle jusqu'au verdict OK. NFR-010 est réécrite en conséquence. La décision de l'ADR 0008 est conservée. L'ADR 0011 (§1) précise que sa règle des critères objectifs vaut pour les boucles de code, et que la boucle de relecture s'arrête sur le verdict des relecteurs. À l'acceptation de l'ADR 0011, le statut de l'ADR 0008 mentionnera cette précision.
- **Impact** : process (relecture, garde-fous) ; FR-023, FR-024, NFR-010 ; profil du relecteur ; glossaire (« Garde-fou », « Tour de relecture ») ; ADR 0011 (critères des boucles, indicateur « tours de relecture »).
- **Statut** : en application.

## RET-007 — Plusieurs relecteurs pour le code

- **Date** : 2026-10-08
- **Remarque** : « Pour les grosses parties de code, on fait relire jusqu'à satisfaction par au minimum deux agents différents qui se partagent les tâches, plus si nécessaire. C'est le début de la loop. »
- **Analyse** : la relecture devient parallèle et découpée par **axe** :
  - **A, justesse** : bugs, tests, cas limites ;
  - **B, conformité** : plan, ADR, lisibilité, sur-ingénierie, sécurité du repo public.

  Chaque axe a son relecteur neuf et son fichier de relecture. Un gros diff justifie plus de relecteurs. La boucle de RET-006 tourne jusqu'à ce que tous les relecteurs disent OK. Seuil validé par le mainteneur : **tout code applicatif**. Les docs et les petites corrections hors code applicatif gardent un seul relecteur, dans la même boucle. Les relecteurs sont des instances Claude neuves ; la diversité de modèles est reportée à E2 (Q-034). Cette lecture de « deux agents différents » a été validée par le mainteneur (« ok pour tout », 2026-10-08).
- **Impact** : profil du relecteur ; process ; FR-022, FR-023 ; glossaire (« Axe de relecture »). L'ADR 0008 n'est pas modifiée : plusieurs instances du rôle relecteur restent une étape « relecture » au contexte neuf.
- **Statut** : en application.

## RET-011 — Consulter Orca avant de concevoir une brique qu'il possède

- **Date** : 2026-10-09
- **Remarque** : « Dans le plan général de la construction de l'appli, il est précisé de bien s'inspirer du code de Orca pour construire l'app ? »
- **Analyse** : les specs le permettent sans le demander. L'ADR 0001 fait d'Orca une référence de lecture, l'ADR 0005 compte la reprise de ses briques parmi les raisons de choisir Electron, et la règle 9 d'`AGENTS.md` encadre la licence. Mais aucun profil ne demande de regarder Orca, aucun clone n'est fourni, et rien n'a été repris jusqu'ici.

  Orca a déjà résolu en conditions réelles une bonne part de ce que jam construit : worktrees, git, processus Electron, SQLite, diff, notifications. Sans consigne, un agent réinvente et retombe dans des pièges déjà corrigés. À l'inverse, trois risques : grossir jam (on part du minimum et on n'élague pas Orca, ADR 0001), reprendre ses parties fragiles (ADR 0002 et 0004), et dépenser du quota dans une exploration sans but. D'où la règle, validée par le mainteneur (« ok go ») :
  1. **regard ciblé, pas systématique** : le planificateur consulte Orca seulement quand la tâche touche une brique qu'Orca possède. Il part de `docs/references/orca.md` comme carte et lit quelques fichiers, pas tout le code ;
  2. **une section « Orca » dans le plan**, de quelques lignes : repris, inspiré, écarté, et pourquoi. Le mainteneur la voit au feu vert plan. Si la tâche ne touche aucune brique d'Orca, une ligne le dit ;
  3. **s'inspirer par défaut, copier par exception** : seulement un petit morceau autonome, avec la mention de licence (règle 9). Sinon, on réécrit à la taille de jam ;
  4. **liste noire** : terminal interactif (PTY) et détection de l'état d'une TUI (ADR 0002, 0004) ;
  5. **un clone d'Orca en lecture seule, à une version fixée**, fourni au planificateur par l'orchestrateur de tâche dans un dossier temporaire, hors du repo. La commande du planificateur l'ouvre en lecture (`--add-dir`).

  La règle précise la façon d'appliquer l'ADR 0001 sans rien en changer. Pour le planificateur, l'ADR 0009 n'est pas touchée non plus : il reste en lecture seule.
- **Compléments validés par le mainteneur** (« ok pour tout », 2026-10-09), proposés par le rédacteur et le relecteur :
  1. **l'implémenteur lit aussi le clone, quand le plan prévoit une reprise**, sans rien écrire hors du worktree. Sans cela, il ne pourrait copier ni le morceau repris ni le texte de la licence, et le point 3 n'aurait pas de voie d'application. C'est au-delà de la lettre de l'ADR 0009 (« lecture et écriture dans le worktree ») : la précision est tracée dans l'[ADR 0014](../decisions/0014-lecture-clone-orca-implementeur.md) ;
  2. **la carte couvre les briques relevées**, pas tout E0 : le cadrage de chaque jalon la complète pour les siennes avant sa première tâche.
- **Portée** : les tâches du repo jam seulement. Orca n'est une référence que pour ce repo : le même rôle planificateur, lancé sur une autre cible comme `house`, n'a ni section « Orca » ni clone. Ne s'applique pas à l'issue #7, dont le plan est déjà validé. S'applique dès la tâche suivante.
- **Impact** :
  - [ADR 0014](../decisions/0014-lecture-clone-orca-implementeur.md), qui précise l'ADR 0009 ;
  - profil du [planificateur](../process/roles/planificateur.md) : lecture du clone, section « Orca » du plan ;
  - profils de l'[implémenteur](../process/roles/implementeur.md) (reprise, licence, accès au clone) et du [relecteur](../process/roles/relecteur.md) (axe conformité) ;
  - profil du [rédacteur](../process/roles/redacteur.md) : compléter la carte au cadrage d'un jalon (complément 2) ;
  - [`docs/references/orca.md`](../references/orca.md) : rôle de carte, version de référence, procédure du clone, liste noire ;
  - `AGENTS.md`, règle 9 ; glossaire (« Clone de référence ») ; Q-040, Q-042, Q-043.
- **Statut** : appliqué (feu vert de cadrage du 2026-10-09).
