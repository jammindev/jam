# Retours du mainteneur

> Journal des remarques et suggestions faites par le mainteneur pendant la construction. Chaque retour est une entrée de specs (RET-003). Le coordinateur, ou l'orchestrateur de tâche qui l'a reçu, reformule et analyse le retour ; le rédacteur l'inscrit ici et l'applique ; le relecteur relit. Les numéros ne sont jamais réutilisés.
>
> Statuts : **consigné** → **en application** (un rôle rédige) → **appliqué** (relu, feu vert de cadrage donné). Le rédacteur passe un retour à « appliqué » juste après le feu vert, avant le commit de l'orchestrateur de tâche.

## RET-001 — Le coordinateur ne produit aucun livrable

- **Date** : 2026-10-08
- **Remarque** : le coordinateur a créé lui-même les milestones GitHub et les issues #1 à #4. Comme ces éléments posent les bases de l'app, ils auraient dû être produits par un autre agent, puis relus.
- **Analyse** : le principe « une méthode imposée plutôt qu'espérée » ne vaut pas que pour le code. Le coordinateur orchestre : il ne produit aucun livrable. Tout livrable, y compris hors code (issues, specs, ADR, docs), suit le même chemin : production par un rôle, relecture indépendante, feu vert.
- **Impact** :
  - process : rôle `rédacteur` créé ([roles/redacteur.md](../process/roles/redacteur.md)) ; le cadrage passe par le rédacteur puis le relecteur ([process](../process/README.md)) ;
  - FR-040 précisé ;
  - glossaire : « Coordinateur », « Rôle », « Rédacteur », « Feu vert » ;
  - rattrapage : les milestones et les issues #1 à #4 ont été relus. Les corrections sont dans `docs/plans/specs-retours-dora-issues.md` et seront publiées par le coordinateur après le feu vert.
- **Statut** : appliqué.

## RET-002 — Appliquer la méthode DORA

- **Date** : 2026-10-08
- **Remarque** : appliquer la méthode DORA. Trois niveaux validés : (1) les pratiques DORA comme principes dès maintenant ; (2) des métriques DORA par repo dans jam, avec un écran minimal au S4 ; (3) la mesure du développement de jam lui-même, qui en découle.
- **Analyse** : jam est un pipeline de livraison, c'est donc l'endroit naturel pour mesurer la livraison. Les pratiques DORA (petits lots, branches courtes, vérifications automatiques) rejoignent les principes existants. D'après DORA 2025, l'IA amplifie les forces et les faiblesses d'une organisation : c'est la méthode qui fait la différence.
- **Compléments validés par le mainteneur** (2026-10-08), proposés par le rédacteur :
  1. les **indicateurs agents** (itérations, tours de relecture, coût, durée de tâche) s'ajoutent aux cinq métriques, sur le même écran et dans le critère de fin du S4 ;
  2. l'**écran des métriques est la première coupe** d'E0 : les horodatages restent enregistrés (FR-036), l'écran peut venir plus tard sans perte ;
  3. le critère du S4 demande l'écran **pour `house` et pour jam**, puisque jam se mesure lui-même.
- **Impact** : [ADR 0011](../decisions/0011-pratiques-et-metriques-dora.md) ; principe dans `00-VISION.md` ; FR-036 et FR-037 ; jalon S4 dans `04-ROADMAP.md` ; termes dans `GLOSSARY.md`.
- **Statut** : appliqué.

## RET-003 — Les specs évoluent pendant la construction

- **Date** : 2026-10-08
- **Remarque** : les specs évoluent pendant la construction. Chaque remarque ou suggestion du mainteneur est une entrée de specs : le coordinateur la consigne dans ce journal, l'analyse, puis la fait appliquer par un rôle.
- **Analyse** : un retour oral se perd dans le contexte d'une session. Le consigner le rend traçable, et le faire appliquer par un rôle le soumet à la même relecture que le reste. Selon RET-001, le coordinateur ne produit aucun livrable : il consigne le retour **dans le brief** du rédacteur, et c'est le rédacteur qui l'inscrit dans ce journal.
- **Impact** : ce journal ; process (circuit d'un retour) ; profil du rédacteur.
- **Statut** : appliqué.

## RET-004 — Un agent doit savoir dans quel environnement il tourne

- **Date** : 2026-10-08
- **Remarque** : une session d'agent ouverte dans un worktree ne savait pas qu'elle tournait dans Orca. Elle ne l'a découvert que lorsque le mainteneur l'a interrogée. N'aurait-elle pas dû le savoir plus tôt ?
- **Analyse** : le contexte d'environnement (outil d'orchestration, une tâche = un worktree, état et passation par la CLI `orca`, process dans `docs/process/README.md`) n'arrive pas automatiquement. `AGENTS.md` n'en parle pas, et la mémoire comme le process ne sont lus qu'à la demande. Un contexte neuf, principe des rôles, part donc sans repères.
- **Impact** :
  - `AGENTS.md` : section « Environnement », courte et générique ;
  - FR-038 : le cœur de jam injecte ce contexte à chaque rôle lancé ;
  - sur le poste du mainteneur, hors du repo : un hook de démarrage de session, installé, donne à chaque agent son contexte (worktree, branche, autres worktrees ; dans Orca, la carte du worktree avec son issue et sa PR, le rôle de la session ou « session libre », les autres agents actifs dans le même worktree, la CLI Orca et le chemin du process). C'est la préfiguration de FR-038 ;
  - profil du rédacteur : écriture permise dans `AGENTS.md` et `README.md`.
- **Statut** : appliqué.

## RET-005 — Le coordinateur aussi a ses garde-fous en code

- **Date** : 2026-10-08
- **Remarque** : « Tu devrais te mettre un hook aussi. »
- **Analyse** : les garde-fous d'un rôle, coordinateur compris, sont tenus par du code et non par la mémoire de l'agent. Que le coordinateur ne produise aucun livrable (RET-001) ne doit pas dépendre de son obéissance. Le coordinateur devient donc un rôle avec son profil : la variable `JAM_ROLE=coordinateur` l'identifie, et un hook refuse ses écritures hors des emplacements autorisés (voir plus bas). Ce hook est personnel au poste du mainteneur, hors du repo. Il a été installé le 2026-10-09, après deux tours de relecture, et n'agit que si la session est lancée avec la variable (un `export` depuis le shell de l'agent n'atteint pas les hooks). Il autorise la mémoire, le plan de la session, les dossiers temporaires et l'installation d'un hook relu (Q-026). Dans jam, c'est le cœur qui jouera ce rôle.
- **Impact** :
  - [ADR 0012](../decisions/0012-coordinateur-role-garde-fous-hook.md), qui complète l'ADR 0009 et y trace aussi les profils du rédacteur et de la variante du relecteur ;
  - profil [roles/coordinateur.md](../process/roles/coordinateur.md) ;
  - process et `AGENTS.md` : « aucun rôle du pipeline ni du cadrage ne committe » ; section « Ce qu'Orca ne permet pas » revue.
- **Statut** : appliqué.

## RET-006 — Relire jusqu'à satisfaction

- **Date** : 2026-10-08
- **Remarque** : « Pas qu'une relecture : tant que ce n'est pas satisfaisant, on fait relire. »
- **Analyse** : la relecture et la correction bouclent jusqu'à `RELECTURE : OK`, avec un relecteur neuf à chaque tour. Le plafond de deux allers-retours disparaît. À la place, la boucle s'arrête et remonte au mainteneur en cas d'**absence de progrès** ou de **dépassement de budget**. Un seul constat bloquant ou à corriger qui revient, en substance, au tour suivant suffit à escalader. C'est le coordinateur qui compare les rapports d'un tour à l'autre ; le relecteur, lui, ne lit pas les tours précédents.

  Le critère de cette boucle est le verdict des relecteurs, pas un test ni une CI. Le mainteneur a tranché : la relecture boucle jusqu'au verdict OK. NFR-010 est réécrite en conséquence. La décision de l'ADR 0008 est conservée. L'ADR 0011 (§1) précise que sa règle des critères objectifs vaut pour les boucles de code, et que la boucle de relecture s'arrête sur le verdict des relecteurs. À l'acceptation de l'ADR 0011, le statut de l'ADR 0008 mentionnera cette précision.
- **Impact** : process (relecture, garde-fous) ; FR-023, FR-024, NFR-010 ; profil du relecteur ; glossaire (« Garde-fou », « Tour de relecture ») ; ADR 0011 (critères des boucles, indicateur « tours de relecture »).
- **Statut** : appliqué.

## RET-007 — Plusieurs relecteurs pour le code

- **Date** : 2026-10-08
- **Remarque** : « Pour les grosses parties de code, on fait relire jusqu'à satisfaction par au minimum deux agents différents qui se partagent les tâches, plus si nécessaire. C'est le début de la loop. »
- **Analyse** : la relecture devient parallèle et découpée par **axe** :
  - **A, justesse** : bugs, tests, cas limites ;
  - **B, conformité** : plan, ADR, lisibilité, sur-ingénierie, sécurité du repo public.

  Chaque axe a son relecteur neuf et son fichier de relecture. Un gros diff justifie plus de relecteurs. La boucle de RET-006 tourne jusqu'à ce que tous les relecteurs disent OK. Seuil validé par le mainteneur : **tout code applicatif**. Les docs et les petites corrections hors code applicatif gardent un seul relecteur, dans la même boucle. Les relecteurs sont des instances Claude neuves ; la diversité de modèles est reportée à E2 (Q-034). Cette lecture de « deux agents différents » a été validée par le mainteneur (« ok pour tout », 2026-10-08).
- **Impact** : profil du relecteur ; process ; FR-022, FR-023 ; glossaire (« Axe de relecture »). L'ADR 0008 n'est pas modifiée : plusieurs instances du rôle relecteur restent une étape « relecture » au contexte neuf.
- **Statut** : appliqué.

## RET-008 — Le coordinateur vit sur `main`, pas dans un worktree

- **Date** : 2026-10-09
- **Remarque** : « C'est vraiment utile que ta session orchestrateur soit dans un worktree séparé ? » Décision prise avec le mainteneur : non.
- **Analyse** :
  - le coordinateur n'écrit aucun fichier du repo (RET-001) : un worktree ne lui sert à rien ;
  - constat : son ancien worktree était sur une vieille branche, 88 fichiers en retard sur `main`. Au démarrage, la session chargeait un `AGENTS.md` et un process périmés ;
  - sur le worktree principal (`main`), avec un `git pull` après chaque merge, il lit toujours la référence.
- **Impact** : lancement depuis le worktree principal, `JAM_ROLE=coordinateur claude` ; profil du coordinateur ; process ; `AGENTS.md` (section « Environnement ») ; [ADR 0013](../decisions/0013-orchestration-deux-niveaux.md).
- **Statut** : appliqué.

## RET-009 — Orchestration à deux niveaux

- **Date** : 2026-10-09
- **Remarque**, en substance :
  - sur `main`, un orchestrateur général, lancé avec un rôle à chaque session. Il peut lancer des agents pour écrire, relire, etc. ;
  - le même schéma un niveau en dessous : dans **chaque worktree**, un orchestrateur qui lance les agents de rédaction, de relecture, de test, etc. ;
  - le mainteneur peut parler à l'orchestrateur d'un worktree pour savoir où en est sa tâche. Cet orchestrateur remonte l'information à l'orchestrateur principal ;
  - but : un seul interlocuteur s'il le souhaite (l'orchestrateur sur `main`), et la possibilité de discuter en détail d'une feature en allant dans son worktree.
- **Analyse** :
  - cohérent avec la vision. Un seul interlocuteur préfigure le cockpit. Une orchestration par worktree préfigure le pipeline par issue ([ADR 0008](../decisions/0008-boucle-exterieure-pipeline.md)) et le lead, la session principale d'un worktree à qui le mainteneur parle. Différence : dans jam, l'orchestration d'une tâche est tenue par le cœur, en code ; dans Orca, c'est un agent ;
  - bénéfices : le contexte du coordinateur reste léger (il a saturé dans la nuit du 8 au 9 octobre), plusieurs tâches avancent en parallèle, et le mainteneur entre dans le détail d'une tâche sans encombrer le coordinateur.
- **Propositions du coordinateur**, **validées par le mainteneur** le 2026-10-09 (« ça me semble OK »). L'[ADR 0013](../decisions/0013-orchestration-deux-niveaux.md) a été acceptée au feu vert de cadrage formel du même jour, après la relecture :
  1. **Nommage** : « coordinateur » au niveau de `main`, « orchestrateur de tâche » au niveau d'un worktree ;
  2. **Remontée d'information** : l'orchestrateur de tâche tient l'état de sa tâche dans la carte Orca (statut et commentaire). C'est ce que lit le coordinateur. Pour un événement qui attend le mainteneur (feu vert, blocage), il prévient aussi le coordinateur par un message court qui renvoie à un fichier ;
  3. **Feux verts** : le mainteneur les donne à l'un ou l'autre niveau. Un feu vert donné dans un worktree est remonté au coordinateur ;
  4. **Commit, push, PR, merge** : l'orchestrateur de tâche committe, pousse sa branche et ouvre la PR, chacun après son feu vert. Le merge reste au coordinateur, après le feu vert merge : un seul acteur merge, les merges sont donc sérialisés et `main` est mis à jour au même endroit. Les autres rôles ne committent toujours pas ;
  5. **Lancement des rôles** : l'orchestrateur de tâche lance les rôles dans son worktree comme le coordinateur le faisait, avec les mêmes profils. Le coordinateur crée le worktree et lance l'orchestrateur de tâche avec son brief ;
  6. **Garde** : l'orchestrateur de tâche est un rôle, avec sa valeur de `JAM_ROLE` et les mêmes interdits d'écriture que le coordinateur. L'extension de la garde du poste est un travail hors repo (Q-036) ;
  7. **Quota** : la limite d'usage a été atteinte dans la nuit du 8 au 9 octobre avec 5 agents actifs. Le coordinateur décide combien d'orchestrateurs de tâche tournent en même temps, pour environ 3 agents actifs au total ;
  8. **Cadrages** : un cadrage suit le même schéma, avec un orchestrateur de tâche dans `cadrage-<slug>`. Le cadrage `cadrage-orchestration` est conduit directement par le coordinateur, puisque le modèle n'est pas encore adopté. Précisé à l'arbitrage qui a suivi le tour 1 de relecture : c'est une exception unique, conduite par le coordinateur jusqu'au merge, et décrite dans l'ADR 0013 seulement.
- **Compléments du mainteneur** (2026-10-09) :
  - **mise en place** : le modèle s'applique dès maintenant dans Orca, et il devient le cœur de jam ;
  - **dans jam, c'est le code qui orchestre** : l'ADR 0008 tient, le pipeline d'une tâche est codé dans le cœur, qui enchaîne les étapes et tient l'état. Les deux niveaux existent dans jam comme deux niveaux d'interlocuteurs : au niveau projet, le cockpit et la session conversationnelle de `main` (le coordinateur) ; au niveau tâche, le lead du worktree (FR-034). La remontée d'information devient structurelle : les deux niveaux lisent le même état du cœur. Dans Orca, faute de cœur, l'orchestrateur de tâche est un agent qui tient ce rôle à la main ;
  - **feu vert relayé** (constat du tour 1 de relecture, option retenue par le mainteneur) : tout feu vert relayé d'un niveau à l'autre (cadrage, plan, recette, merge) cite les mots exacts du mainteneur, l'heure et la session où il l'a donné. Il vaut alors feu vert, et accord explicite au sens de la règle 6 d'`AGENTS.md` pour l'action que ce feu vert ouvre, et elle seule (commit, push et PR après le feu vert recette ou de cadrage ; merge après le feu vert merge ; publication après le feu vert de cadrage ; aucune après le feu vert plan). Sans ces trois éléments, il ne vaut qu'information (format étendu à tout feu vert au tour 2 de relecture, portée de l'accord précisée au tour 3). Limite : l'expéditeur d'un message relayé n'est pas authentifié ; dans jam, le feu vert sera une action du cockpit, enregistrée par le cœur ;
  - **question ouverte, non tranchée** : avancer le coordinateur conversationnel dans E0, pour que le niveau projet existe dans jam dès E0 (Q-039).
- **Feu vert merge d'un cadrage**, proposé par le rédacteur et **décidé par le mainteneur** le 2026-10-09 : la PR d'un cadrage passe, comme toute PR, par un **feu vert merge** avant que le coordinateur la merge. Jusqu'ici, un cadrage n'avait que le feu vert de cadrage. Les issues et les milestones du cadrage sont publiés une fois sa PR mergée, pour que leurs liens vers les docs fonctionnent sur `main`.
- **Impact** : [ADR 0013](../decisions/0013-orchestration-deux-niveaux.md), qui précise l'ADR 0012 et complète l'ADR 0009 ; profil [roles/orchestrateur-tache.md](../process/roles/orchestrateur-tache.md) ; profils du coordinateur, du rédacteur, du relecteur et de l'implémenteur ; process (acteurs, lancement, correspondance, signalement, relecture, garde-fous) ; `AGENTS.md` (section « Environnement », règle 6) ; glossaire (« Orchestrateur de tâche », « Coordinateur », « Rôle », « Lead », « Agent actif », « Cadrage », « Feu vert ») ; Q-036 à Q-039, Q-028 et Q-033 (porteur) ; risques R-02 et R-03 de la roadmap. Les exigences ne changent pas : FR-021, FR-027 et FR-034 décrivent déjà le pipeline codé, l'état partagé et le lead.
- **Statut** : appliqué.

## RET-010 — La recette de l'agent part du même état que celle du mainteneur

- **Date** : 2026-10-09
- **Remarque**, en substance : la recette est une étape obligatoire ; celle de l'agent doit attraper ce que le mainteneur trouvera.
- **Constat** : à la recette manuelle du S1, sur le worktree principal, `pnpm install` puis `pnpm dev` échoue aussitôt (`Error: Electron uninstall`). La recette de l'agent ([`E0-S1-squelette-recette.md`](../plans/E0-S1-squelette-recette.md)) avait pourtant tout passé.
- **Analyse** (du coordinateur, vérifiée) :
  - Electron 44 ne télécharge plus son binaire à l'installation, mais au premier `require('electron')`. Après un `pnpm install` neuf, le binaire est absent ;
  - electron-vite 5 lit le chemin du binaire lui-même et échoue s'il manque, sans déclencher le téléchargement : `pnpm dev` ne marche donc jamais sur une installation neuve ;
  - la recette de l'agent a d'abord lancé l'app par Playwright, qui passe par `require('electron')` et a téléchargé le binaire. Elle n'a vérifié `pnpm dev` qu'en dernier (contrôle « 3 bis »), quand le binaire était déjà là : un contrôle a préparé le terrain du suivant ;
  - la CI ne lance jamais `pnpm dev`.
- **Règle** : la recette de l'agent part d'une **installation neuve** (dépendances réinstallées depuis zéro, sans binaire préparé par un autre contrôle), et déroule **d'abord la check-list du mainteneur**, avec ses commandes et dans son ordre. Les contrôles outillés (Playwright, etc.) viennent ensuite. Aucun mécanisme nouveau. La réinstallation est une étape de la recette : elle relève de la « commande de recette » et du « réseau selon la recette » que l'[ADR 0009](../decisions/0009-permissions-par-role.md) donne au recetteur. Elle ne touche aucun fichier suivi par git : le recetteur reste en lecture seule sur le repo.
- **Impact** : profil [roles/recetteur.md](../process/roles/recetteur.md) ; process (section « Recette ») ; Q-033 (la commande du recetteur doit permettre la réinstallation) ; brouillon d'issue du bug dans [`cadrage-orchestration-issues.md`](../plans/cadrage-orchestration-issues.md). Les exigences ne changent pas.
- **Statut** : appliqué.

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
  - profil de l'[orchestrateur de tâche](../process/roles/orchestrateur-tache.md) : préparer et vérifier le clone, le donner au planificateur et, pour une reprise, à l'implémenteur (ajouté à l'intégration de `main`, Q-042) ;
  - [`docs/references/orca.md`](../references/orca.md) : rôle de carte, version de référence, procédure du clone, liste noire ;
  - `AGENTS.md`, règle 9 ; glossaire (« Clone de référence ») ; Q-040, Q-042, Q-043.
- **Statut** : appliqué (feu vert de cadrage du 2026-10-09 ; intégration de `main` relue au tour 10).

## RET-012 — Le coordinateur vit dans le terminal flottant d'Orca, lancé depuis le worktree principal

- **Date** : 2026-10-09
- **Remarque** : « ça serait pas mieux d'ouvrir les "agents" comme toi au top niveau dans Orca dans le floating workspace ? » Proposition validée, testée et appliquée le jour même. Complément du mainteneur, pour jam : « si on fait le même système sur jam, il faut atterrir dans le dossier principal (peut-être un réglage) ».
- **Analyse** (du coordinateur) :
  - le terminal flottant est accessible depuis tous les worktrees : le mainteneur parle au coordinateur de partout, pendant une recette par exemple. C'est l'interlocuteur unique de RET-009 dans l'interface ;
  - RET-008 tient : la session est lancée depuis le worktree principal. La CLI `orca` voit le terminal flottant (`worktreeId` vaut `global-floating-terminal`, sans chemin de worktree), mais il s'ouvre dans le dossier personnel. Il faut donc se placer dans le worktree principal avant `JAM_ROLE=coordinateur claude` (avec `--continue` pour reprendre une session) ;
  - pour jam, le complément se traduit par une précision de FR-016 : le champ de conversation accessible partout ouvre une session qui tourne dans le worktree principal du repo. L'étape du coordinateur conversationnel ne change pas (Q-039).
- **Impact** : [ADR 0015](../decisions/0015-remontee-carte-seule-coordinateur-flottant.md), qui précise l'ADR 0013 ; profil du coordinateur ; process (acteurs, correspondance, lancement du coordinateur) ; FR-016 et Q-051 (cas de plusieurs repos) ; `02-ARCHITECTURE.md` (composant « Coordinateur ») ; glossaire (« Terminal flottant », « Coordinateur »).
- **Statut** : appliqué.

## RET-013 — Plus de message de l'orchestrateur de tâche dans le terminal du coordinateur

- **Date** : 2026-10-09
- **Remarque** : « je vois des trucs apparaître automatiquement dans le prompt ».
- **Constat** : les messages courts de l'orchestrateur de tâche (`orca terminal send`) s'insèrent dans la saisie du terminal du coordinateur, où le mainteneur écrit aussi. Le risque noté dans l'ADR 0013 (Q-037) s'est produit pendant le premier essai du modèle à deux niveaux (issue #7).
- **Analyse** (du coordinateur) : la carte Orca suffit comme canal montant. Règle appliquée dans Orca dès le 2026-10-09, sur consigne du coordinateur : l'orchestrateur de tâche tient **seulement sa carte** (statut et commentaire, avec le chemin du fichier à lire, désigné dans son worktree) ; le coordinateur surveille les cartes en arrière-plan. Le coordinateur peut toujours écrire dans le terminal d'un orchestrateur de tâche, qui est un agent. Un feu vert donné dans le worktree remonte par le commentaire de la carte, au format de tout feu vert relayé (mots exacts, heure, session) ; un feu vert donné au coordinateur arrive à l'orchestrateur de tâche par son terminal.
- **Impact** : [ADR 0015](../decisions/0015-remontee-carte-seule-coordinateur-flottant.md) ; profils de l'orchestrateur de tâche et du coordinateur ; process (acteurs, cadrage, correspondance, lancement, « Remontée vers le coordinateur », « Signalement d'attente », « Ce qu'Orca ne permet pas ») ; glossaire (« Orchestrateur de tâche ») ; Q-037 tranchée.
- **Statut** : appliqué.
