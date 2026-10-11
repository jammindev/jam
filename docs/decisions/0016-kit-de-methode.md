# ADR 0016 : jam est un kit de méthode, pas un outil

- **Statut** : acceptée (feu vert de cadrage du 2026-10-11)
- **Date** : 2026-10-11
- **Tranche** : RET-014, RET-016. Rend caduques ou historiques plusieurs ADR, en précise d'autres, dont l'ADR 0013 (voir « Sort des ADR existantes »)

## Contexte

jam visait une app Electron, un cockpit qui déroule le pipeline du mainteneur en code ([ADR 0008](0008-boucle-exterieure-pipeline.md)). Le jalon S1 a été livré, le S2 découpé. En attendant l'app, la méthode a été déroulée à la main dans Orca, et c'est elle qui a mûri : coordinateur sur `main`, orchestrateur de tâche par worktree, rôles neufs, trois feux verts, remontée par la carte Orca ([ADR 0013](0013-orchestration-deux-niveaux.md), [ADR 0015](0015-remontee-carte-seule-coordinateur-flottant.md)).

Le 2026-10-11, le mainteneur constate qu'il n'a pas le temps de construire l'outil, et que la méthode telle qu'elle tourne lui suffit (RET-014). Elle tourne déjà sur trois de ses projets, dans Orca, sans l'app.

Elle vit pourtant mal :
- sa référence est dans ce repo, et chaque autre projet la recopie et la transpose à sa façon : elle dérive ;
- ses garde-fous en code, des hooks de Claude Code, vivent sur les postes, hors de tout dépôt. Ils ont déjà divergé d'un poste à l'autre, et trois d'entre eux se recouvrent pour garder les sorties (commit, push) ;
- des outils indispensables (veille des cartes, schéma de la CLI Orca) et les notes de frictions des essais vivaient dans un dossier temporaire ;
- le process est mêlé aux ADR de l'outil (Electron, `stream-json`, SQLite), et il s'est alourdi d'essai en essai.

Le temps du mainteneur est la contrainte principale. Le kit est le troisième chantier de méthode d'affilée : le premier risque est qu'il devienne un chantier sans fin (RET-016).

## Décision

### jam devient un plugin Claude Code, minimal

- jam reste ce repo et garde son nom. Il ne construit plus d'app : il porte la méthode, sous la forme d'un **plugin Claude Code** installé une fois sur le poste de travail.
- Le repo est lui-même le plugin. Ses dossiers, à la racine :

| Dossier | Contenu |
|---|---|
| `process/` | Le déroulé, élagué : étapes, niveaux, feux verts et leur relais, carte Orca, garde-fous ; le gabarit de la fiche projet |
| `roles/` | Les sept profils de rôle, génériques : coordinateur, orchestrateur de tâche, rédacteur, planificateur, implémenteur, relecteur, recetteur |
| `hooks/` | Garde du coordinateur, **garde de sortie unique** (commit, push, merge, écritures `gh`), reprise de contexte, contrôle d'état git ; avec leurs tests |
| `scripts/` | Veille des cartes, lancement d'une tâche |

- `docs/` reste la documentation de jam lui-même : specs, ADR, retours, plans de ses tâches.
- La garde de sortie unique remplace les gardes qui se recouvrent aujourd'hui sur le poste. La garde du coordinateur reste distincte : elle ne garde pas les sorties, mais les écritures de fichiers.
- Installée pour tout le poste de travail, la garde de sortie s'applique à tous les projets du poste, y compris ceux qui n'ont pas encore de fiche. C'est voulu : « pas de merge ni de publication sans accord du mainteneur » vaut partout. Cela ne contredit pas « le kit ne s'étend à aucun autre projet », qui vise la méthode et la fiche.
- Ni skills, ni modèles, ni script d'indicateurs dans ce jalon ([Q-062](../specs/OPEN-QUESTIONS.md)).

### Kit gelé

- Le jalon K1 compte **trois issues au plus**, pour deux à trois jours de travail.
- Une fois livré, **le kit est gelé** : il ne change que sur une friction vécue dans un projet, jamais pour améliorer la méthode en soi.
- Toute nouvelle règle dit laquelle elle remplace ou retire. Le process tient sous un plafond de taille ; l'historique d'une règle (« Origine : … ») va dans une ADR, pas dans le process.
- Le kit ne s'étend à aucun autre projet du mainteneur pendant ce jalon. Chaque projet adopte sa fiche quand il en a besoin, sans tâche dédiée.

### Chaque projet a une fiche, et rien d'autre

- Un projet qui suit la méthode a une **fiche projet**, `docs/methode.md` : son niveau par défaut, sa commande de test, sa grille de relecture, sa recette, ce que veut dire un merge (mise en production ou non), son plafond d'agents. Ce plafond est une borne propre au projet, en plus du plafond global ci-dessous, pas une part de celui-ci.
- Plus de transposition de la méthode par brief, plus de copie dans les mémoires.
- Rien de propre à un autre projet ni à des tiers dans le kit ; jam a sa propre fiche, publique comme le reste du repo.

### Niveaux selon le risque du projet

- La fiche projet fixe le **niveau par défaut** du projet :
  - *standard* pour un projet en production qui touche à l'argent ou à des données de personnes : le déroulé complet ;
  - *léger* partout ailleurs, par exemple un site statique ou jam.
- Une tâche peut **monter d'un niveau**, en le motivant : dans l'issue, ou au plan. Au-dessus de *standard*, le niveau *renforcé* (appelé « argent ou prod » dans RET-014) n'a pas encore de contenu : il sera fixé quand une tâche en aura besoin ([Q-061](../specs/OPEN-QUESTIONS.md)).
- **En léger, pas d'orchestrateur de tâche ni de planificateur** : l'issue tient lieu de plan, et il n'y a pas de feu vert plan. Le coordinateur lance lui-même l'implémenteur (ou le rédacteur, pour des docs), puis **un seul relecteur**, même pour du code applicatif ; il tient la carte et la boucle de relecture, puis committe, pousse et ouvre la PR après le feu vert recette, et merge après le feu vert merge. Pas de recette par un agent : le mainteneur recette.

### Allègements nés des frictions

- **Seuil « assez bon »** : un tour de relecture qui ne trouve que du cosmétique clôt la boucle. Des cadrages ont fait 9 et 11 tours, chaque relecteur neuf trouvant un cran de plus.
- **Plafond d'agents global** : un seul plafond pour le poste de travail, tous projets confondus. Toute session qui lance un agent (coordinateur, ou orchestrateur de tâche au niveau *standard*) compte les agents en cours (`orca terminal list`) avant de le lancer, par exemple par le script de lancement, et ne le lance que si ni le plafond global ni celui de son projet ne sont atteints. Le plafond porte sur les **agents en cours**, c'est-à-dire les sessions d'agent que liste Orca, qu'elles travaillent ou attendent, et non plus sur les agents actifs de l'ADR 0013 : un script sait compter les premiers, pas les seconds.
- **Relais d'un feu vert allégé** : la forme complète (mots exacts du mainteneur, heure, session) reste obligatoire pour le merge d'un projet en production, et pour les feux verts qu'aucune règle n'allège. Pour le feu vert plan et le feu vert recette, un « ok » transmis suffit. Un feu vert remonté par la carte pour une action du coordinateur (merge, publication) est confirmé par le mainteneur dans le terminal du coordinateur : la garde de sortie ne lit que les messages de la session qui agit.
- **Recette d'une interface** : quand un navigateur piloté (Playwright) est disponible, le recetteur livre des captures ou un enregistrement du parcours ; la recette du mainteneur se réduit à une vérification rapide.
- **Mesure** : une seule, notée à la main dans la PR ou le plan : le temps passé par le mainteneur sur l'issue. Pas de script d'indicateurs. Elle alimente la page publique de jam, son `README.md`.

Le détail de ces règles est écrit dans `process/` et les profils, par l'issue « Process élagué » du jalon K1. **Entrée en vigueur** : toutes ces règles s'appliquent au merge de cette issue, qui les écrit dans `process/` ; jusque-là, `docs/process/README.md` et la règle 6 d'`AGENTS.md` s'appliquent tels quels. C'est aussi à ce moment que le plugin, et donc sa garde de sortie, est installé sur le poste.

### Sort de l'app

- Les issues #13 à #20 sont fermées « not planned » et le milestone E0-S2 fermé.
- Le dernier état de l'app est gardé au tag `app-electron`.
- Le retrait du code Electron (`apps/`, `packages/`, outillage pnpm, Vitest et CI qui ne sert plus) fait partie de la première issue du jalon K1. Les fiches concept de l'app restent, marquées historiques.

### Sort des ADR existantes

Trois sorts :
- **caduque** : la décision réglait l'app ; plus rien ne l'applique ;
- **historique** : la décision n'est pas contredite, mais elle n'a plus d'objet ; elle reste comme trace ;
- **valable** : la décision règle encore la méthode, en tout ou en partie.

| ADR | Sort | Ce qui reste |
|---|---|---|
| [0001](0001-from-scratch.md) From scratch, Orca référence de lecture | Historique | Le choix « from scratch » portait sur l'app. Orca reste l'outil où la méthode tourne ; la règle de licence d'un code repris reste dans `AGENTS.md` (règle 9). |
| [0002](0002-orchestrer-claude-code-avant-harness.md) Orchestrer Claude Code avant le harness | Caduque | Ni app ni harness maison. |
| [0003](0003-code-ecrit-par-agents.md) Code écrit par des agents | Valable | Hooks et scripts du kit sont écrits par des agents ; le mainteneur ne code pas. |
| [0004](0004-claude-code-headless-stream-json.md) Claude Code headless `stream-json` | Caduque | Aucun cœur ne lance Claude Code. Le mode de lancement des rôles reste ouvert ([Q-054](../specs/OPEN-QUESTIONS.md)). |
| [0005](0005-electron-macos.md) Electron, macOS | Caduque | — |
| [0006](0006-coeur-separe-ui.md) Cœur séparé de l'UI | Caduque | — |
| [0007](0007-commandes-ui-partagees-agent.md) Commandes d'UI partagées | Caduque | — |
| [0008](0008-boucle-exterieure-pipeline.md) Boucle extérieure codée dans le cœur | Valable en partie | Le pipeline reste la méthode du niveau *standard* : source issue, plan, TDD, relecture au contexte neuf, recette, trois feux verts, PR et CI, merge, garde-fous. Caduc : le pipeline codé dans un cœur, l'état persisté par lui, le coordinateur conversationnel « après E0 ». Le pipeline est tenu par l'orchestrateur de tâche, ou par le coordinateur en *léger* ; ce que le code peut garantir l'est par les hooks. |
| [0009](0009-permissions-par-role.md) Permissions par rôle | Valable en partie | Les profils passent par les options de la CLI de chaque session. Caduc : le repérage des refus par le cœur et leur entrée dans une file de l'app. |
| [0010](0010-persistance-sqlite.md) État en SQLite | Caduque | L'état d'une tâche vit dans sa carte Orca et dans `docs/plans/`. |
| [0011](0011-pratiques-et-metriques-dora.md) Pratiques et métriques DORA | Valable en partie | §1, les pratiques (petits lots, branches courtes), et les définitions restent. Caduc : le calcul et l'écran par jam (§2 à §5), remplacés par une seule mesure notée à la main, le temps du mainteneur par issue. L'exception « outillage du poste » du §1 disparaît : les hooks entrent dans le plugin. |
| [0012](0012-coordinateur-role-garde-fous-hook.md) Coordinateur rôle, garde par un hook | Valable, précisée | La garde devient un hook du plugin, versionné et testé. Une garde de sortie unique, distincte, couvre en plus commit, push, merge et écritures `gh` pour toute session. Caduc : « dans jam, c'est le cœur qui jouera ce rôle ». |
| [0013](0013-orchestration-deux-niveaux.md) Orchestration à deux niveaux | Valable, précisée | Les deux niveaux sont la méthode du niveau *standard*. Précisé : le plafond d'agents devient global au poste ; en *léger*, pas d'orchestrateur de tâche, le coordinateur tient la tâche, commit et PR compris ; le relais d'un feu vert est allégé pour le plan et la recette. Caduc : « Correspondance avec jam » et l'exception unique de `cadrage-orchestration`, close. |
| [0014](0014-lecture-clone-orca-implementeur.md) Clone de référence d'Orca pour l'implémenteur | Historique | Le kit ne reprend pas de code d'Orca. Elle redeviendrait applicable si une tâche en reprenait. |
| [0015](0015-remontee-carte-seule-coordinateur-flottant.md) Carte seule, terminal flottant | Valable en partie | La remontée par la carte seule tient. L'emplacement du coordinateur est remplacé par l'[ADR 0017](0017-coordinateur-main-poste-de-travail.md). Le format d'un feu vert relayé suit l'allègement ci-dessus. Caduc : « Correspondance avec jam ». |

À l'acceptation de cette ADR, le statut de chaque ADR du tableau mentionne son sort : « caduque (ADR 0016) », « historique (ADR 0016) », ou, pour une ADR valable en partie ou précisée, ce qui est caduc ou précisé. Leur texte ne change pas.

## Conséquences

- (+) Une seule référence de la méthode, versionnée : plus de dérive de copie, ni de hooks qui divergent d'un poste à l'autre.
- (+) Les garde-fous en code sont versionnés, testés en CI et réinstallables : la conséquence (−) de l'ADR 0012 « la garde vit sur un seul poste et n'est pas versionnée » est levée.
- (+) Un projet ne porte que ce qui lui est propre, sa fiche. Un projet à faible risque passe en *léger* : deux agents par tâche au lieu de quatre ou plus.
- (+) Le travail est borné : trois issues, puis gel.
- (−) Le principe « une méthode imposée plutôt qu'espérée » recule : l'ordre des étapes et les feux verts ne sont plus garantis par un cœur, seulement par l'orchestrateur de tâche, le coordinateur et ce que les hooks savent vérifier.
- (−) En *léger*, un seul relecteur, y compris pour du code, et pas de plan relu : une erreur de conception passe plus facilement. Le mainteneur le compense en montant d'un niveau.
- (−) En *léger*, le contexte du coordinateur porte le détail des tâches qu'il conduit, ce que l'ADR 0013 voulait éviter.
- (−) Un « ok » relayé pour le plan ou la recette n'est plus vérifiable par le mainteneur après coup.
- (−) Le gel laisse des frictions connues sans réponse (Q-060, Q-062) tant qu'aucun projet ne les revit.
- (−) Le kit dépend du format des plugins et des hooks de Claude Code, et de la CLI d'Orca, qu'il ne maîtrise pas.
- (−) L'objectif d'apprentissage du harness (boucle intérieure) est abandonné, et les métriques DORA ne sont plus calculées.
