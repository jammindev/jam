# Retours du mainteneur

> Journal des remarques et suggestions faites par le mainteneur pendant la construction. Chaque retour est une entrée de specs (RET-003). Le coordinateur, ou l'orchestrateur de tâche qui l'a reçu, reformule et analyse le retour ; le rédacteur l'inscrit ici et l'applique ; le relecteur relit. Les numéros ne sont jamais réutilisés.
>
> Statuts : **consigné** → **en application** (un rôle rédige) → **appliqué** (relu, feu vert de cadrage donné). Le rédacteur passe un retour à « appliqué » juste après le feu vert, avant le commit de l'orchestrateur de tâche.

## RET-001 — Le coordinateur ne produit aucun livrable

- **Date** : 2026-10-08
- **Remarque** : le coordinateur a créé lui-même les milestones GitHub et les issues #1 à #4. Comme ces éléments posent les bases de l'app, ils auraient dû être produits par un autre agent, puis relus.
- **Analyse** : le principe « une méthode imposée plutôt qu'espérée » ne vaut pas que pour le code. Le coordinateur orchestre : il ne produit aucun livrable. Tout livrable, y compris hors code (issues, specs, ADR, docs), suit le même chemin : production par un rôle, relecture indépendante, feu vert.
- **Impact** :
  - process : rôle `rédacteur` créé ([roles/redacteur.md](../../roles/redacteur.md)) ; le cadrage passe par le rédacteur puis le relecteur ([process](../../process/README.md)) ;
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
  - profil [roles/coordinateur.md](../../roles/coordinateur.md) ;
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
- **Impact** : [ADR 0013](../decisions/0013-orchestration-deux-niveaux.md), qui précise l'ADR 0012 et complète l'ADR 0009 ; profil [roles/orchestrateur-tache.md](../../roles/orchestrateur-tache.md) ; profils du coordinateur, du rédacteur, du relecteur et de l'implémenteur ; process (acteurs, lancement, correspondance, signalement, relecture, garde-fous) ; `AGENTS.md` (section « Environnement », règle 6) ; glossaire (« Orchestrateur de tâche », « Coordinateur », « Rôle », « Lead », « Agent actif », « Cadrage », « Feu vert ») ; Q-036 à Q-039, Q-028 et Q-033 (porteur) ; risques R-02 et R-03 de la roadmap. Les exigences ne changent pas : FR-021, FR-027 et FR-034 décrivent déjà le pipeline codé, l'état partagé et le lead.
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
- **Impact** : profil [roles/recetteur.md](../../roles/recetteur.md) ; process (section « Recette ») ; Q-033 (la commande du recetteur doit permettre la réinstallation) ; brouillon d'issue du bug dans [`cadrage-orchestration-issues.md`](../plans/cadrage-orchestration-issues.md). Les exigences ne changent pas.
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
  - profil du [planificateur](../../roles/planificateur.md) : lecture du clone, section « Orca » du plan ;
  - profils de l'[implémenteur](../../roles/implementeur.md) (reprise, licence, accès au clone) et du [relecteur](../../roles/relecteur.md) (axe conformité) ;
  - profil du [rédacteur](../../roles/redacteur.md) : compléter la carte au cadrage d'un jalon (complément 2) ;
  - profil de l'[orchestrateur de tâche](../../roles/orchestrateur-tache.md) : préparer et vérifier le clone, le donner au planificateur et, pour une reprise, à l'implémenteur (ajouté à l'intégration de `main`, Q-042) ;
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

## RET-014 — Pivot : la méthode plutôt que l'outil

- **Date** : 2026-10-11
- **Remarque** : « je pense que j'ai été trop loin à vouloir faire un outil dédié, j'ai pas trop le temps en fait. Par contre ça a permis d'affiner la méthode. Prends en compte le nouveau setup avec [le poste de travail] etc. Ça me satisfait pour le moment ce que j'ai mis en place. » Puis « ok à tout » sur la proposition du coordinateur résumée ci-dessous. Entre crochets : le nom de la machine, remplacé (repo public).
- **Analyse** (du coordinateur, validée par le mainteneur) :
  - la méthode (coordinateur sur `main`, orchestrateur de tâche par worktree, rôles neufs, trois feux verts, remontée par la carte Orca) tourne déjà sur trois projets du mainteneur, dans Orca, sans l'app. L'app Electron n'est plus nécessaire ;
  - la méthode vit mal : (1) sa référence est dans ce repo, et chaque autre projet la recopie et la transpose à sa façon, d'où une dérive ; (2) les garde-fous en code (garde du coordinateur, garde des écritures distantes, reprise de contexte, contrôle d'état git, environ 60 Ko avec leurs tests) vivent hors de tout dépôt, sur le poste de travail ; (3) des outils indispensables (script de veille des cartes, schéma de la CLI Orca) et les notes de frictions des essais vivaient dans un dossier temporaire ; (4) le process est mêlé aux ADR de l'outil (Electron, `stream-json`, SQLite).
- **Décision** :
  - jam reste ce repo et garde son nom, mais devient un **plugin Claude Code** installé sur le poste de travail et utilisé par tous les projets : `process/`, `roles/` (les sept profils, rendus génériques), `hooks/` avec leurs tests (rapatriés, versionnés, câblés par le plugin), `scripts/` (veille des cartes, lancement d'une tâche, relais d'un feu vert), `skills/` (lancer une tâche, présenter un feu vert, reprise…), `modeles/` (brief d'orchestrateur, plan, rapports de relecture et de recette) ;
  - chaque projet n'a plus qu'une **fiche projet**, `docs/methode.md` : sa commande de test, sa grille de relecture, sa recette, ce que veut dire un merge (mise en production ou non), son plafond d'agents. Plus de transposition par brief, plus de copie de la méthode dans les mémoires ;
  - **allègements nés des frictions** : trois **niveaux de tâche** fixés au plan (*léger* : docs et cosmétique, un relecteur, pas de recette agent ; *standard* : le déroulé actuel ; *argent ou prod* : régime renforcé) ; **seuil « assez bon »** (un tour de relecture qui ne trouve que du cosmétique clôt la boucle ; un cadrage a fait 11 tours) ; **plafond d'agents global** au poste, lu par chaque coordinateur (`orca terminal list`), au lieu d'une estimation partagée ;
  - **sort de l'app** : les issues #13 à #20 sont fermées « not planned » et le milestone E0-S2 fermé, par le coordinateur, hors de ce cadrage ; le dernier état de l'app est gardé au tag `app-electron`, posé par le coordinateur ; le retrait du code Electron (`apps/`, `packages/`, outillage pnpm, Vitest et CI qui ne sert plus) est une issue de ce cadrage, pas une action du cadrage.
- **Impact** : [ADR 0016](../decisions/0016-kit-de-methode.md) ; `00-VISION.md` à `04-ROADMAP.md` (exigences de l'app marquées abandonnées, FR-042 à FR-051, NFR-013 et NFR-014, jalon K1) ; `03-HARNESS.md` marqué historique ; glossaire (« Kit », « Plugin », « Fiche projet », « Niveau de tâche », « Seuil « assez bon » », « Plafond d'agents global », « Poste de travail », termes de l'app marqués) ; questions rendues sans objet, Q-054 à Q-061 ; `AGENTS.md` et `README.md` (présentation, stack) ; brouillons d'issues [`cadrage-kit-issues.md`](../plans/cadrage-kit-issues.md).
- **Statut** : appliqué.

## RET-015 — Le coordinateur vit dans le worktree `main`, sur le poste de travail

- **Date** : 2026-10-10, complété le 2026-10-11
- **Remarque** (transmise par le coordinateur) : le coordinateur d'un projet tourne dans un terminal Orca du worktree `main` de ce projet, plus dans le terminal flottant. Une session dans le terminal flottant n'a plus de rôle.
- **Analyse** :
  - remplace la partie « terminal flottant » de l'[ADR 0015](../decisions/0015-remontee-carte-seule-coordinateur-flottant.md). Le reste de cette ADR, la remontée par la carte seule, tient ;
  - le terminal flottant est unique pour tous les projets ouverts dans Orca : il ne peut pas porter un coordinateur par projet. Dans un terminal du worktree principal, la session part du bon dossier : plus de `cd` à oublier ;
  - **contexte nouveau** (2026-10-11) : les agents tournent désormais sur une machine dédiée, le poste de travail. Orca y tourne, et le mainteneur le pilote depuis un autre poste par le serveur Orca distant. Conséquences : les agents se lancent par Orca, car une session lancée par SSH n'a pas les identifiants ; rien d'indispensable ne vit dans un dossier temporaire, puisque le poste peut redémarrer et que ce dossier est alors vidé ; une fenêtre d'autorisation du système bloque un agent jusqu'à ce que le mainteneur la valide sur l'écran du poste.
- **Impact** : [ADR 0017](../decisions/0017-coordinateur-main-poste-de-travail.md) ; process (acteurs, correspondance, lancement du coordinateur) et profil du coordinateur ; glossaire (« Coordinateur », « Terminal flottant », « Poste de travail ») ; NFR-013 ; Q-058 et Q-059.
- **Statut** : appliqué.

## RET-016 — Un kit minimal, puis gelé

- **Date** : 2026-10-11
- **Remarque** : « ok go », à 13:58, dans la session du coordinateur du `main` de jam, en réponse à une synthèse du coordinateur, complétée par l'avis d'une autre session d'agent que le mainteneur avait demandé. Ces retours priment sur le premier découpage du cadrage `cadrage-kit`.
- **Analyse** : le temps du mainteneur est la contrainte principale. Le kit est le troisième chantier de méthode d'affilée ; la méthode doit servir les livraisons des projets, pas l'inverse. Le premier risque du jalon est que le kit devienne un chantier sans fin.
- **Décisions** :
  1. **Kit minimal, puis gelé.** Le jalon K1 compte trois issues au plus, pour deux à trois jours de travail. Une fois livrées, le kit est gelé : il ne change que sur une friction vécue dans un projet, jamais pour améliorer la méthode en soi.
     - *Issue 1, le repo devient le kit* : retrait du code Electron, hooks rapatriés avec leurs tests, scripts de veille des cartes et de lancement d'une tâche. **Un seul garde-fou de sortie** (commit, push, merge, écritures `gh`) remplace les trois qui se recouvrent aujourd'hui sur le poste ; la garde du coordinateur reste. Constat : les hooks ont déjà divergé d'un poste à l'autre, faute d'être versionnés. Les commandes des rôles pour cette première tâche (constat B-1 du tour 1 de relecture) y sont traitées.
     - *Issue 2, process élagué* : process et profils génériques, plus courts qu'aujourd'hui, sous un plafond de taille ; l'historique (« Origine : … ») part dans les ADR ; toute nouvelle règle dit laquelle elle remplace ou retire. Y figurent les niveaux, la fiche projet (gabarit et fiche de jam) et le relais allégé (décisions 2 à 5).
     - *Issue 3, page publique* : le `README.md` de jam devient la page « comment je travaille avec des agents » : courte, strictement factuelle, avec les quelques chiffres réellement mesurés (décision 6), rien d'inventé.
     - *Retirés du jalon* : skills, modèles, script d'indicateurs, bascule groupée des autres projets. Chaque projet adopte sa fiche quand il en a besoin, sans tâche dédiée.
  2. **Niveaux selon le risque du projet**, pas seulement selon la taille de la tâche. La fiche projet fixe le niveau par défaut : *standard* pour un projet en production qui touche à l'argent ou à des données de personnes ; *léger* pour un site statique ou pour jam, et partout ailleurs. Le plan peut monter d'un niveau en le motivant.
  3. **En niveau léger, pas d'orchestrateur de tâche** : le coordinateur lance lui-même l'implémenteur, puis un relecteur. Pas de script pour remplacer l'orchestrateur maintenant. Exception à l'ADR 0013.
  4. **Relais du feu vert allégé** : la forme complète (mots exacts, heure, session) reste obligatoire pour le merge d'un projet en production ; pour le plan et la recette, un « ok » transmis suffit.
  5. **Recette d'une interface** : quand un navigateur piloté (Playwright) est disponible, le recetteur livre des captures ou un enregistrement du parcours, pour que la recette du mainteneur se réduise à une vérification rapide.
  6. **Mesure** : pas de script d'indicateurs. Une seule mesure, notée à la main dans la PR ou le plan : le temps passé par le mainteneur sur l'issue. Elle alimente la page publique.
  7. **Périmètre** : le kit ne s'étend à aucun autre projet du mainteneur pendant ce jalon. Rien de propre à un autre projet ni à des tiers dans le kit ni dans les fiches : le repo est public.
- **Impact** : [ADR 0016](../decisions/0016-kit-de-methode.md) (gel, contenu du plugin, niveaux, léger sans orchestrateur, relais allégé, mesure) ; `00-VISION.md`, `01-REQUIREMENTS.md` (FR-043 à FR-051 revues, FR-052 à FR-056, NFR-015 et NFR-016), `02-ARCHITECTURE.md`, `04-ROADMAP.md` (jalon K1 en trois issues, risque R-07) ; glossaire ; Q-053, Q-055, Q-057, Q-060, Q-061 revues, Q-062 et Q-063 ; `AGENTS.md`, `README.md` ; profils de l'implémenteur, du relecteur et du recetteur (commandes de l'issue 1) ; brouillons d'issues redécoupés.
- **Statut** : appliqué.

## RET-017 — La veille voit les cartes que personne ne tient, et un relais se vérifie

- **Date** : 2026-10-11, ajouté à l'issue #23 (point 7)
- **Remarque** : retour du coordinateur d'un autre projet du poste, repris dans l'issue #23. Un relais de feu vert envoyé par `orca terminal send` a été avalé par une fenêtre : il n'est jamais arrivé à la session visée, et rien ne l'a signalé. Pendant ce temps, la veille des cartes tournait à vide : la carte restait `▶`, et la veille ne se réveillait que sur `⏸`, `⛔`, `✓` ou `💬`.
- **Analyse** :
  - une carte est tenue par un agent. Bloqué sur une invite d'autorisation, arrêté, ou en attente d'un relais qui n'est pas venu, il ne la tient plus, et la carte reste `▶`. La règle « quand une carte reste longtemps `in-progress`, le coordinateur vérifie l'état de l'agent » (ADR 0013, ADR 0017) suppose qu'il y pense : il n'y pensait pas ;
  - Orca connaît l'état de chaque agent d'un worktree (`orca worktree ps`) : la veille peut le lire. Elle se réveille sur une **transition**, un agent qui passe en attente d'autorisation ou une carte sans agent au travail depuis N minutes, une seule fois par **épisode** : sans cela, elle réveillerait le coordinateur à chaque lecture ;
  - un relais qui n'arrive pas ne se voit que si on le cherche : 30 s après l'envoi, `orca terminal read` lit l'écran de la session visée. Le relais est court, et sans négation, que la garde de sortie lirait comme un refus (friction 24 de #22).
- **Impact** : FR-046 ; `scripts/watch_cards.py` (deux réveils, `--idle-minutes`) ; process (« Carte, feux verts et veille ») et profil du coordinateur ; [ADR 0018](../decisions/0018-process-elague.md) (remplace la vérification à la main) ; glossaire (« Agent en cours », « Épisode », « Veille des cartes ») ; fiche concept `docs/concepts/veille-et-mesure.md`. Limite : une fenêtre d'autorisation du système laisse l'agent au travail, la veille ne la voit pas (Q-059).
- **Statut** : appliqué.

## RET-018 — Le temps du mainteneur est estimé par un script

- **Date** : 2026-10-12, ajouté à l'issue #23 (point 8)
- **Remarque** : ne plus demander au mainteneur le temps qu'il a passé sur une issue ; un script l'estime, et la session qui ouvre la PR l'y note.
- **Analyse** :
  - FR-055 demandait une mesure « notée à la main » : personne ne chronomètre, et une estimation au jugé ne vaut pas une mesure. Les transcripts de Claude Code gardent chaque message du mainteneur, avec son heure ;
  - le script reprend le tri des messages du mainteneur de la garde de sortie (même fonction, pour que les deux lectures ne divergent pas) et écarte ce qu'il n'a pas tapé : commandes `!` et messages d'autres agents. Des messages à moins de 10 min l'un de l'autre forment un moment, qui vaut sa durée plus 3 min de lecture (feu vert plan de #23) ;
  - seules les sessions du coordinateur, sur le worktree principal, sont lues, à l'écart de l'issue #23 qui nommait aussi celles de la tâche : à la recette de #23, tout ce qui arrivait dans le worktree de #22 venait d'agents, et le script en comptait les relais comme des messages du mainteneur (décision du mainteneur, 2026-10-13) ;
  - c'est une estimation, avec des limites écrites : un « ok » qui suit un résumé de plusieurs tâches compte pour chacune ; un message qui ne nomme pas la tâche est perdu ; la recette du mainteneur, faite dans une session du worktree de la tâche, n'est pas comptée, ni un feu vert tapé là (Q-065). La page publique le présente comme une estimation ;
  - le mainteneur ne compte rien lui-même, il ne valide donc pas le chiffre (retour du 2026-10-13, à la recette de #23) : sa vérification n'aurait été qu'un second relevé à la main. La publication de la page reste soumise à son feu vert. Ce n'est pas le script d'indicateurs que RET-016 écarte : il ne mesure que le temps du mainteneur.
- **Impact** : FR-055, FR-046, FR-056 ; `00-VISION.md` et `04-ROADMAP.md` (critère de fin du jalon K1) ; `scripts/maintainer_time.py` ; process (« Mesure ») et profils du coordinateur et de l'orchestrateur de tâche ; [ADR 0018](../decisions/0018-process-elague.md) ; Q-057 ; glossaire (« Moment ») ; fiche concept `docs/concepts/veille-et-mesure.md` ; issue de la page publique (K1-3), dont le passage « Chiffres » demande des chiffres mesurés et est à aligner sur FR-056 (corps de l'issue modifié par le coordinateur après le merge, sur feu vert). Un message ne compte que s'il porte le numéro d'issue ou le nom du worktree de la tâche : la règle « Messages au mainteneur » (RET-019) rend ce numéro obligatoire.
- **Statut** : appliqué.

## RET-019 — Les messages au mainteneur se lisent seuls

- **Date** : 2026-10-13, à la recette de l'issue #23 ; accord du mainteneur sur la règle le même jour, relayé par le coordinateur
- **Remarque** : le mainteneur suit plusieurs projets et ne lit que les sessions de `main`. Il ne peut pas retenir à quoi renvoient « issue #22 » ou « friction 18 ». Un message qui en dépend l'oblige à aller chercher le sens ailleurs.
- **Analyse** :
  - le défaut est réel et vient de la tâche même : la tête « À décider » du rapport de recette de #23 parlait de « friction 18 » et de « #22 » sans dire ce qu'ils désignent ;
  - les numéros servent aux rôles, qui ont les fichiers sous la main. Le mainteneur, lui, lit hors contexte, à côté d'autres projets ;
  - la règle vaut pour tout ce qui lui est adressé : la carte, la tête « À décider » d'un fichier ouvert pour lui, le résumé du coordinateur. Elle ne touche pas les fichiers de travail entre rôles. Elle coûte quelques mots par message, sous le plafond du process.
- **Règle** (« Messages au mainteneur ») : tout message adressé au mainteneur se lit seul. Il nomme le projet et la tâche en mots, la tâche suivie de son numéro d'issue entre parenthèses, avec son dièse (« (#23) »), que lit la mesure du temps (RET-018). Toute autre référence interne (friction, ADR, RET, FR) est remplacée par ce qu'elle désigne, le numéro au plus entre parenthèses.
- **Impact** : process (« Messages au mainteneur ») et profils du coordinateur, de l'orchestrateur de tâche, du planificateur et du recetteur ; [ADR 0018](../decisions/0018-process-elague.md) (règle ajoutée, sans rien remplacer). Les exigences ne changent pas.
- **Statut** : appliqué.
